# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import fields, osv
import ir
import pooler
import tools
import time
from tools import config
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import netsvc




class contracts_pest(osv.osv):
	_name = 'contracts.pest'
	_columns = {
		'name': fields.char('Name', size=46, ),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}

contracts_pest()

class contracts_areas(osv.osv):
	_name = 'contracts.areas'

	def search(self, cr, uid, args ,offset=0, limit=None, order=None,
			context={}, count=False):
		#print 'context',context
		keys = []
		for aa in args:
			keys.append(aa)
		if not 'parent_id' in keys:
			return super(contracts_areas,self).search(cr, uid, args, offset, limit,
				order, context=context, count=count)
		part_obj = self.pool.get('res.partner')
		part = args[0][2][0]
		partner= args[0][2]
		#print 'parent', partner
		while part_obj.browse(cr, uid, part).parent_id.id:
			#print 'partner=',part_obj.browse(cr, uid, part).parent_id.id
			partner.append(part_obj.browse(cr, uid, part).parent_id.id)
			part = part_obj.browse(cr, uid, part).parent_id.id
		area = super(contracts_areas,self).search(cr, uid, args, offset, limit,
				order, context=context, count=count)
		if not area:
			args = [('partner_id', 'in', [1])]
		return super(contracts_areas,self).search(cr, uid, args, offset, limit,
				order, context=context, count=count)

	_columns = {
		'name': fields.char('Name', size=46, ),
		'partner_id': fields.many2many('res.partner', 'partner_area_rel', 'area_id', 'partner_id', 'Partner'),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}

contracts_areas()

class contracts_route(osv.osv):
	_name = 'contracts.route'
	_columns = {
		'name': fields.char('Route', required=True, size=46, translate=True),
		'shortcut': fields.char('Shortcut', required=True, size=16),
		'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),
	}
	_defaults = {
	}
	_order = 'name'
contracts_route()

class contracts_technician(osv.osv):
	_name = 'contracts.technician'
	_columns = {
		'name': fields.char('Name', size=46, ),
		'employee_id' : fields.many2one('hr.employee', 'Employee', select=True),
		'route_id': fields.many2one('contracts.route', 'Route', ),
	}
	_defaults = {
	}
	def onchange_employee_id(self, cr, uid, ids, employee_id):
		if not employee_id:
			return {'value':{'name': False}}
		name = self.pool.get('hr.employee').browse(cr, uid, employee_id).name
		return {'value':{'name': name}}

contracts_technician()




