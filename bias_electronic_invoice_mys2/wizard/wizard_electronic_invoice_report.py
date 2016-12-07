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
from lxml.builder import ElementMaker
from lxml import etree
import SOAPpy
import re

import StringIO
import csv


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


def _get_report(self,cr,uid,data,context):
	pool = pooler.get_pool(cr.dbname)
	fy_id = data['form']['fiscalyear']
	pe_id = data['form']['period']
	company_id = data['form']['company_id']
	ano = int(pool.get('account.fiscalyear').browse(cr, uid, fy_id, context=context).date_start[:4])
	mes = int(pool.get('account.period').browse(cr, uid, pe_id, context=context).date_start[5:7])
	rfc = pool.get('res.company').browse(cr, uid, company_id, context=context).partner_id.vat
	rfc = re.sub('-','',rfc)
	res = file = self._reporte(rfc,mes,ano)
	buf=StringIO.StringIO()
	writer=buf.write(res)
	out=base64.encodestring(buf.getvalue())
	buf.close()
	
	return {'note': res, 'report': out}
	
	
	
class wizard_electronic_report_invoice(wizard.interface):
	def _reporte(self, rfc, mes, ano):
		E = ElementMaker(namespace="http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2", 
				 nsmap={
					 'soapenv':"http://schemas.xmlsoap.org/soap/envelope/", 
					 'ns':"http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2"},)
		
		DOC = E.RequestReporteMensual
		reporte = DOC({'rfcEmisor':rfc, 'mes':str(mes), 'anio':str(ano)})
		reporte_xml = etree.tostring(reporte)
		reporte_xml = '<?xml version="1.0" encoding="UTF-8"?>' + reporte_xml
		util = SOAPpy.WSDL.Proxy("CorporativoWS2.2.wsdl")
		reporte = util.GeneraReporteMensual(reporte_xml)
		return reporte

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

