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
from tools.misc import UpdateableStr

def querytuplestr(mytuple):
	if len(mytuple) == 1:
		return str(mytuple).replace(",", "")
	else:
		return str(mytuple)

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


export_form = UpdateableStr()
export_fields = {}


def _get_report(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	fy_id = data['form']['fiscalyear']
	pe_id = data['form']['period']
	company_id = data['form']['company_id']
	agnio = int(pool.get('account.fiscalyear').browse(cr, uid, fy_id, context=context).date_start[:4])
	mes = int(pool.get('account.period').browse(cr, uid, pe_id, context=context).date_start[5:7])
	rfc = pool.get('res.company').browse(cr, uid, company_id, context).partner_id.vat
	rfc = re.sub('-','',rfc)
	res = file = self._reporte(cr, uid, rfc, mes, agnio)
	report_name = str('1%s%s%s.txt'%(rfc, mes, agnio))
	buf=StringIO.StringIO()
	writer=buf.write(res)
	out=base64.encodestring(buf.getvalue())
	buf.close()
	
	return {'note': res, report_name: out}

def last_day_of_month(date):
	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)	
	
	
class wizard_electronic_report_invoice(wizard.interface):


	def _reporte(self, cr, uid, rfc, mes, agnio):
		report_name = str('1%s%s%s.txt'%(rfc, mes, agnio))
		export_form.string = '''<?xml version="1.0"?><form string="Payment Export"> <field name="%s"/><field name="note" colspan="4" height="300" width="800" nolabel="1"/></form>'''%(report_name)
		export_fields[report_name] = {
			'string':'Export File',
			'type':'binary',
			'required': False,
			'readonly':True,
			}
		export_fields['note'] = {'string':'Log','type':'text'}

		pool = pooler.get_pool(cr.dbname)
		attachment_obj = pool.get('ir.attachment')
		date_from = "%s-%s-01 00:00:00"%(agnio, mes)
		date_to = last_day_of_month(datetime.date(agnio, mes, 1)).strftime('%Y-%m-%d 24:00:00')
		cr.execute("SELECT id FROM account_journal WHERE e_invoice = 'True'")
		journal_id = cr.fetchall()
		journal_id = tuple([id[0] for id in  journal_id])
		if len(journal_id) <= 1:
			journal_query = 'journal_id = %s'%journal_id[0]
		else:
			journal_query = 'journal_id in %s'%str(journal_id)
		query = "SELECT id, number, move_id, account_id, type FROM account_invoice WHERE sign_date between '%s' and '%s' and state not in ('proforma','proforma2', 'draft') and %s order by number"%(date_from, date_to, journal_query)
		cr.execute(query)
		invoiced_ids = cr.fetchall()
		query = "SELECT id, number, move_id, account_id, type FROM account_invoice WHERE cancel_date between '%s' and '%s'  and %s   order by number"%(date_from, date_to, journal_query)
		cr.execute(query)
		canceld_ids = cr.fetchall()
		for ix in range(len(invoiced_ids)):
			item = invoiced_ids[ix]
			query = "SELECT distinct(account_id) FROM account_invoice_line WHERE invoice_id=%i" %(item[0], )
			cr.execute(query)
			acctlist = querytuplestr(tuple([x[0] for x in cr.fetchall()]))
			if item[4] == "out_invoice":
				credit_debit = "credit"
				collected_paid = "account_collected_id"
			elif item[4] == "out_refund":
				credit_debit = "debit"
				collected_paid = "account_paid_id"
			else:
				####Esta mal el tipo de factura...
				item[2] = None
			query = "SELECT SUM(aml.%s) FROM account_move_line aml," %(credit_debit, )
			query += " account_tax at, account_tax_code atc, account_invoice ai, account_invoice_tax ait"
			query += " WHERE ai.id=%i AND ai.move_id=aml.move_id" %(item[0], )
			query += " AND aml.account_id=at.%s" %(collected_paid, )
			query += " AND  (ait.tax_code_id = at.tax_code_id OR ait.tax_code_id = at.ref_tax_code_id)"
			query += " AND ait.invoice_id=ai.id"
			query += " AND atc.tax_type in ('tax_iva', 'tax_ietu')"
			cr.execute(query)
			tax = cr.fetchall()
			if not item[2]:
				invoiced_ids[ix] = tuple(item + (0.0,) + (0.0,) + ('ERROR',))
			else:
				query = "SELECT SUM(%s) FROM account_move_line WHERE move_id=%i and account_id in %s" %(credit_debit, item[2], acctlist)
				cr.execute(query)
				sums = cr.fetchall()
				invoiced_ids[ix] = tuple(item + sums[0] + tax[0])
		for ix in range(len(canceld_ids)):
			item = canceld_ids[ix]
			query = "SELECT distinct(account_id) FROM account_invoice_line WHERE invoice_id=%i" %(item[0], )
			cr.execute(query)
			acctlist = querytuplestr(tuple([x[0] for x in cr.fetchall()]))
			if item[4] == "out_invoice":
				credit_debit = "credit"
				collected_paid = "account_collected_id"
			elif item[4] == "out_refund":
				credit_debit = "debit"
				collected_paid = "account_paid_id"
			else:
				####Esta mal el tipo de factura...
				item[2] = None
			query = "SELECT SUM(aml.%s) FROM account_move_line aml," %(credit_debit, )
			query += " account_tax at, account_tax_code atc, account_invoice ai, account_invoice_tax ait"
			query += " WHERE ai.id=%i AND ai.move_id=aml.move_id" %(item[0], )
			query += " AND aml.account_id=at.%s" %(collected_paid, )
			query += " AND  (ait.tax_code_id = at.tax_code_id OR ait.tax_code_id = at.ref_tax_code_id)"
			query += " AND ait.invoice_id=ai.id"
			query += " AND atc.tax_type in ('tax_iva', 'tax_ietu')"
			cr.execute(query)
			tax = cr.fetchall()
			if not item[2]:
				canceld_ids[ix] = tuple(item + (0.0,) + (0.0,) + ('ERROR',))
			else:
				query = "SELECT SUM(%s) from account_move_line WHERE move_id=%i and account_id in %s" %(credit_debit, item[2], acctlist)
				cr.execute(query)
				sums = cr.fetchall()
				canceld_ids[ix] = tuple(item + sums[0] + tax[0])
		res_open = {}
		res_cancel = {}
		for id in invoiced_ids:
			if (len(id) == 8) and (id[7] == 'ERROR'):
				res_open[id[1]]={'id':id[0],'state':False, 'subtotal_valuestr': '%.2f' %(id[5] or 0.0, ), 'tax_valuestr': '%.2f' %(id[6] or 0.0, ), 'ERROR':True}
			else:
				res_open[id[1]]={'id':id[0],'state':False, 'subtotal_valuestr': '%.2f' %(id[5] or 0.0, ), 'tax_valuestr': '%.2f' %(id[6] or 0.0, ), 'ERROR':False}
		for c_ids in canceld_ids:
			if (len(c_ids) == 8) and (c_ids[7] == 'ERROR'):
				res_cancel[c_ids[1]]={'id':c_ids[0],'state':True, 'subtotal_valuestr': '%.2f' %(c_ids[5] or 0.0, ), 'tax_valuestr': '%.2f' %(c_ids[6] or 0.0, ),'ERROR':True}
			else:
				res_cancel[c_ids[1]]={'id':c_ids[0],'state':True, 'subtotal_valuestr': '%.2f' %(c_ids[5] or 0.0, ), 'tax_valuestr': '%.2f' %(c_ids[6] or 0.0, ),'ERROR':False}
		invoices = [res_open, res_cancel ]
		report_line = ''
		for res in invoices:
			inv_numbers = res.keys()
			inv_numbers.sort()
			for inv_numb in inv_numbers:
				try:
					attachment_id = attachment_obj.search(cr, uid, [('res_id','=', res[inv_numb]['id']),('res_model','=', 'account.invoice'),('datas_fname','ilike', '%.xml'),('name','not ilike', '%.old')])[0]
					xml_str = attachment_obj.browse(cr, uid, attachment_id).datas
					xml_str = base64.decodestring(xml_str)
					xml_str = unicode(xml_str, 'utf-8')
					xml_obj = StringIO.StringIO(xml_str.encode('utf-8'))
					xml_str_obj = etree.parse(xml_obj)
					line = pool.get('account.invoice').cfdutil_getLineaReporte(xml_str_obj, res[inv_numb]['state'],
												   res[inv_numb]['subtotal_valuestr'],
												   res[inv_numb]['tax_valuestr'])
					if res[inv_numb]['ERROR']:
						report_line += line + '********** REVISAR MANUALMENTE %s *********'%(inv_numb) + '\n'
					else:
						report_line += line +'\n'
					#report_line += line +'\n'
				except IndexError:
					report_line += '-------- NO HAY ARCHIVO XML DEL FOLIO %s -----------'%(inv_numb) + '\n'
 				except etree.XMLSyntaxError:
 					report_line += '-------- ERROR EN ARCHIVO XML DEL FOLIO %s -----------'%(inv_numb) + '\n'
					
		return report_line

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