class equipment_atribut(osv.osv):
	_name = 'equipment.atribut'
	_columns = {
		'name': fields.char('Name', size=64, ),
		'equipment_type_id': fields.many2many('equipment.type', 'equipment_atribut_rel', 'atribut_id','equipment_id', 'Equipment Type'),# readonly=True ),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}

equipment_atribut()



class equipment_type(osv.osv):
	_name = 'equipment.type'
	_columns = {
		'name': fields.char('Name', size=46, ),
		'equipment_atribut_id': fields.many2many('equipment.atribut',  'equipment_atribut_rel','equipment_id','atribut_id', 'Atribut'),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}

	def _partner_title_get(self, cr, uid, context={}):
		obj = self.pool.get('res.partner.title')
		ids = obj.search(cr, uid, [('domain', '=', 'partner')])
		res = obj.read(cr, uid, ids, ['shortcut','name'], context)
		return [(r['shortcut'], r['name']) for r in res]

	def _employee_get(obj,cr,uid,context={}):
		ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
		if ids:
			return ids[0]
		else:
			return False


equipment_type()







##def _partner_title_get(self, cr, uid, context={}):
##	obj = self.pool.get('res.partner.title')
##	ids = obj.search(cr, uid, [('domain', '=', 'partner')])
##	res = obj.read(cr, uid, ids, ['shortcut','name'], context)
##	return [(r['shortcut'], r['name']) for r in res]

##def _employee_get(obj,cr,uid,context={}):
##	ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
##	if ids:
##		return ids[0]
##	return False


##equipment_type()



class inspection_question(osv.osv):
	_name = 'inspection.question'
	_columns = {
		'name': fields.char('Name', size=256, ),
		}
	_defaults = {
	}

inspection_question()



class inspection_category(osv.osv):
	_name = 'inspection.category'
	_columns = {
		'name': fields.char('Name', size=46, ),
		'inspection_question_id': fields.many2many('inspection.question',  'inspection_category_rel','category_id','question_id', 'Question'),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}
inspection_category()


class inspection_survay(osv.osv):
	_name = 'inspection.survay'
	_columns = {
		'name': fields.char('Name', size=64, ),
		'inspection_category_id': fields.many2many('inspection.category',  'inspection_survay_rel','survay_id', 'category_id','Category'),
		'notes': fields.text('Notes'),
	}
	_defaults = {
	}
inspection_survay()





class contracts_order(osv.osv):
	_name = 'contracts.order'
	_description = 'Cotracts'

	def search(self, cr, uid, args, offset=0, limit=None, order=None,
			context={}, count=False):
		#print 'args =',args
		if not args:
			now = time.strftime('%Y-%m-%d')
			contracts = super(contracts_order,self).search(cr, uid, args, offset, limit,
				order, context=context)
			#print 'contracts=', contracts
			for contract in contracts:
				if self.browse(cr, uid, contract).date_stop < now and self.browse(cr, uid, contract).state == 'progress':
					#print 'expirado=',contract
					self.write(cr, uid, [contract], {'state':'expired'})
		return super(contracts_order,self).search(cr, uid, args, offset, limit,
				order, context=context, count=count)

	def _amount_initial(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		#print 'ids=', ids
		for sale in self.browse(cr, uid, ids):
			res[sale.id] = 0.0
			for line in sale.contract_services:
				if line.init:
					res[sale.id] += line.price_subtotal
			cur = sale.pricelist_id.currency_id
			res[sale.id] = cur_obj.round(cr, uid, cur, res[sale.id])
		return res

	def _amount_service(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for sale in self.browse(cr, uid, ids):
			res[sale.id] = 0.0
			for line in sale.contract_services:
				if not line.init:
					##print 'pricesubtotal',line.price_subtotal
					res[sale.id] += line.price_subtotal
			cur = sale.pricelist_id.currency_id
			res[sale.id] = cur_obj.round(cr, uid, cur, res[sale.id])
		return res

	def _amount_untaxed(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for sale in self.browse(cr, uid, ids):
			res[sale.id] = 0.0
			for line in sale.contract_services:
				if not line.init:
					res[sale.id] += line.price_subtotal
			cur = sale.pricelist_id.currency_id
			initial=self._amount_initial(cr, uid, ids, field_name, arg, context)[sale.id]
			res[sale.id]=res[sale.id]*sale.duration*eval(sale.periodicity)+initial
			res[sale.id] = cur_obj.round(cr, uid, cur, res[sale.id])
		return res

	def _amount_tax(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		tax_obj=self.pool.get('account.tax')
		for sale in self.browse(cr, uid, ids):
			res[sale.id] = 0.0
			for line in sale.contract_services:
				taxTotal=0.0
				for tt in line.tax_id:
					taxTotal+=tt.amount
				if line.init:
					res[sale.id] += line.price_subtotal*taxTotal
				else:
					res[sale.id] += line.price_subtotal*taxTotal*sale.duration*eval(sale.periodicity)
				
			cur = sale.pricelist_id.currency_id
			res[sale.id] = cur_obj.round(cr, uid, cur, res[sale.id])
		return res


	def _amount_total(self, cr, uid, ids, field_name, arg, context):
		res = {}
		untax = self._amount_untaxed(cr, uid, ids, field_name, arg, context) 
		tax = self._amount_tax(cr, uid, ids, field_name, arg, context)
		cur_obj=self.pool.get('res.currency')
		for id in ids:
			order=self.browse(cr, uid, [id])[0]
			cur=order.pricelist_id.currency_id
			res[id] = cur_obj.round(cr, uid, cur, untax.get(id, 0.0) + tax.get(id, 0.0))
		return res

	def _get_date_end(self, cr, uid, ids, field_name, arg, context={}):
		result = {}
		for cont in self.browse(cr, uid, ids, context={}):
			dt = cont.date_start
			print 'date start', dt
			if dt:
				ds = mx.DateTime.strptime(dt, '%Y-%m-%d')
				stop = ds + RelativeDateTime(months=(cont.duration * 1/eval(cont.periodicity)))
				result[cont.id]=(stop.strftime('%Y-%m-%d'))
				print 'date stop', result
		return 	result

	def _get_old_price(self, cr, uid, ids, field_name, arg, context={}):
		result = {}
		for cont in self.browse(cr, uid, ids, context={}):
			if cont.renew:
				result[cont.id] = cont.renew.amount_total
			else:
				result[cont.id] = 0.0
		return 	result

	def _get_renew_no(self, cr, uid, ids, field_name, arg, context={}):
		result = {}
		for cont in self.browse(cr, uid, ids, context={}):
			#print 'cont=',cont
			res = 0
			i = cont
			while i.renew:
				#print 'i.renew=',i.renew
				res += 1
				i = i.renew
				#print 'res=',res
			result[cont.id] = res
		return 	result

	
	def _get_determinante(self, cr, uid, ids, field_name, arg, context={}):
		result={}
		for cont in self.browse(cr, uid, ids, context={}):
			try:
				determinante = cont.partner_shipping_id.determinante
			except:
				determinante=''
			result[cont.id] = determinante
		return result

	def total_equipments(self,cr, uid, ids ):
		#print ' a ver que tan chichon'
		return 'ddddd'
#####
	def _partner_title_get(self, cr, uid, context={}):
		obj = self.pool.get('res.partner.title')
		ids = obj.search(cr, uid, [('domain', '=', 'partner')])
		res = obj.read(cr, uid, ids, ['shortcut','name'], context)
		return [(r['shortcut'], r['name']) for r in res]

	def _employee_get(obj,cr,uid,context={}):
		ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
		if ids:
			return ids[0]
		else:
			return False
#####
	
	_columns = {
		'shop_id':fields.many2one('sale.shop', 'Shop', required=True, ),
		'technician_id' : fields.many2one('contracts.technician', 'Technician', select=True,  states={'initial':[('required',True)]}),
		'type': fields.selection([('type01','Type 01'),('type02','Type 02')], 'Contract Type', ),
		'format': fields.selection([('format01','Format 01'),('format02','Format 02')], 'Format' ),
		'schedule': fields.selection([('schedule01','Schedule 01'),('schedule02','Schedule 02')], 'Schedule' ),
		'survay_id':fields.many2one('inspection.survay', 'Survay', required=True, select=True),
		'format': fields.selection([
			('aves','Aves'),
			('residencial','Residencial'),
			('comercial','Comercial'),
			('inspeccion','Inspeccion de Calidad')], 'Format' ),
		'partner_id':fields.many2one('res.partner', 'Partner', change_default=True, required=True, select=True),
		'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address', required=True,),
		'partner_order_id':fields.many2one('res.partner.address', 'Contract Contact', help="The name and address of the contact that requested the order or quotation."),
		'partner_shipping_id':fields.many2one('res.partner.address', 'Service Address', ),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True,),
		'contract_services': fields.one2many('contracts.order.services', 'order_id', 'Services', readonly=False),
		'determinante': fields.function(_get_determinante, method=True, type='char', string='Determinante'),
		'date_order':fields.date('Date Ordered', required=True, ),
		'user_id':fields.many2one('hr.employee', 'Salesman', select=True),
		'currency_id': fields.many2one('res.currency', 'Currency', help=" "),
		'layout': fields.char('Layout', size=64,),
		'business_type': fields.selection(_partner_title_get, 'Business Type', size=32),
		'route_id': fields.many2one('contracts.route', 'Route',states={'initial':[('required',True)]} ),
		'name': fields.char('name', size=64,),
		'state': fields.selection([
			('draft','Draft'),
			('initial','Initialization'),
			('progress','In progress'),
			('expired','Expired'),
			('cancel','Cancel'),
			('renewed','Renewed')
			], 'Contract State', readonly=True, help="Gives the state of the contract. The exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the packing list process (Shipping Exception). The 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to be on the date 'Date Ordered'.", select=True),
		'zone': fields.char('Zone', size=64,),
		'amount_initial': fields.function(_amount_initial, method=True, string='Initial Service'),
		'amount_service': fields.function(_amount_service, method=True, string='Regular Service'),
		'amount_untaxed': fields.function(_amount_untaxed, method=True, string='Untaxed Amount'),
		'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
		'amount_total': fields.function(_amount_total, method=True, string='Total'),
		'duration': fields.integer('Duration'),
		'periodicity': fields.selection([
			('4','Weekly'),
			('1','Monthly'),
			('6/12.0','Two-monthds'),
			('4/12.0','Quarterly'),
			('2/12.0','Half-yearly'),
			('1/12','yearly'),
			], 'Periodicity', help=""),
		'hour': fields.selection([
			('08','08 A.M.'),('09','09 A.M.'),('10','10 A.M.'),('11','11 A.M.'),
			('12','12 P.M.'),('13','01 P.M.'),('14','02 P.M.'),('15','03 P.M.'),
			('16','04 P.M.'),('17','05 P.M.'),('18','06 P.M.'),('19','07 P.M.'),
			('20','08 P.M.'),('21','09 P.M.'),('22','10 P.M.'),('23','11 P.M.'),
			('24','12 P.M.'),('01','01 A.M.'),('02','02 A.M.'),('03','03 A.M.'),
			('04','04 A.M.'),('05','05 A.M.'),('06','06 A.M.'),('07','07 A.M.'),
			], 'Hour', help=""),
		'minutes': fields.selection([
			('00','00'),('15','15'),('30','30'),('45','45'),
			], 'Minutes', help=""),
		'week': fields.selection([
			('none','None'),('first_week','First '),('second_week','Second'),('third_week','Third'),('forth_week','Fourth'),('fith_week','Fifth'),
			], 'Week', help=""),
		'day': fields.selection([
			('none','None'),('SUNDAY','Sunday'),('MONDAY','Monday'),('TUESDAY','Tuesday'),('WEDNESDAY','Wednesday'),('THURSDAY','Thursday'),('FRIDAY','Friday'),('SATURDAY','Saturday'),
			], 'Day', help=""),
		'serv_len': fields.char('Serv. Length', size=16,),
		'renew_no': fields.function(_get_renew_no, method=True, type='float', string='Renew Count'),
		'date_start':fields.date('Date Start'),
		'date_stop': fields.function(_get_date_end, method=True, type='date', string='Date End'),
		'renew': fields.many2one('contracts.order', 'Renew', ),
		'old_price': fields.function(_get_old_price, method=True, type='float', string='Old Price'),
		'date_inc':fields.date('Date inc.'),
		'service_order': fields.one2many('service.order', 'contract_id', 'Service Orders'),
		'contracts_equipment': fields.one2many('contracts.equipment', 'contract_id', 'Contract Equipment', readonly=False),
		'order_recomendation': fields.one2many('service.order.recomendation', 'order_id', 'Activity Lines', readonly=False),
		'instructions': fields.text('Instructions'),
		'comments': fields.text('Comments'),
		'area_id': fields.many2many('contracts.areas', 'contracts_areas_rel', 'contract_id', 'area_id', 'Area'),
		'pest': fields.many2many('contracts.pest', 'contracts_pest_rel', 'contract_id', 'pest_id', 'Area'),
		'rep_equipment': fields.boolean('Reports Equipment'),
		'rep_survay': fields.boolean('Reports Survay'),
	}

	_defaults = {
		'date_order': lambda *a: time.strftime('%Y-%m-%d'),
		'date_start': lambda *a: time.strftime('%Y-%m-%d'),
		'user_id': _employee_get,
		'state': lambda *a: 'draft',
		'week': lambda *a: 'none',
		'day': lambda *a: 'none',
		'duration': lambda *a: 12,
		'hour': lambda *a: 12,
		'minutes': lambda *a: 0,
		'periodicity': lambda *a: '1',
		'survay_id': lambda *a: '1',
	}
	_order = 'date_order desc'

	def button_cancel(self, cr, uid, ids, context={}):
		cont_id = ids[0]
		self.write(cr, uid, [cont_id], {'state':'cancel'})
		service_ids=self.pool.get('service.order').search(cr,uid,[('contract_id','=',cont_id),('state','=','in_progress')])
		cancel_ids=self.pool.get('service.order').write(cr,uid,service_ids,{'state':'cancel'})
		return True

	def button_confirm(self, cr, uid, ids, context={}):
		id = ids[0]
		if self.pool.get('contracts.order.services').search(cr,uid,[('order_id','=',ids[0]),('init','=',True)]):
			self.write(cr, uid, [id], {'state':'initial'})
		else:
			self.write(cr, uid, [id], {'state':'progress'})
		return True

	def button_draft(self, cr, uid, ids, context={}):
		id = ids[0]
		self.write(cr, uid, [id], {'state':'draft'})
		return True
	
	def button_initial_service(self, cr, uid, ids, context={}):
		cont_id = ids[0]
		self.write(cr, uid, cont_id, {'state':'progress'})
		print ' button_scheduler'
		order_id=self.browse(cr,uid,cont_id)
		service_ids=self.pool.get('contracts.order.services').search(cr,uid,[('order_id','=',cont_id),('init','=',True)])
		service_records=self.pool.get('contracts.order.services').browse(cr,uid,service_ids,context)
		obj_service = self.pool.get('service.order')
		service_dir=self._service_order_dir(cr,uid,self.browse(cr,uid,cont_id))
		print 'service dir', service_dir
		serv_id=obj_service.create(cr, uid, service_dir)
		serv_lines_id=self._create_service_line(cr,uid,service_records,serv_id,cont_id)
		


	def _create_service_line(self,cr,uid, browse_records, serv_id,cont_id=0):
		obj_service_line = self.pool.get('service.order.line')
		service_line_dir = {}
		ids = []
		for line in browse_records:
			print 'line',line
			service_line_dir['product_uom']=line.product_uom.id
			service_line_dir['order_id'] = serv_id
			service_line_dir['name']=line.name
			service_line_dir['product_uos_qty']=line.product_uos_qty
			service_line_dir['product_id']=line.product_id.id
			service_line_dir['order_id']=serv_id
			service_line_dir['price_unit']=line.price_unit
			service_line_dir['tax_id']=[(6,0,[x.id for x in line.tax_id])]
			ids += [obj_service_line.create(cr, uid, service_line_dir),]
		return ids


		
	def _service_order_dir(self,cr,uid,contract):
		res={}
		res['init']=True
		res['name']=self.pool.get('ir.sequence').get(cr,uid,'service.order')
		res['date_order']=contract.date_inc
		res['contract_id']= contract.id
		res['pricelist_id']=contract.pricelist_id.id
		res['partner_id']=contract.partner_id.id
		res['partner_shipping_id']=contract.partner_shipping_id.id
		res['partner_order_id']=contract.partner_order_id.id
		res['state']= 'in_progress'
		res['shop_id']=contract.shop_id.id
		res['partner_invoice_id']=contract.partner_invoice_id.id
		res['technician_id']=contract.technician_id.id
		res['route_id']=contract.route_id.id
		res['instructions']=contract.instructions
		res['comments']=contract.comments
		res['rep_equipment']=contract.rep_equipment
		res['rep_survay']=contract.rep_survay
		res['area_id']=[(6,0,[x.id for x in contract.area_id])]
		res['pest_id']=[(6,0,[x.id for x in contract.pest])]
		return res


	def onchange_partner_id(self, cr, uid, ids, part):
		if not part:
			return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False, 'pricelist_id': False, 'business_type': False, 'currency_id': False}}
		addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
		pricelist = self.pool.get('res.partner').browse(cr, uid, part).property_product_pricelist.id
		currency = self.pool.get('product.pricelist').browse(cr, uid, pricelist).currency_id.id
		title = self.pool.get('res.partner').browse(cr, uid, part).title
		return {'value':{'partner_invoice_id': addr['invoice'], 'partner_order_id':addr['contact'], 'partner_shipping_id':addr['delivery'], 'pricelist_id': pricelist, 'business_type': title, 'currency_id': currency}}



	def onchange_route_id(self, cr, uid, ids, shop_id):
		#print 'onchange_shop_id'
		if not shop_id:
			return {'value':{}}
		obj = self.pool.get('contracts.route')
		ids = obj.search(cr, uid, [('shop_id', '=', shop_id)])
		res = obj.read(cr, uid, ids, ['shortcut','name'], )
		res = [(r['shortcut'], r['name']) for r in res]
		#print 'res=',res
		return {'value':{'route':res}}

		addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
		pricelist = self.pool.get('res.partner').browse(cr, uid, part).property_product_pricelist.id
		currency = self.pool.get('product.pricelist').browse(cr, uid, pricelist).currency_id.id
		title = self.pool.get('res.partner').browse(cr, uid, part).title
		return {'value':{'partner_invoice_id': addr['invoice'], 'partner_order_id':addr['contact'], 'partner_shipping_id':addr['delivery'], 'pricelist_id': pricelist, 'business_type': title, 'currency_id': currency}}


	def onchange_area(self, cr, uid, ids, area):
		product_obj = self.pool.get('product.product')
		if not product_id:
			return {'value': {'product_uom': product_uos,
				'product_uom_qty': product_uos_qty}, 'domain':{}}

		product = product_obj.browse(cr, uid, product_id)
		value = {
			'product_uom' : product.uom_id.id,
		}
		# FIXME must depend on uos/uom of the product and not only of the coeff.
		try:
			value.update({
				'product_uom_qty' : product_uos_qty / product.uos_coeff,
				'th_weight' : product_uos_qty / product.uos_coeff * product.weight
			})
		except ZeroDivisionError:
			pass
		return {'value' : value}

	def onchange_date_start(self, cr, uid, ids, date_start, duration):
		for cont in self.browse(cr, uid, ids, context={}):
			dt = cont.date_start
			ds = mx.DateTime.strptime(dt, '%Y-%m-%d')
			stop = ds + RelativeDateTime(months=duration)
		value = {
			'date_stop' : stop.strftime('%Y-%m-%d'),
		}
		return {'value' : value}

	def button_dummy(self, cr, uid, ids, context={}):
		return True

	def button_scheduler(self, cr, uid, ids, context={}, month=1):
		print ' button_scheduler but'
		obj_service = self.pool.get('service.order')
		for id in ids:
			elements = obj_service.search(cr, uid, [('contract_id','=',id)])
			if elements:
				for element in elements:
					obj_service.unlink(cr, uid, [element])
#		self.write(cr, uid, ids, {'state':'cleared',})
		for cont in self.browse(cr, uid, ids, context):
			dt = cont.date_start
			ds = mx.DateTime.strptime(dt, '%Y-%m-%d')
			ds = ds + RelativeDateTime(hours=int(cont.hour), minutes=int(cont.minutes))
			if cont.periodicity != 'week':
				month = 1/eval(cont.periodicity)
				day = 0
				#print 'month=',month
			else:
				month = 0
				day = 7
			#print 'partner =', cont.partner_id.id
			#print 'pricelist=', cont.pricelist_id.id
			while ds.strftime('%Y-%m-%d') < cont.date_stop:
				service_dir = self._service_order_dir(cr, uid, cont)
				#print 'serivce dir', service_dir
				service_dir.update({'date_order':ds,})
				service_id = self.pool.get('service.order').create(cr, uid, service_dir)
				line_ids = self._create_service_line(cr, uid, cont.contract_services, service_id, cont.id)
##								      {
##					'name': self.pool.get('ir.sequence').get(cr, uid, 'service.order'),
##					'date_order': ds,
##					'contract_id': cont.id,
##					'state': 'draft',
##					'pricelist_id': cont.pricelist_id.id,
##					'partner_id': cont.partner_id.id,
##					'shop_id': cont.shop_id.id,
##					'partner_inoice_id':cont.partner_inoice_id.id,
##					'partner_order_id':cont.partner_order_id.id,
##					'partner_shipping_id':cont.partner_shipping_id.id,
					
##				})
##								      {
				print 'variables*************'
				print 'months=',month
				print 'days', day
				print 'asi empieza ds=', ds
				de = ds + RelativeDateTime(months=month, days=-1)
				print 'de = ', de
				ds = ds + RelativeDateTime(months=month, days=day)
				print 'ds', ds
		return True

contracts_order()

#
#	Scheduled Services Order
#

class contracts_service_order(osv.osv):
	_name = 'service.order'

	def _amount_untaxed(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for sale in self.browse(cr, uid, ids):
			res[sale.id] = 0.0
			for line in sale.order_line:
				res[sale.id] += line.price_subtotal
			cur = sale.pricelist_id.currency_id
			res[sale.id] = cur_obj.round(cr, uid, cur, res[sale.id])
		return res

	def _amount_tax(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids):
			val = 0.0
			cur=order.pricelist_id.currency_id
			for line in order.order_line:
				for c in self.pool.get('account.tax').compute(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, order.partner_invoice_id.id, line.product_id, order.partner_id):
					val+= cur_obj.round(cr, uid, cur, c['amount'])
			res[order.id]=cur_obj.round(cr, uid, cur, val)
		return res

	def _amount_total(self, cr, uid, ids, field_name, arg, context):
		res = {}
		untax = self._amount_untaxed(cr, uid, ids, field_name, arg, context) 
		tax = self._amount_tax(cr, uid, ids, field_name, arg, context)
		cur_obj=self.pool.get('res.currency')
		for id in ids:
			order=self.browse(cr, uid, [id])[0]
			cur=order.pricelist_id.currency_id
			res[id] = cur_obj.round(cr, uid, cur, untax.get(id, 0.0) + tax.get(id, 0.0))
		return res

	def _invoiced(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for sale in self.browse(cursor, user, ids, context=context):
			res[sale.id] = True
			for invoice in sale.invoice_ids:
				if invoice.state <> 'paid':
					res[sale.id] = False
					break
			if not sale.invoice_ids:
				res[sale.id] = False
		return res

	def _invoiced_search(self, cursor, user, obj, name, args):
		if not len(args):
			return []

		clause = ''
		no_invoiced = False
		for arg in args:
			if arg[1] == '=':
				if arg[2]:
					clause += 'AND inv.state = \'paid\''
				else:
					clause += 'AND inv.state <> \'paid\''
					no_invoiced = True

		cursor.execute('SELECT rel.order_id ' \
				'FROM sale_order_invoice_rel AS rel, account_invoice AS inv ' \
				'WHERE rel.invoice_id = inv.id ' + clause)
		res = cursor.fetchall()
		if no_invoiced:
			cursor.execute('SELECT sale.id ' \
					'FROM sale_order AS sale ' \
					'WHERE sale.id NOT IN ' \
						'(SELECT rel.order_id ' \
						'FROM sale_order_invoice_rel AS rel)')
			res.extend(cursor.fetchall())
		if not res:
			return [('id', '=', 0)]
		return [('id', 'in', [x[0] for x in res])]



	def _service_order_dir(self,cr,uid,service_order):
		res={}
		res['init']=service_order.init
		res['name']=self.pool.get('ir.sequence').get(cr,uid,'service.order')
		res['date_order']=service_order.date_order
		res['contract_id']= service_order.contract_id.id
		res['pricelist_id']=service_order.pricelist_id.id
		res['partner_id']=service_order.partner_id.id
		res['partner_shipping_id']=service_order.partner_shipping_id.id
		res['partner_order_id']=service_order.partner_order_id.id
		res['state']= 'draft'
		res['shop_id']=service_order.shop_id.id
		res['partner_invoice_id']=service_order.partner_invoice_id.id
		res['technician_id']=service_order.technician_id.id
		res['route_id']=service_order.route_id.id
		res['rep_equipment']=service_order.rep_equipment
		res['rep_survay']=service_order.rep_survay
		res['instructions']=service_order.instructions
		res['comments']=service_order.comments
		res['area_id']=[(6,0,[x.id for x in service_order.area_id])]
		res['pest_id']=[(6,0,[x.id for x in service_order.pest_id])]
		res['client_order_ref']=service_order.client_order_ref
		res['renew']=service_order.id
		return res

	def _create_service_line(self,cr,uid,browse_records,serv_id):
		obj_service_line=self.pool.get('service.order.line')
		service_line_dir={}
		ids=[]
		for line in browse_records:
			print 'line',line
			service_line_dir['product_uom']=line.product_uom.id
			service_line_dir['name']=line.name
			service_line_dir['product_uos_qty']=line.product_uos_qty
			service_line_dir['product_id']=line.product_id.id
			service_line_dir['order_id']=serv_id
			service_line_dir['price_unit']=line.price_unit
			service_line_dir['tax_id']=[(6,0,[x.id for x in line.tax_id])]
			ids+=[ obj_service_line.create(cr, uid, service_line_dir),]
		return ids

	_columns = {
		'contract_id': fields.many2one('contracts.order', 'Cotract', required=True, ondelete='cascade', select=True),
		'name': fields.char('Order Number', size=46, ),
		'init': fields.boolean('Initial'),
		'date_order':fields.datetime('Date/Time Order', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'date_done':fields.datetime('Date/Time Done', required=False, readonly=True, states={'in_progress':[('readonly',False)],'eq_checked':[('readonly',False)],'survay_done':[('readonly',False)],'done':[('required',True)]}),
		'date_start':fields.datetime('Date/Time Start', required=False, readonly=True, states={'in_progress':[('readonly',False)],'eq_checked':[('readonly',False)],'survay_done':[('readonly',False)],'done':[('required',True)]}),
		'done': fields.boolean('Done'),
		'state': fields.selection([
		('draft','Draft'),
		('in_progress','In Progress'),
		('eq_checked','Equipments Checked'),
		('survay_done','Survay Done'),
		('re_schedule','Re Scheduel'),
		('droped','Droped'),
		('invoiced','Invoiced'),
		('done','Done'),
		('cancel','Cancel')
		], 'Order State', readonly=True,  select=True),
		'order_line': fields.one2many('service.order.line', 'order_id', 'Order Lines', readonly=False, states={'done':[('readonly',True)]}),
		'order_aplication': fields.one2many('service.order.aplication', 'order_id', 'Aplication Lines', readonly=False),
		'order_activity': fields.one2many('service.order.activity', 'order_id', 'Activity Lines', readonly=False),
		
		'order_survay': fields.one2many('service.order.survay', 'order_id', 'Activity Lines', readonly=False),
		'order_equipment': fields.one2many('service.order.equipment', 'order_id', 'Equipment', readonly=False),

		'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'origin': fields.char('Origin', size=64),
		'client_order_ref': fields.char('Partner Ref.',size=64),
		'user_id':fields.many2one('res.users', 'Salesman', states={'draft':[('readonly',False)]}, select=True),
		'partner_id':fields.many2one('res.partner', 'Partner', readonly=True, states={'draft':[('readonly',False)]}, change_default=True, select=True),
		'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
		'partner_order_id':fields.many2one('res.partner.address', 'Ordering Contact', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="The name and address of the contact that requested the order or quotation."),
		'partner_shipping_id':fields.many2one('res.partner.address', 'Shipping Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
		'picking_policy': fields.selection([('direct','Direct Delivery'),('one','All at once')], 'Packing Policy', required=True ),
		'order_policy': fields.selection([
			('prepaid','Payment before delivery'),
			('manual','Shipping & Manual Invoice'),
			('postpaid','Automatic Invoice after delivery'),
			('picking','Invoice from the packings'),
		], 'Shipping Policy', required=True, readonly=True, states={'draft':[('readonly',False)]},
					help="""The Shipping Policy is used to synchronise invoice and delivery operations.
  - The 'Pay before delivery' choice will first generate the invoice and then generate the packing order after the payment of this invoice.
  - The 'Shipping & Manual Invoice' will create the packing order directly and wait for the user to manually click on the 'Invoice' button to generate the draft invoice.
  - The 'Invoice after delivery' choice will generate the draft invoice after the packing list have been finished.
  - The 'Invoice from the packings' choice is used to create an invoice during the packing process."""),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'project_id':fields.many2one('account.analytic.account', 'Analytic account', readonly=True, states={'draft':[('readonly', False)]}),

		'invoice_ids': fields.many2many('account.invoice', 'contracts_order_services_invoice_rel', 'contracts_order_services', 'invoice_id', 'Invoice', help="This is the list of invoices that have been generated for this sale order. The same sale order may have been invoiced in several times (by line for example)."),
		'picking_ids': fields.one2many('stock.picking', 'sale_id', 'Packing List', readonly=True, help="This is the list of picking list that have been generated for this invoice"),
		'shipped':fields.boolean('Picked', readonly=True),
		'invoiced': fields.function(_invoiced, method=True, string='Paid',
			fnct_search=_invoiced_search, type='boolean'),
		'note': fields.text('Notes'),
		'amount_untaxed': fields.function(_amount_untaxed, method=True, string='Untaxed Amount'),
		'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
		'amount_total': fields.function(_amount_total, method=True, string='Total'),
		'invoice_quantity': fields.selection([('order','Ordered Quantities'),('procurement','Shipped Quantities')], 'Invoice on', help="The sale order will automatically create the invoice proposition (draft invoice). Ordered and delivered quantities may not be the same. You have to choose if you invoice based on ordered or shipped quantities. If the product is a service, shipped quantities means hours spent on the associated tasks."),
		'technician_id' : fields.many2one('contracts.technician', 'Technician', select=True),
		'route_id': fields.many2one('contracts.route', 'Route', ),
		'equipment_list':fields.boolean('Equipment List Created',readonly=True),
		'survay_list':fields.boolean('Survay List Created',readonly=True),
		'area_id':  fields.many2many('contracts.areas','service_order_areas_rel','service_order_id','area_id','Area',readonly=True),
		
		'pest_id':fields.many2many('contracts.pest','service_order_pest_rel','service_order_id','pest_id','Pest',readonly=True),
		'instructions': fields.text('Instructions'),
		'comments': fields.text('Comments'),
		'rep_equipment': fields.boolean('Reports Equipment'),
		'rep_survay': fields.boolean('Reports Survay'),
		'renew': fields.many2one('service.order', 'Renew', ),
		
		
	}
	_defaults = {
		'picking_policy': lambda *a: 'direct',
		'date_order': lambda *a: time.strftime('%Y-%m-%d'),
		'order_policy': lambda *a: 'manual',
		'state': lambda *a: 'in_progress',
		'user_id': lambda obj, cr, uid, context: uid,
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'sale.order'),
		'invoice_quantity': lambda *a: 'order',
		'partner_invoice_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['invoice'])['invoice'],
		'partner_order_id': lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['contact'])['contact'],
		'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['delivery'],
		'pricelist_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').browse(cr, uid, context['partner_id']).property_product_pricelist.id,
	}
	_order = 'name desc'

	def _inv_get(self, cr, uid, order, context={}):
		return {}

	def _make_invoice(self, cr, uid, order, lines):
		a = order.partner_id.property_account_receivable.id
		if order.partner_id and order.partner_id.property_payment_term.id:
			pay_term = order.partner_id.property_payment_term.id
		else:
			pay_term = False
		for preinv in order.invoice_ids:
			if preinv.state in ('open','paid','proforma'):
				for preline in preinv.invoice_line:
					inv_line_id = self.pool.get('account.invoice.line').copy(cr, uid, preline.id, {'invoice_id':False, 'price_unit':-preline.price_unit})
					lines.append(inv_line_id)
		inv = {
			'name': order.client_order_ref or order.name,
			'origin': order.name,
			'type': 'out_invoice',
			'reference': "P%dSO%d"%(order.partner_id.id,order.id),
			'account_id': a,
			'partner_id': order.partner_id.id,
			'address_invoice_id': order.partner_invoice_id.id,
			'address_contact_id': order.partner_invoice_id.id,
			'invoice_line': [(6,0,lines)],
			'currency_id' : order.pricelist_id.currency_id.id,
			'comment': order.note,
			'payment_term': pay_term,
		}
		inv.update(self._inv_get(cr, uid, order))
		inv_obj = self.pool.get('account.invoice')
		inv_id = inv_obj.create(cr, uid, inv)
		inv_obj.button_compute(cr, uid, [inv_id])
		return inv_id

	def action_invoice_create(self, cr, uid, ids, grouped=False, context={}, states=['in_progress','done']):
		print 'empieza',ids, grouped, states
		res = False
		invoices = {}
		invoice_ids = []

		for o in self.browse(cr,uid,ids):
			lines = []
			for line in o.order_line:
				print 'la linea,',line.state, line.invoiced
				if (line.state in states) and not line.invoiced:
					lines.append(line.id)
					print 'el id de las lineas ',lines
			created_lines = self.pool.get('service.order.line').invoice_line_create(cr, uid, lines)
			print 'a ver como va created lines', created_lines
			if created_lines:
				invoices.setdefault(o.partner_id.id, []).append((o, created_lines))

		if not invoices:
			for o in self.browse(cr, uid, ids):
				for i in o.invoice_ids:
					if i.state == 'draft':
						return i.id

		for val in invoices.values():
			if grouped:
				res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x,y: x + y, [l for o,l in val], []))
				for o,l in val:
					self.write(cr, uid, [o.id], {'state' : 'invoiced'})
					cr.execute('insert into  contracts_order_services_invoice_rel (contracts_order_services,invoice_id) values (%d,%d)', (o.id, res))
			else:
				for order, il in val:
					res = self._make_invoice(cr, uid, order, il)
					invoice_ids.append(res)
					self.write(cr, uid, [order.id], {'state' : 'invoiced'})
					cr.execute('insert into contracts_order_services_invoice_rel (contracts_order_services,invoice_id) values (%d,%d)', (order.id, res))
		return res




	def button_create_equipments(self, cr, uid, ids, context={}):
		obj_order_equipment=self.pool.get('service.order.equipment')
		equipment = self.pool.get('service.order').browse(cr, uid, ids[0]).contract_id.contracts_equipment
		for ee in equipment:
			if ee.state=='active':
				equipment_id=obj_order_equipment.create(cr,uid,{'order_id':ids[0],'name':ee.id,'barcode':ee.barcode,'area_id':ee.area_id.id, 'equipment_type_id':ee.equipment_type_id.id})
				
				query='select atribut_id from equipment_atribut_rel where equipment_id =%s'%(ee.equipment_type_id.id)
				cr.execute(query)
				atributs_ids=cr.fetchall()
				atributs=[]
				for i in atributs_ids:
					atributs.append(i[0])
				obj_atributs=self.pool.get('equipment.atribut').browse(cr,uid,atributs)
				for aa in obj_atributs:
					self.pool.get('service.order.equipment.inspection').create(cr,uid,{'name':equipment_id,'equipment_atribut_id':aa.id})
		self.write(cr,uid,ids,{'state':'eq_checked'})
								      
		return True

	def button_make_questions(self, cr, uid, ids, context={}):
		obj_order_survay=self.pool.get('service.order.survay')
		obj_survay_inspection=self.pool.get('service.order.survay.inspection')
		survay_id = self.pool.get('service.order').browse(cr, uid, ids[0]).contract_id.survay_id.id
		query='select category_id from inspection_survay_rel where survay_id=%s'%(survay_id)
		cr.execute(query)
		category_ids=cr.fetchall()
		for cc in category_ids:
			cc=cc[0]
			new_category=obj_order_survay.create(cr,uid,{'order_id':ids[0],'name':cc})
			query='select question_id from inspection_category_rel where category_id=%s'%(cc)
			cr.execute(query)
			question_ids=cr.fetchall()
			for qq in question_ids:
				qq=qq[0]
				obj_survay_inspection.create(cr,uid,{'name':new_category,'inspection_question_id':qq})
       			
 		self.write(cr,uid,ids,{'state':'survay_done'})
		return True

	def button_confirm(self, cr, uid, ids, context={}):
		self.write(cr, uid, ids, {'state':'in_progress'})
		return True

	def button_done(self, cr, uid, ids, context={}):
		print 'button done'
		bb=self.browse(cr,uid,ids[0])
		ee=False
		ss=False
		if bb.rep_equipment:
			has_equipment=self.pool.get('service.order.equipment').search(cr,uid,[('order_id','=',ids[0]),])
			if has_equipment:
				ee=True
		else:
			ee=True
		if bb.rep_survay:
			has_survay=self.pool.get('service.order.survay').search(cr,uid,[('order_id','=',ids[0]),])
			if has_survay:
				ss=True
		else:
			ss=True
		if ee and ss and bb.date_done:
			service_ids=self.pool.get('service.order.line').search(cr,uid,[('order_id','=',ids[0]),])
			self.pool.get('service.order.line').write(cr,uid,service_ids,{'state':'done'})
			self.write(cr, uid, ids, {'state':'done'})
			return True
		else:
			return False
		
		

	def button_reschedule(self, cr, uid, ids, context={}):
		service_ids = self.pool.get('service.order.line').search(cr,uid,[('order_id','=',ids[0]),])
		service_records = self.pool.get('service.order.line').browse(cr,uid,service_ids,context)
		dd = self._service_order_dir(cr,uid,self.browse(cr,uid,ids[0]))
		serv_id = self.create(cr, uid,dd)
		print 'service_records', service_records
		self._create_service_line(cr,uid, service_records, serv_id)
		self.write(cr, uid, ids, {'state':'re_schedule'})
		#print 'el nuevo serv_id',serv_id
		return serv_id

	def button_drop(self, cr, uid, ids, context={}):
		self.write(cr, uid, ids, {'state':'droped'})
		return True


	def button_create_invoice(self, cr, uid, ids, context={}):
		self.write(cr, uid, ids, {'state':'invoiced'})
		return True

	
	

