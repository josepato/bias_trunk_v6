##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import time
import wizard
import pooler
import calendar
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

dates_form = '''<?xml version="1.0"?>
<form string="Service Order Programer">
	<field name="date_from"/>
	<field name="date_to"/>
</form>'''

dates_fields = {
	'date_from': {'string': 'Date From:', 'type': 'date',
		 'required': True},
	'date_to': {'string':'Date To:', 'type':'date',
		 'required':True},
	}


class wizard_contract_orders(wizard.interface):

	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		data['form']['date_from'] = time.strftime('%Y-%m-%d')
		data['form']['date_to'] = time.strftime('%Y-%m-%d')
		return data['form']


	def getDayNumberByWeekOccurance(self,planned_day,year,month):
	    first_week,second_week,third_week,forth_week,fifth_week = self.getMonthByWeeks(year,month)
	    #print 'el plannday',planned_day
	    day_method='calendar.'+planned_day['day']
	    if first_week[eval(day_method)]:
		    if planned_day['week'] == 'first_week':
			    service_date = first_week[eval(day_method)]
		    elif planned_day['week'] == 'second_week':
			    service_date = second_week[eval(day_method)]
			    
		    elif planned_day['week'] == 'third_week':
			    service_date = third_week[eval(day_method)]
			    
		    elif planned_day['week'] == 'forth_week':
			    service_date = forth_week[eval(day_method)]
			    
		    elif planned_day['week'] == 'fifth_week':
			    service_date = fifth_week[eval(day_method)]
			    
		    elif planned_day['week'] == 'none':
			    service_date = 0
	    else:
		    if planned_day['week'] == 'first_week':
			    service_date = second_week[eval(day_method)]
		    elif planned_day['week'] == 'second_week':
			    service_date = third_week[eval(day_method)]
		    elif planned_day['week'] == 'third_week':
			    service_date = forth_week[eval(day_method)]
		    elif planned_day['week'] == 'forth_week':
			    service_date = fifth_week[eval(day_method)]
		    elif planned_day['week'] == 'service_date':
			    fifth_week = fifth_week[eval(day_method)]
		    elif planned_day['week'] == 'none':
			    service_date = 0
			    
	    return service_date

	def getMonthByWeeks(self,year,month):
	    c = calendar.monthcalendar(year, month)
	    first_week = c[0]
	    second_week = c[1]
	    third_week = c[2]
	    forth_week = c[3]
	    fifth_week =c[4]
	    return first_week,second_week,third_week,forth_week,fifth_week

	

	def getOnlyContractsForSelectedMonths(self,cr,uid,contracts_ids,schedule_months):
		res=[]
		pool=pooler.get_pool(cr.dbname)
		obj_contracts=pool.get('contracts.order')
		months_search=[]
		for sm in schedule_months:
			months_search+=['%02i'%sm[1]]
		for cont_id in contracts_ids:
			info=obj_contracts.read(cr,uid,[cont_id],['date_start','periodicity'])[0]
			date_start=info['date_start']
			periodicity=info['periodicity']
			if len(periodicity)==1:
				periodicity='12/12'
			months_list=[date_start.split('-')[1],]
			month=int(months_list[0])
			frecuency=12/int(periodicity.split('/')[0])
			vv=len(res)
			while len(months_list) < int(periodicity.split('/')[0]):
				if '%02i'%month in months_search:
					if not cont_id in res:
						res+=[cont_id,]
				month=month+frecuency
				if month > 12:
					month = month -12
				months_list.append('%02i'%(month))
		return res

	def getContractsInServiceOrder(self, cr, mk_day, do_order_id):
		#pool=pooler.get_pool(cr.dbname)	
		#obj_service=pool.get('service.order')
		if len(do_order_id) == 1:
			oo = tuple(do_order_id)
			oo = oo + oo
		else:
			oo = tuple(do_order_id)
			
		query = "select contract_id from service_order where contract_id in %s and date_order >= '%s' and date_order  <= '%s'"%(oo,  time.strftime('%Y-%m-%d 00:00:00',time.localtime(mk_day)), time.strftime('%Y-%m-%d 24:00:00',time.localtime(mk_day)))
		#print 'el query', query
		cr.execute(query)
		contracts_to_extract = cr.fetchall()
		#print 'ordernes originales', do_order_id
		#print 'ordenes a extraer', contracts_to_extract
		if len(contracts_to_extract):
			for cc in contracts_to_extract:
				try:
					do_order_id.remove(cc[0])
				except ValueError:
					pass
		#print 'ordenes remanentes', do_order_id
		return do_order_id




	def getScheduleMonths(self,date_from,date_to):
		year_month_from=[int(date_from.split('-')[0]),int(date_from.split('-')[1])]
		year_month_to=[int(date_to.split('-')[0]),int(date_to.split('-')[1])]
		schedule_months=[year_month_from,]
		if year_month_from[1]>year_month_to[1]:
			mm_to=year_month_to[1]+12
		else:
			mm_to=year_month_to[1]
		if  year_month_from[0] != year_month_to[0]:
			mm_to+=(year_month_to[0]-year_month_from[0])*12
		mm=year_month_from[1]
		yy=year_month_from[0]
		for dd in range(year_month_from[1],mm_to):
			mm+=1
			if mm >12:
				mm-=12
				yy+=1
			schedule_months+=[[yy,mm]]
		return schedule_months
	
	def _create_service_orders(self, cr, uid, data, context):
		pool=pooler.get_pool(cr.dbname)
		obj_contract_service = pool.get('contracts.order.services')
		obj_contracts=pool.get('contracts.order')
		obj_service=pool.get('service.order')
		args=['week','day','hour','minutes']
		date_from=data['form']['date_from']
		mk_date_from=time.mktime([int(date_from.split('-')[0]),int(date_from.split('-')[1]),int(date_from.split('-')[2]),0,0,0,0,0,0])
		now=time.time()
		if mk_date_from < now:
			mk_date_from=now
		date_to=data['form']['date_to']
		mk_date_to=time.mktime([int(date_to.split('-')[0]),int(date_to.split('-')[1]),int(date_to.split('-')[2]),24,59,0,0,0,0])
		schedule_months=self.getScheduleMonths(date_from,date_to)
		contracts_ids=obj_contracts.search(cr, uid,[('state','=','expired')])
		contracts_ids+=obj_contracts.search(cr, uid,[('state','=','progress')])
		#contratos=obj_contracts.browse(cr,uid,contracts_ids[0])
		contracts_ids=self.getOnlyContractsForSelectedMonths(cr,uid,contracts_ids,schedule_months)
		res_ids = []
		for order_id in obj_contracts.browse(cr, uid, contracts_ids, context):
			#print 'la vuelta del order_id'
			planned_day=[]
			service_ids=obj_contract_service.search(cr, uid,[('order_id','=',int(order_id.id))])
			cc=0
			#print 'esto lo mete al for:',obj_contract_service.read(cr,uid,service_ids,['init'])
			ww=[]
			dd={}
			for ss in obj_contract_service.read(cr,uid,service_ids,['init']):
				if not ss['init']:
					dicc=[obj_contract_service.read(cr,uid,int(ss['id']),args),][0]
					#print 'args',args
					contract_service=[obj_contract_service.browse(cr,uid,int(ss['id']),context),]
					dicc['contract_service']=contract_service
					#print '/n asi va planned day:',planned_day
					#print 'asi esta el diccionario;',ss['id'],dicc
					#print 'asi esta ww',ww
					if planned_day:
						if dicc['week'] in ww:
							#print 'if week in ww'
							if dicc['day'] in dd[ii['week']]:
								cc=ww.index(dicc['week'])
								#print 'cc',cc
								#print 'week',dicc['week']
								planned_day[cc]['contract_service']+=contract_service
							else:
								planned_day+=[dicc,]
								#cc+=1
						else:
							#print 'aver'
							planned_day+=[dicc,]
							#cc+=1
					else:
						planned_day=[]
						if dicc['week'] and dicc['day']:
							#print 'asi esta el dicc',dicc
							planned_day.append(dicc)
							#print 'asi imprime si no hubo plannedday',planned_day
					for ii in planned_day:
						#print 'entro para crecer el ww y dd', ii['week']
						if ii['week'] not in ww:
							ww.append(ii['week'])
							#print 'el iidayk',ii['week'], dd
							if dd.has_key(ii['week']):
								dd[ii['week']]=dd[ii['week']]+(ii['day'])
							else:
								dd[ii['week']]=(ii['day'])
						#print 'asi va ww y dd', ww,dd
	

			if  len(planned_day)==0:
				planned_day+=obj_contracts.read(cr,uid,[str(order_id.id)],args)
				#print 'el planed day',planned_day
				#print 'los args',args
				#print 'el order_id.id', order_id.id
				#print 'asi esta el read',obj_contracts.read(cr,uid,str(order_id.id),args)
				planned_day[0]['contract_service']=obj_contract_service.browse(cr,uid,service_ids,context)
				
				
			serv_ids=[]
			for service_day in planned_day:
				for mm in schedule_months:
					do_order_id = self.getOnlyContractsForSelectedMonths(cr,uid,[int(order_id.id),],[mm])
					#print 'el orders', do_order_id
					#print 'el service day', service_day
					if do_order_id:
						day_num = self.getDayNumberByWeekOccurance(service_day,mm[0],mm[1])
						#print 'day num', day_num
						
						day = '%i-%02i-%i'%(mm[0],mm[1],day_num)
						mk_day = time.mktime([mm[0],mm[1],day_num,int(service_day['hour']),int(service_day['minutes']),0,0,0,0])
						#print 'el mkday', mk_day
						#print 'serv'
						if (mk_day > mk_date_from) and (mk_day < mk_date_to):
							dt = time.strftime('%Y-%m-%d',time.localtime(mk_day))
							ds = mx.DateTime.strptime(dt, '%Y-%m-%d')
							ds = ds + RelativeDateTime(hours=int(service_day['hour']), minutes=int(service_day['minutes']))
							do_order_id = self.getContractsInServiceOrder(cr, mk_day, do_order_id)
							#print 'el order_id.id', order_id.id
							#print 'el do order id', do_order_id
							if order_id.id in do_order_id:
								service_dir = self._service_order_dir(cr,uid,pool,order_id,ds,)
								res_id = obj_service.create(cr, uid, service_dir)
								res_ids += [res_id,]
								#print 'el service day',service_day
								serv_ids = self._create_service_line(cr,uid,service_day['contract_service'],res_id)
		#print 'las ordenes creadas', res_ids
		cr.execute('select id,name from ir_ui_view where model=%s and type=%s', ('account.move.line', 'form'))
		view_res = cr.fetchone()
		try:
			res_ids
		except:
			res_ids=[]
		res={
		'domain': "[('id','in',%s)]" % (res_ids),
		'name': 'Servic Orders',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'service.order',
		'view_id': False,
		'context': "{}",
		'type': 'ir.actions.act_window'
		}
		#print 'el return de res', res
		return res

                
	def _service_order_dir(self,cr,uid,pool,order_id,ds):
		res={}
		res['name']=pool.get('ir.sequence').get(cr,uid,'service.order')
		res['date_order']=ds
		res['contract_id']= order_id.id
		res['pricelist_id']=order_id.pricelist_id.id
		res['partner_id']=order_id.partner_id.id
		res['partner_shipping_id']=order_id.partner_shipping_id.id
		res['partner_order_id']=order_id.partner_order_id.id
		res['state']= 'in_progress'
		res['shop_id']=order_id.shop_id.id
		res['partner_invoice_id']=order_id.partner_invoice_id.id
		res['technician_id']=order_id.technician_id.id
		res['area_id']=[(6,0,[x.id for x in order_id.area_id])]
		res['pest_id']=[(6,0,[x.id for x in order_id.pest])]
		res['instructions']=order_id.instructions
		res['comments']=order_id.comments
		res['route_id']=order_id.route_id.id
		res['rep_equipment']=order_id.rep_equipment
		res['rep_survay']=order_id.rep_survay
		return res

	def _create_service_line(self,cr,uid,browse_records,serv_id):
		pool=pooler.get_pool(cr.dbname)
		obj_service_line=pool.get('service.order.line')
		service_line_dir={}
		ids=[]
		a=0
		for line in browse_records:
			a+=1
			#print 'line',line[0]
			service_line_dir['product_uom']=line.product_uom.id
			service_line_dir['name']=line.name
			service_line_dir['product_uos_qty']=line.product_uos_qty
			service_line_dir['product_id']=line.product_id.id
			service_line_dir['order_id']=serv_id
			service_line_dir['price_unit']=line.price_unit
			service_line_dir['tax_id']=[(6,0,[x.id for x in line.tax_id])]
			ids+=[obj_service_line.create(cr,uid,service_line_dir),]
		return ids
		
		
		   

	#def _crea

	states = {
		'init': {
			'actions': [_get_defaults],
			'result': {
				'type': 'form',
				'arch': dates_form,
				'fields': dates_fields,
				'state': [
					('end', 'Cancel'),
					('open', 'Create Orders')]
			}
		},
		'open': {
			'actions': [],
			'result': {
				'type': 'action',
				'action':_create_service_orders,
				'state':'end'
			}
		}
	}

wizard_contract_orders('schedule.contract.orders')


