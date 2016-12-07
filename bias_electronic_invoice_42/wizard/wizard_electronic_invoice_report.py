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

import pooler
import wizard
import base64
from osv import osv
import time
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import datetime
import re
import StringIO
import csv
from lxml import etree

dates_form = '''<?xml version="1.0"?>
<form string="Select period">
	<field name="company_id"/>
	<field name="fiscalyear" colspan="4"/>
	<field name="period" colspan="4" domain="[('fiscalyear_id','=',fiscalyear)]"/>
</form>'''

dates_fields = {
	'company_id': {'string': 'Company', 'type': 'many2one',
		'relation': 'res.company', 'required': True},
	'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
		'help': 'Keep empty for all open fiscal year'},
	'period': {'string': 'Period', 'type': 'many2one', 'relation': 'account.period',
		'help': ''},
}

export_form = """<?xml version="1.0"?>
	<form string="Payment Export">
   	<field name="report"/>
   	<field name="note" colspan="4" height="300" width="800" nolabel="1"/>
   	</form>"""

export_fields = {
    	'report' : {
        'string':'Export File',
        'type':'binary',
        'required': False,
        'readonly':True,
    	},
    	'note' : {'string':'Log','type':'text'},
}



def _get_report(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	fy_id = data['form']['fiscalyear']
	pe_id = data['form']['period']
	company_id = data['form']['company_id']
	agnio = int(pool.get('account.fiscalyear').browse(cr, uid, fy_id, context=context).date_start[:4])
	mes = int(pool.get('account.period').browse(cr, uid, pe_id, context=context).date_start[5:7])
	rfc = pool.get('res.company').browse(cr, uid, company_id, context=context).partner_id.vat
	rfc = re.sub('[-,._ \t\n\r\f\v]','',rfc)
	res = file = self._reporte(cr, uid, rfc, mes, agnio)
	buf=StringIO.StringIO()
	writer=buf.write(res)
	out=base64.encodestring(buf.getvalue())
	buf.close()
	
	return {'note': res, 'report': out}
	

def last_day_of_month(date):
	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)	
	
	
	
class wizard_electronic_report_invoice(wizard.interface):



	def _reporte(self, cr, uid, rfc, mes, agnio):
		pool = pooler.get_pool(cr.dbname)
		attachment_obj = pool.get('ir.attachment')
		date_from = "%s-%s-01 00:00:00"%(agnio, mes)
		date_to = last_day_of_month(datetime.date(agnio, mes, 1)).strftime('%Y-%m-%d 24:00:00')
		cr.execute("Select id from account_journal where code in ('factura_e', 'nota_credito_e')")
		journal_id = cr.fetchall()
		journal_id = tuple([id[0] for id in  journal_id])
		if len(journal_id) <= 1:
			journal_query = 'journal_id = %s'%journal_id[0]
		else:
			journal_query = 'journal_id in %s'%str((journal_id))
		query = "SELECT id, number from account_invoice where sign_date between '%s' and '%s' and state not in ('proforma','proforma2', 'draft') and %s order by number"%(date_from, date_to, journal_query)
		cr.execute(query)
		invoiced_ids = cr.fetchall()
		query = "SELECT id, number from account_invoice where cancel_date between '%s' and '%s'  and  %s   order by number"%(date_from, date_to, journal_query)
		cr.execute(query)
		canceld_ids = cr.fetchall()
		res_open = {}
		res_cancel = {}
		for id in invoiced_ids:
			res[id[1]]={'id':id[0],'state':False}
		for c_ids in canceld_ids:
			res[c_ids[1]]={'id':c_ids[0],'state':True}
		invoices = [res_open, res_cancel ]
		resport_line = ''
		for res in invoices:
			inv_numbers = res.keys()
			inv_numbers.sort()
			for inv_numb in inv_numbers:
				try:
					attachment_id = attachment_obj.search(cr, uid, [('res_id','=', res[inv_numb]['id']),('res_model','=', 'account.invoice')])[0]
					xml_str = attachment_obj.browse(cr, uid, attachment_id).datas
					xml_str = base64.decodestring(xml_str)
					xml_str = unicode(xml_str, 'utf-8')
					xml_obj = StringIO.StringIO(xml_str.encode('utf-8'))
					xml_str_obj = etree.parse(xml_obj)
					line = pool.get('account.invoice').cfdutil_getLineaReporte(xml_str_obj, res[inv_numb]['state'])
					resport_line += line +'\n'
				except IndexError:
					raise osv.except_osv(('Warrnig !'), ('Check the XML file for the invoice %s.'%inv_numb))
		return resport_line

	