contracts_service_order()

#
#	Scheduled Services Order Lines
#

class contracts_service_order_line(osv.osv):
	def copy(self, cr, uid, id, default=None, context={}):
		if not default: default = {}
		default.update( {'invoice_lines':[]})
		return super(contracts_service_order_line, self).copy(cr, uid, id, default, context)

	def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			res[line.id] = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		return res

	def _amount_line(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			res[line.id] = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	def _number_packages(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			try:
				res[line.id] = int(line.product_uom_qty / line.product_packaging.qty)
			except:
				res[line.id] = 1
		return res
	
	def _get_1st_packaging(self, cr, uid, context={}):
		cr.execute('select id from product_packaging order by id asc limit 1')
		res = cr.fetchone()
		if not res:
			return False
		return res[0]

	_name = 'service.order.line'
	_columns = {
		'order_id': fields.many2one('service.order', 'Service Order', required=True, ondelete='cascade', select=True),
		'name': fields.char('Description', size=256, required=True, select=True),
		'sequence': fields.integer('Sequence'),
		'delay': fields.float('Delivery Delay', required=True),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
		'invoice_lines': fields.many2many('account.invoice.line', 'contracts_service_order_line_invoice_rel', 'service_order_line_id','invoice_id', 'Invoice Lines', readonly=True),
		'invoiced': fields.boolean('Invoiced', readonly=True),
		'procurement_id': fields.many2one('mrp.procurement', 'Procurement'),
		'price_unit': fields.float('Unit Price', required=True, digits=(16, int(config['price_accuracy']))),
		'price_net': fields.function(_amount_line_net, method=True, string='Net Price', digits=(16, int(config['price_accuracy']))),
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
		'tax_id': fields.many2many('account.tax', 'service_order_tax_rel', 'order_line_id', 'tax_id', 'Taxes'),
		'type': fields.selection([('make_to_stock','from stock'),('make_to_order','on order')],'Procure Method', required=True),
		'property_ids': fields.many2many('mrp.property', 'sale_order_line_property_rel', 'order_id', 'property_id', 'Properties'),
		'address_allotment_id' : fields.many2one('res.partner.address', 'Allotment Partner'),
		'product_uom_qty': fields.float('Quantity (UOM)', digits=(16,2), required=True),
		'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
		'product_uos_qty': fields.float('Quantity (UOS)'),
		'product_uos': fields.many2one('product.uom', 'Product UOS'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging used'),
		'move_ids': fields.one2many('stock.move', 'sale_line_id', 'Inventory Moves', readonly=True),
		'discount': fields.float('Discount (%)', digits=(16,2)),
		'number_packages': fields.function(_number_packages, method=True, type='integer', string='Number packages'),
		'notes': fields.text('Notes'),
		'th_weight' : fields.float('Weight'),
		'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Canceled'),('invoiced','Invoiced')], 'State', required=True, readonly=True),
		
	}
	_order = 'sequence, id'
	_defaults = {
		'discount': lambda *a: 0.0,
		'delay': lambda *a: 0.0,
		'product_uom_qty': lambda *a: 1,
		'product_uos_qty': lambda *a: 1,
		'sequence': lambda *a: 10,
		'invoiced': lambda *a: 0,
		'state': lambda *a: 'draft',
		'type': lambda *a: 'make_to_stock',
		'product_packaging': _get_1st_packaging,

	}



	def invoice_line_create(self, cr, uid, ids, context={}):
		def _get_line_qty(line):
			if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
				if line.product_uos:
					return line.product_uos_qty or 0.0
				return line.product_uom_qty
			else:
				return self.pool.get('mrp.procurement').quantity_get(cr, uid,
						line.procurement_id.id, context)

		def _get_line_uom(line):
			if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
				if line.product_uos:
					return line.product_uos.id
				return line.product_uom.id
			else:
				return self.pool.get('mrp.procurement').uom_get(cr, uid,
						line.procurement_id.id, context)

		create_ids = []
		for line in self.browse(cr, uid, ids, context):
			if not line.invoiced:
				if line.product_id:
					a =  line.product_id.product_tmpl_id.property_account_income.id
					if not a:
						cc=line.product_id.product_tmpl_id.categ_id
						a=cc[0].property_account_income_categ.id
						#a = line.product_id.product_tmpl_id.property_account_income_categ.id
					if not a:
						raise osv.except_osv('Error !',
								'There is no income account defined ' \
										'for this product: "%s" (id:%d)' % \
										(line.product_id.name, line.product_id.id,))
				else:
					a = self.pool.get('ir.property').get(cr, uid,
							'property_account_income_categ', 'product.category',
							context=context)
				uosqty = _get_line_qty(line)
				print 'uos qty de service order line',uosqty
				uos_id = _get_line_uom(line)
				print 'uos id de service order line',uos_id
				pu = 0.0
				if uosqty:
					pu = round(line.price_unit * line.product_uom_qty / uosqty,
							int(config['price_accuracy']))
				inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
					'name': line.name,
					'account_id': a,
					'price_unit': pu,
					'quantity': uosqty,
					'discount': line.discount,
					'uos_id': uos_id,
					'product_id': line.product_id.id or False,
					'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
					'note': line.notes,
					'account_analytic_id': line.order_id.project_id.id,
				})
				print 'aqui hizo el insert'
				cr.execute('insert into contracts_service_order_line_invoice_rel (service_order_line_id,invoice_id) values (%d,%d)', (line.id, inv_id))
				self.write(cr, uid, [line.id], {'invoiced':True})
				create_ids.append(inv_id)
				print 'esto creo', create_ids
		return create_ids



	def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
		product_obj = self.pool.get('product.product')
		if not product_id:
			return {'value': {'product_uom': product_uos,
				'product_uom_qty': product_uos_qty}, 'domain':{}}

		product = product_obj.browse(cr, uid, product_id)
		value = {
			'product_uom' : product.uom_id.id,
		}
		# FIXME must depend on uos/uom of the product and not only of the coeff.
		try:
			value.update({
				'product_uom_qty' : product_uos_qty / product.uos_coeff,
				'th_weight' : product_uos_qty / product.uos_coeff * product.weight
			})
		except ZeroDivisionError:
			pass
		return {'value' : value}

	def copy(self, cr, uid, id, default=None,context={}):
		if not default:
			default = {}
		default.update({'state':'draft', 'move_ids':[], 'invoiced':False, 'invoice_lines':[]})
		return super(contracts_service_order_line, self).copy(cr, uid, id, default, context)

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False):
		#print 'product_id_change'

		product_uom_obj = self.pool.get('product.uom')
		partner_obj = self.pool.get('res.partner')
		product_obj = self.pool.get('product.product')

		if partner_id:
			lang = partner_obj.browse(cr, uid, partner_id).lang
		context = {'lang': lang, 'partner_id': partner_id}

		if not product:
			return {'value': {'price_unit': 0.0, 'notes':'', 'th_weight' : 0,
				'product_uos_qty': qty}, 'domain': {'product_uom': [],
					'product_uos': []}}

		if not pricelist:
			raise osv.except_osv('No Pricelist !',
					'You have to select a pricelist in the sale form !\n'
					'Please set one before choosing a product.')

		if not date_order:
			date_order = time.strftime('%Y-%m-%d')
		price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
				product, qty or 1.0, partner_id, {
					'uom': uom,
					'date': date_order,
					})[pricelist]
		if price is False:
			raise osv.except_osv('No valid pricelist line found !',
					"Couldn't find a pricelist line matching this product and quantity.\n"
					"You have to change either the product, the quantity or the pricelist.")

		product = product_obj.browse(cr, uid, product, context=context)

		if uom:
			uom2 = product_uom_obj.browse(cr, uid, uom)
			if product.uom_id.category_id.id <> uom2.category_id.id:
				uom = False

		if uos:
			if product.uos_id:
				uos2 = product_uom_obj.browse(cr, uid, uos)
				if product.uos_id.category_id.id <> uos2.category_id.id:
					uos = False
			else:
				uos = False

		result = {'price_unit': price, 'type': product.procure_method,
				'notes': product.description_sale}

		if update_tax: #The quantity only have changed
			result['delay'] = (product.sale_delay or 0.0)
			taxes = self.pool.get('account.tax').browse(cr, uid,
					[x.id for x in product.taxes_id])
			taxep = None
			if partner_id:
				taxep = self.pool.get('res.partner').browse(cr, uid,
						partner_id).property_account_tax
			if not taxep or not taxep.id:
				result['tax_id'] = [x.id for x in product.taxes_id]
			else:
				res5 = [taxep.id]
				for t in taxes:
					if not t.tax_group==taxep.tax_group:
						res5.append(t.id)
				result['tax_id'] = res5

		result['name'] = product.partner_ref

		domain = {}
		if not uom and not uos:
			result['product_uom'] = product.uom_id.id
			if product.uos_id:
				result['product_uos'] = product.uos_id.id
				result['product_uos_qty'] = qty * product.uos_coeff
				uos_category_id = product.uos_id.category_id.id
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
				uos_category_id = False
			result['th_weight'] = qty * product.weight
			domain = {'product_uom':
						[('category_id', '=', product.uom_id.category_id.id)],
						'product_uos':
						[('category_id', '=', uos_category_id)]}
		elif uom: # whether uos is set or not
			default_uom = product.uom_id and product.uom_id.id
			q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
			if product.uos_id:
				result['product_uos'] = product.uos_id.id
				result['product_uos_qty'] = q * product.uos_coeff
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = q
			result['th_weight'] = q * product.weight
		elif uos: # only happens if uom is False
			result['product_uom'] = product.uom_id and product.uom_id.id
			result['product_uom_qty'] = qty_uos / product.uos_coeff
			result['th_weight'] = result['product_uom_qty'] * product.weight
		#print 'result=',result
		#print 'domain=',domain
		return {'value': result, 'domain': domain}

	def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False):
		res = self.product_id_change(cursor, user, ids, pricelist, product,
				qty=0, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
				partner_id=partner_id, lang=lang, update_tax=update_tax,
				date_order=date_order)
		if 'product_uom' in res['value']:
			del res['value']['product_uom']
		if not uom:
			res['value']['price_unit'] = 0.0
		return res

