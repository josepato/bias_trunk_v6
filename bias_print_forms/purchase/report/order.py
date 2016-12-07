## -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import pooler
from report import report_sxw
import text
import re

class order(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
        	super(order, self).__init__(cr, uid, name, context)
        	self.localcontext.update({
			'time': time,
			'texto': self._get_text,
			'date_sp': self.date_sp,
			'moneyfmt': text.moneyfmt,
			'get_money_name': text.get_money_name,
			'invoice_addr': self.invoice_addr,
			'comma_me': self.comma_me,
			'ship_addr': self.ship_addr,
			'get_total_products': self._get_total_products,
			'convert_value': self._convert_value,
			'create_user': self.user_uid,
        	})

	def date_sp(self, date):
		print 'date=',date
		return 'ok'


	def _get_text(self, amount):
		return text.text(int(amount))
	
	def invoice_addr(self, cr, uid,  company_id, adr_pref):
		res = {}
		invoce_addres = pooler.get_pool(self.cr.dbname).get('res.partner').address_get(cr, uid, [company_id.partner_id.id], [adr_pref])
		address_brw =  pooler.get_pool(self.cr.dbname).get('res.partner.address').browse(cr, uid, invoce_addres['invoice'])
		res['name'] = address_brw.name
		res['sa'] = company_id.name
		res['street'] = address_brw.street
		res['street2'] = address_brw.street2
		res['city'] = address_brw.city
		res['state'] = address_brw.state_id.name
		res['country'] = address_brw.country_id.name
		res['vat'] = company_id.partner_id.vat
		res['zip'] = address_brw.zip
		return [res,]

	
	def ship_addr(self,obj, dest_address_id, wharehouse_id):
		res = {}
		if dest_address_id:
			address_id = dest_address_id.id
		elif wharehouse_id.partner_address_id:
			#address_id =  pooler.get_pool(self.cr.dbname).get('stock.warehouse').browse(obj._cr, obj._uid,[wharehouse_id]).partner_address_id.id
			address_id =  wharehouse_id.partner_address_id.id
		else:
			res['name'] = ''
			res['sa'] = ''
			res['street'] = ''
			res['street2'] = ''
			res['city'] = ''
			res['state'] = ''
			res['country'] = ''
			res['vat'] = ''
			res['zip'] = ''
			return [res, ]
		dest_addr_brw =  pooler.get_pool(self.cr.dbname).get('res.partner.address').browse(obj._cr, obj._uid, address_id)
		res['name'] = dest_addr_brw.name
		res['sa'] = dest_addr_brw.partner_id.name
		res['street'] = dest_addr_brw.street
		res['street2'] = dest_addr_brw.street2
		res['city'] = dest_addr_brw.city
		res['state'] = dest_addr_brw.state_id.name
		res['country'] = dest_addr_brw.country_id.name
		res['vat'] = dest_addr_brw.partner_id.vat
		res['zip'] = dest_addr_brw.zip
		return [res,]


	def comma_me(self,amount):
		if not amount:
		    amount = 0.0
		if  type(amount) is float :
		    amount = str('%.2f'%amount)
		else :
		    amount = str(amount)
		if (amount == '0'):
			return ' '
		orig = amount
		new = re.sub("^(-?\d+)(\d{3})", "\g<1>,\g<2>", amount)
		if orig == new:
			return new
		else:
			return self.comma_me(new)

	def user_uid(self, obj_id):
		query = "SELECT u.name FROM res_users u WHERE id = (SELECT p.create_uid FROM purchase_order p WHERE p.id =%s)"%(obj_id)
		self.cr.execute(query)
		res = self.cr.fetchone()
		if res:
			res=res[0]
		return res

	def _convert_value(self, value, context={}):
		if not value:
			return ''
		if context.get('strip', False) and context.get('model', False):
			quitar=len(context['model'])+3
			value = value[quitar:]
			return value
		if context.get('money_format', False):
			return '$ ' + text.moneyfmt( '%.2f' % float(value))
		return value

	def _get_total_products(self, obj_id):
		totales = "SELECT SUM(product_qty) FROM purchase_order_line WHERE order_id=%s"%(obj_id.id)
		self.cr.execute(totales)
		res = self.cr.fetchone()
		if res:
			res=res[0]
		return text.moneyfmt( '%.2f' % float(res))
		
report_sxw.report_sxw('report.purchase.order.bias','purchase.order','addons/bias_print_forms/purchase/report/order.rml', parser=order)