##	def _reporte(self, cr, uid, rfc, mes, agnio):
##		pool = pooler.get_pool(cr.dbname)
##		attachment_obj = pool.get('ir.attachment')
##		date_from = "%s-%s-01 00:00:00"%(agnio, mes)
##		date_to = last_day_of_month(datetime.date(agnio, mes, 1)).strftime('%Y-%m-%d 24:00:00')
##		query = "SELECT id, number from account_invoice where sign_date between '%s' and '%s' and state not in ('cancel', 'draft') order by number"%(date_from, date_to)
##		print 'query',query
##		cr.execute(query)
##		invoiced_ids = cr.fetchall()
##		print 'invoiced_ids',invoiced_ids
##		query = "SELECT id, number from account_invoice where cancel_date between '%s' and '%s'  order by number"%(date_from, date_to)
##		print 'query canceld_ids',query
##		cr.execute(query)
##		canceld_ids = cr.fetchall()
##		res = {}
##		for id in invoiced_ids:
##			res[id[1]]={'id':id[0],'state':False}
##		print 'canceld_ids',canceld_ids
##		for c_ids in canceld_ids:
##			res[c_ids[1]]={'id':c_ids[0],'state':True}
##		print 'res', res
##		inv_numbers = res.keys()
##		inv_numbers.sort()
##		print inv_numbers
##		resport_line = ''
##		for inv_numb in inv_numbers:
##			print 
##			attachment_id = attachment_obj.search(cr, uid, [('res_id','=', res[inv_numb]['id']),('res_model','=', 'account.invoice')])[0]
##			xml_str = attachment_obj.browse(cr, uid, attachment_id).datas
##			#print 'xml_str=', xml_str
##			#print 'xml', type(xml_str)
##			xml_str = base64.decodestring(xml_str)
##			xml_str = unicode(xml_str, 'utf-8')
##			print 'xml_str',xml_str
##			xml_obj = StringIO.StringIO(xml_str)
##			xml_str_obj = etree.parse(xml_obj)
##			line = pool.get('account.invoice').cfdutil_getLineaReporte(xml_str_obj, res[inv_numb]['state'])
##			print 'line',line
##			resport_line += line +'\n'

		
##		print 'resport_line',resport_line
##		return resport_line


	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		fiscalyear_obj = pool.get('account.fiscalyear')
		data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
		user = pool.get('res.users').browse(cr, uid, uid, context=context)
		if user.company_id:
			company_id = user.company_id.id
		else:
			company_id = pool.get('res.company').search(cr, uid,
					[('parent_id', '=', False)])[0]
		data['form']['company_id'] = company_id
		return data['form']

	states = {
	'init': {
		'actions': [_get_defaults],
		'result': {'type':'form', 
			'arch':dates_form, 
			'fields':dates_fields, 
			'state':[('end','Cancel'),('export','Export')]}
		},
        'export' : {
            	'actions' : [_get_report],
            	'result' : {'type' : 'form',
                        'arch' : export_form,
                        'fields' : export_fields,
                        'state' : [('close', 'Ok','gtk-ok') ]}
        },
        'close': {
            	'actions': [],
            	'result': {'type': 'state', 'state':'end'}
        }

    }
wizard_electronic_report_invoice('account.invoice.electronic.report')