contracts_service_order_line()

#
#	Quoted Services
#

class contracts_order_services(osv.osv):
	def copy(self, cr, uid, id, default=None, context={}):
		if not default: default = {}
		default.update( {'invoice_lines':[]})
		return super(sale_order_line, self).copy(cr, uid, id, default, context)

	def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			res[line.id] = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		return res

	def _amount_line(self, cr, uid, ids, field_name, arg, context):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			res[line.id] = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	def _number_packages(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			try:
				res[line.id] = int(line.product_uom_qty / line.product_packaging.qty)
			except:
				res[line.id] = 1
		return res
	
	def _get_1st_packaging(self, cr, uid, context={}):
		cr.execute('select id from product_packaging order by id asc limit 1')
		res = cr.fetchone()
		if not res:
			return False
		return res[0]

	_name = 'contracts.order.services'
	_description = 'Contract Order Services'
	_columns = {
		'order_id': fields.many2one('contracts.order', 'Order Ref', required=True, ondelete='cascade', select=True),
		'name': fields.char('Description', size=256, required=True, select=True),
		'sequence': fields.integer('Sequence'),
		'delay': fields.float('Delivery Delay', required=True),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
		'invoice_lines': fields.many2many('account.invoice.line', 'contracts_order_services_invoice_rel', 'contracts_order_services','invoice_id', 'Invoice Lines', readonly=True),
		'invoiced': fields.boolean('Invoiced', readonly=True),
		'init': fields.boolean('Initial'),
		'procurement_id': fields.many2one('mrp.procurement', 'Procurement'),
		'price_unit': fields.float('Unit Price', required=True, digits=(16, int(config['price_accuracy']))),
		'price_net': fields.function(_amount_line_net, method=True, string='Net Price', digits=(16, int(config['price_accuracy']))),
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
		'tax_id': fields.many2many('account.tax', 'contract_order_tax', 'order_id', 'tax_id', 'Taxes'),
		'type': fields.selection([('make_to_stock','from stock'),('make_to_order','on order')],'Procure Method', required=True),
		'prod_type': fields.selection([('product','Producto'),('consu', 'Consumible'),('service','Servicio')], 'Product Type', required=True),
		'property_ids': fields.many2many('mrp.property', 'sale_order_line_property_rel', 'order_id', 'property_id', 'Properties'),
		'address_allotment_id' : fields.many2one('res.partner.address', 'Allotment Partner'),
		'product_uom_qty': fields.float('Quantity (UOM)', digits=(16,2), required=True),
		'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
		'product_uos_qty': fields.float('Quantity (UOS)'),
		'product_uos': fields.many2one('product.uom', 'Product UOS'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging used'),
		'move_ids': fields.one2many('stock.move', 'sale_line_id', 'Inventory Moves', readonly=True),
		'discount': fields.float('Discount (%)', digits=(16,2)),
		'number_packages': fields.function(_number_packages, method=True, type='integer', string='Number packages'),
		'hour': fields.selection([
		('01','01 A.M.'),('02','02 A.M.'),('03','03 A.M.'),('04','04 A.M.'),
		('05','05 A.M.'),('06','06 A.M.'),('07','07 A.M.'),('08','08 A.M.'),
		('09','09 A.M.'),('10','10 A.M.'),('11','11 A.M.'),('12','12 A.M.'),
		('13','01 P.M.'),('14','02 P.M.'),('15','03 P.M.'),('16','04 P.M.'),
		('17','05 P.M.'),('18','06 P.M.'),('19','07 P.M.'),('20','08 P.M.'),
		('21','09 P.M.'),('22','10 P.M.'),('23','11 P.M.'),('24','12 P.M.'),
		], 'Hour', help=""),
		'minutes': fields.selection([
		('00','00'),('15','15'),('30','30'),('45','45'),
		], 'Minutes', help=""),
		'serv_len': fields.char('Serv. Length', size=16,),
		'week': fields.selection([
		('none','None'),('first_week','First '),('second_week','Second'),('third_week','Third'),('forth_week','Fourth'),
		], 'Week', help=""),
		'day': fields.selection([
		('none','None'),('SUNDAY','Sunday'),('MONDAY','Monday'),('TUESDAY','Tuesday'),('WEDNESDAY','Wednesday'),('THURSDAY','Thursday'),('FRIDAY','Friday'),('SATURDAY','Saturday')]),
		'notes': fields.text('Notes'),
		'th_weight' : fields.float('Weight'),
		'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Canceled')], 'State', required=True, readonly=True),
	}
	_order = 'sequence, id'
	_defaults = {
		'discount': lambda *a: 0.0,
		'delay': lambda *a: 0.0,
		'product_uom_qty': lambda *a: 1,
		'product_uos_qty': lambda *a: 1,
		'sequence': lambda *a: 10,
		'invoiced': lambda *a: 0,
		'state': lambda *a: 'draft',
		'type': lambda *a: 'make_to_stock',
		'product_packaging': _get_1st_packaging,
	}
	def invoice_line_create(self, cr, uid, ids, context={}):
		def _get_line_qty(line):
			if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
				if line.product_uos:
					return line.product_uos_qty or 0.0
				return line.product_uom_qty
			else:
				return self.pool.get('mrp.procurement').quantity_get(cr, uid,
						line.procurement_id.id, context)

		def _get_line_uom(line):
			if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
				if line.product_uos:
					return line.product_uos.id
				return line.product_uom.id
			else:
				return self.pool.get('mrp.procurement').uom_get(cr, uid,
						line.procurement_id.id, context)

		create_ids = []
		for line in self.browse(cr, uid, ids, context):
			if not line.invoiced:
				if line.product_id:
					a =  line.product_id.product_tmpl_id.property_account_income.id
					if not a:
						a = line.product_id.categ_id.property_account_income_categ.id
					if not a:
						raise osv.except_osv('Error !',
								'There is no income account defined ' \
										'for this product: "%s" (id:%d)' % \
										(line.product_id.name, line.product_id.id,))
				else:
					a = self.pool.get('ir.property').get(cr, uid,
							'property_account_income_categ', 'product.category',
							context=context)
				uosqty = _get_line_qty(line)
				uos_id = _get_line_uom(line)
				pu = 0.0
				if uosqty:
					pu = round(line.price_unit * line.product_uom_qty / uosqty,
							int(config['price_accuracy']))
				inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
					'name': line.name,
					'account_id': a,
					'price_unit': pu,
					'quantity': uosqty,
					'discount': line.discount,
					'uos_id': uos_id,
					'product_id': line.product_id.id or False,
					'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
					'note': line.notes,
					'account_analytic_id': line.order_id.project_id.id,
				})
				cr.execute('insert into sale_order_line_invoice_rel (contracts_order_services,invoice_id) values (%d,%d)', (line.id, inv_id))
				self.write(cr, uid, [line.id], {'invoiced':True})
				create_ids.append(inv_id)
		return create_ids

	def button_confirm(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'confirmed'})

	def button_done(self, cr, uid, ids, context={}):
		return
		wf_service = netsvc.LocalService("workflow")
		res = self.write(cr, uid, ids, {'state':'done'})
		for line in self.browse(cr,uid,ids,context):
			wf_service.trg_write(uid, 'contracts.order.services', line.order_id.id, cr)

		return res

	def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
		product_obj = self.pool.get('product.product')
		if not product_id:
			return {'value': {'product_uom': product_uos,
				'product_uom_qty': product_uos_qty}, 'domain':{}}

		product = product_obj.browse(cr, uid, product_id)
		value = {
			'product_uom' : product.uom_id.id,
		}
		# FIXME must depend on uos/uom of the product and not only of the coeff.
		try:
			value.update({
				'product_uom_qty' : product_uos_qty / product.uos_coeff,
				'th_weight' : product_uos_qty / product.uos_coeff * product.weight
			})
		except ZeroDivisionError:
			pass
		return {'value' : value}

	def copy(self, cr, uid, id, default=None,context={}):
		if not default:
			default = {}
		default.update({'state':'draft', 'move_ids':[], 'invoiced':False, 'invoice_lines':[]})
		return super(sale_order_line, self).copy(cr, uid, id, default, context)

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False):
		product_uom_obj = self.pool.get('product.uom')
		partner_obj = self.pool.get('res.partner')
		product_obj = self.pool.get('product.product')

		if partner_id:
			lang = partner_obj.browse(cr, uid, partner_id).lang
		context = {'lang': lang, 'partner_id': partner_id}

		if not product:
			return {'value': {'price_unit': 0.0, 'notes':'', 'th_weight' : 0,
				'product_uos_qty': qty}, 'domain': {'product_uom': [],
					'product_uos': []}}

		if not pricelist:
			raise osv.except_osv('No Pricelist !',
					'You have to select a pricelist in the sale form !\n'
					'Please set one before choosing a product.')

		if not date_order:
			date_order = time.strftime('%Y-%m-%d')
		price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
				product, qty or 1.0, partner_id, {
					'uom': uom,
					'date': date_order,
					})[pricelist]
		if price is False:
			raise osv.except_osv('No valid pricelist line found !',
					"Couldn't find a pricelist line matching this product and quantity.\n"
					"You have to change either the product, the quantity or the pricelist.")

		product = product_obj.browse(cr, uid, product, context=context)

		if uom:
			uom2 = product_uom_obj.browse(cr, uid, uom)
			if product.uom_id.category_id.id <> uom2.category_id.id:
				uom = False

		if uos:
			if product.uos_id:
				uos2 = product_uom_obj.browse(cr, uid, uos)
				if product.uos_id.category_id.id <> uos2.category_id.id:
					uos = False
			else:
				uos = False

		result = {'price_unit': price, 'type': product.procure_method,
				'notes': product.description_sale}

		if update_tax: #The quantity only have changed
			result['delay'] = (product.sale_delay or 0.0)
			taxes = self.pool.get('account.tax').browse(cr, uid,
					[x.id for x in product.taxes_id])
			taxep = None
			if partner_id:
				taxep = self.pool.get('res.partner').browse(cr, uid,
						partner_id).property_account_tax
			if not taxep or not taxep.id:
				result['tax_id'] = [x.id for x in product.taxes_id]
			else:
				res5 = [taxep.id]
				for t in taxes:
					if not t.tax_group==taxep.tax_group:
						res5.append(t.id)
				result['tax_id'] = res5

		result['name'] = product.partner_ref

		domain = {}
		if not uom and not uos:
			result['product_uom'] = product.uom_id.id
			if product.uos_id:
				result['product_uos'] = product.uos_id.id
				result['product_uos_qty'] = qty * product.uos_coeff
				uos_category_id = product.uos_id.category_id.id
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
				uos_category_id = False
			result['th_weight'] = qty * product.weight
			domain = {'product_uom':
						[('category_id', '=', product.uom_id.category_id.id)],
						'product_uos':
						[('category_id', '=', uos_category_id)]}
		elif uom: # whether uos is set or not
			default_uom = product.uom_id and product.uom_id.id
			q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
			if product.uos_id:
				result['product_uos'] = product.uos_id.id
				result['product_uos_qty'] = q * product.uos_coeff
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = q
			result['th_weight'] = q * product.weight
		elif uos: # only happens if uom is False
			result['product_uom'] = product.uom_id and product.uom_id.id
			result['product_uom_qty'] = qty_uos / product.uos_coeff
			result['th_weight'] = result['product_uom_qty'] * product.weight
		result['prod_type'] = product.type
		#print 'type=',product.type
		return {'value': result, 'domain': domain}

	def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False):
		res = self.product_id_change(cursor, user, ids, pricelist, product,
				qty=0, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
				partner_id=partner_id, lang=lang, update_tax=update_tax,
				date_order=date_order)
		if 'product_uom' in res['value']:
			del res['value']['product_uom']
		if not uom:
			res['value']['price_unit'] = 0.0
		return res

contracts_order_services()


#
#	Contract Equipments
#

class contracts_equipment(osv.osv):
	
	_name = 'contracts.equipment'

	_columns = {
		'contract_id': fields.many2one('contracts.order', 'Cotract', required=True, ondelete='cascade', select=True),
		'order_equipment': fields.one2many('service.order.equipment', 'name', 'Order Equipment', readonly=False),
		'name':  fields.char('Position', size=46,  required=True),
		'equipment_type_id': fields.many2one('equipment.type', 'Equipment Type', required=False ),
		'barcode': fields.char('BarCode', size=256, required=True, select=True),
		'area_id': fields.many2one('contracts.areas', 'Area',required=True),
		'state': fields.selection([('active','Active'),('lost','Lost'),('damage','Damage'),('inactive','Inavtive')], 'State', required=True),
		'disposition': fields.selection([('sold','Sold'),('rented','Rented')],'Disposition'),
		'life_span': fields.selection([('definitive','Definitive'),('temporal','Temporal')],'Life Span'),
		'replaced': fields.boolean('Replaced'),
		'notes': fields.text('Notes'),
		}
	#_order = 'sequence, id'
	_defaults = {
		'state': lambda *a: 'active',
		'disposition': lambda *a: 'sold',
		'life_span': lambda *a: 'definitive',
		}

contracts_equipment()




#

#	Service Aplications
#

class service_order_aplication(osv.osv):

	_name = 'service.order.aplication'

	_columns = {
		'order_id': fields.many2one('service.order', 'Service Order', required=True, ondelete='cascade', select=True),
		'name': fields.char('Name', size=64, required=False, select=True),
		'area_id': fields.many2one('contracts.areas', 'Area',required=True),
		'product_id':fields.many2one('product.product', 'Product',required=True),
		'product_preparetion_uom_qty': fields.float('Quantity (UOM)', digits=(16,2), required=True),
		'product_preparetion_uom': fields.many2one('product.uom', 'Product UOM', required=True),
		'product_aplication_uom_qty': fields.float('Quantity (UOM)', digits=(16,2), required=True),
		'product_aplication_uom': fields.many2one('product.uom', 'Product UOM', required=True),
		'method': fields.selection([
		('1','Grietas y Hendiduras'),
		('2','Bandeo Interior'),
		('3','Bandeo Exterior'),
		('4','Nebulizacion'),
		('5','Aerosol'),
		('6','Inpeccion'),
		('7','Colocacion Gomas'),
		('8','Superficie General'),
		('9','Bomba a Motor'),
		('10','Cebado con Gel'),
		('11','Cebado con Granulos'),
		('12','Cebado para Roedores'),
		('13','Espolvoreo'),
		], 'Method', readonly=False, select=True),
		'replaced': fields.boolean('Replaced'),
		'notes': fields.text('Notes'),
		}
	#_order = 'sequence, id'
	_defaults = {
		}

service_order_aplication()



#
#	Service Activity
#

class service_order_activity(osv.osv):

	_name = 'service.order.activity'

	_columns = {
		'order_id': fields.many2one('service.order', 'Service Order', required=True, ondelete='cascade', select=True),
		'name': fields.char('Name', size=64, required=False, select=True),
		'pest': fields.many2one('contracts.pest', 'Pest', required=True),
		'area_id': fields.many2one('contracts.areas', 'Area',required=True),
		'damage': fields.selection([
		('1','Roeduras'),
		('2','Perforacion de Empaque'),
		('3','Contaminacion'),
		('4','Mal Aspecto'),
		], 'Damage', readonly=False, select=True),
		'evidence': fields.selection([
		('1','Excretas'),
		('2','Manchas'),
		('3','Organismo Muerto'),
		('4','Organismo Vivo'),
		('5','Exoesqueleto'),
		], 'Evidence', readonly=False, select=True),
		'notes': fields.text('Notes'),
		}
	#_order = 'sequence, id'
	_defaults = {
		}

service_order_activity()

class service_order_recomendation(osv.osv):

	_name = 'service.order.recomendation'

	_columns = {
		'order_id': fields.many2one('contracts.order', 'Service Order', required=True, ondelete='cascade', select=True),
		'name': fields.char('Name', size=64, required=False, select=True),
		'attended': fields.boolean('Recomendation Attended'),
		'notes': fields.text('Notes'),
		'reported_times':fields.integer('Times Reported'),
		#'times_reported': fields.function(_amount_line_net, method=True, string='Net Price', digits=(16, int(config['price_accuracy']))),
		}
	#_order = 'sequence, id'
	_defaults = {
		}

service_order_recomendation()




class service_order_survay(osv.osv):
 	_name = 'service.order.survay'
 	_columns = {
 		'order_id':fields.many2one('service.order', 'Service Order', required=True, ondelete='cascade', select=True),
 		'name':fields.many2one('inspection.category', 'Survay Category', required=False, readonly=False),
		'survay_inspection_id':fields.one2many('service.order.survay.inspection', 'name', 'Category', readonly=False),
		'notes': fields.char('Notes', size=128),
 	}
 	_defaults = {
 	}
service_order_survay()


class service_order_survay_inspection(osv.osv):
 	_name = 'service.order.survay.inspection'
 	_columns = {
		'name': fields.many2one('service.order.survay', 'Survay Category', required=True, ondelete='cascade', select=True),
 		'inspection_question_id':fields.many2one('inspection.question', 'Quesiotn', required=True ),
		'answer_yes': fields.boolean('Yes'),
		'answer_no': fields.boolean('No'),
		'answer_na': fields.boolean('N.A.'),
 		'notes': fields.char('Notes', size=128),
 	}
 	_defaults = {
 	}
	
service_order_survay_inspection()




class service_order_equipment(osv.osv):

	

	_name = 'service.order.equipment'

	_columns = {
		'order_id': fields.many2one('service.order', 'Service Order', required=True, ondelete='cascade', select=True),
		'name':fields.many2one('contracts.equipment', 'Postion', required=False, readonly=False),
		'equipment_type_id': fields.many2one('equipment.type', 'Equipment Type', required=True ),
		'barcode': fields.char('BarCode', size=256, required=False, select=True),
		'area_id': fields.many2one('contracts.areas', 'Area',required=True),
		'equipment_inspection_id': fields.one2many('service.order.equipment.inspection', 'name', 'Equipment', readonly=False),
		'notes': fields.text('Notes'),
		}
	#_order = 'sequence, id'
	_defaults = {
		}


	def onchange_equipment_id(self, cr, uid, ids, contracts_equipment_id):
		if not contracts_equipment_id:
			return {'value':{'equipment_type_id': False}}
		type_id = self.pool.get('contracts.equipment').browse(cr, uid, contracts_equipment_id).equipment_type_id.id
		area_id = self.pool.get('contracts.equipment').browse(cr, uid, contracts_equipment_id).area_id.id
		barcode = self.pool.get('contracts.equipment').browse(cr, uid, contracts_equipment_id).barcode
		return {'value':{'equipment_type_id': type_id,'area_id':area_id,'barcode':barcode}}

service_order_equipment()

class service_order_equipment_inspection(osv.osv):

	_name = 'service.order.equipment.inspection'

	_columns = {
		'name': fields.many2one('service.order.equipment', 'Position', required=True, ondelete='cascade', select=True),
		'equipment_atribut_id':fields.many2one('equipment.atribut', 'Equipment Atribut', required=True ),
		'atribut_checked': fields.boolean('Atribut Cheked'),
		'atribut_value': fields.char('Atribut Value', size=46, ),
		'replaced': fields.boolean('Replaced'),
		'notes': fields.text('Notes'),
		}
	#_order = 'sequence, id'
	_defaults = {
		}

service_order_equipment_inspection()
