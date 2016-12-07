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
from mx.DateTime import *
import datetime
from lxml import etree
import os
import tools


invoices_form = '''<?xml version="1.0"?>
<form string="Select the invoices to ReGenerate"  width="800" height="250" >
	<field name="invoice_ids" domain = "[('state','in',('open','paid')), ('type', 'in', ('out_invoice','out_refund'))]"  width="800" height="250"  />
	<field name="keep_date" />
</form>'''


invoices_fields = {
	'invoice_ids': {'string': 'Invoices', 'type': 'many2many', 'relation': 'account.invoice',},
	'keep_date': {'string': 'Keep same Date?', 'type': 'boolean', }
}

done_form = '''<?xml version="1.0"?>
<form string="Regeneration Done!!!">
<separator string="Regeneration Done!!!"/>
</form>'''

done_fields = {}




class wizard_redo_einvoice(wizard.interface):


	def _get_new_xml(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		invoice_obj = pool.get('account.invoice')
		attach_obj = pool.get('ir.attachment')
		context = {}
		for inv_id in data['ids']:
			if not data['form']['keep_date']:
				context = {}
			else:
				date = invoice_obj.browse(cr, uid, inv_id).sign_date
				date = date.split(' ')
				same_date = date[0] + 'T' + date[1]
				context['date'] = same_date
			cfe= invoice_obj.create_xml(cr, uid, [inv_id], context)
			cfe_str = etree.tostring(cfe, pretty_print=True, encoding='utf-8')
			attachment_ids = attach_obj.search(cr, uid, [('res_id','=',inv_id),('res_model','=', 'account.invoice')])
			attach_brw_ids = attach_obj.browse(cr, uid, attachment_ids)
			for attach_brw in attach_brw_ids:
				attach_name = attach_brw.name
				attach_name = attach_name + '.old'
				query = "UPDATE ir_attachment set name='%s' where id=%s"%(attach_name, attach_brw.id)
				cr.execute("UPDATE ir_attachment set name='%s' where id=%s"%(attach_name, attach_brw.id))
			invoice_obj.attach_xml(cr, uid, inv_id, cfe_str)
		return {}

	def _get_defaults(self, cr, uid, data, context):
		data['form'] = {'invoice_ids': data['ids']}
		return data['form']

	def _get_all_md5(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		cr.execute("SELECT id from account_invoice where sign_date between '2010-01-01 00:00:00' and '2011-03-01 00:00:00'")
		all_ids = cr.fetchall()
		all_ids = [a[0] for a in all_ids]
		ids = []
		for inv_brw in pool.get('account.invoice').browse(cr, uid, all_ids):
			cadena = inv_brw.cadena
			sello = inv_brw.digital_signature
			certfname = inv_brw.company_id.certificate
			verify = pool.get('account.invoice').cfdutil_verifySello(cadena, certfname, sello)
			if verify:
				ids.append(inv_brw.id)
		data['form'] = {'invoice_ids': ids}
		return data['form']


	states = {
		'init': {
			'actions': [_get_defaults],
			'result': {'type':'form', 
				   'arch':invoices_form, 
				   'fields':invoices_fields, 
				   'state':[('end','Cancel'),('md5','MD5 to SHA1'),('export','Export')]}
			},
		'export' : {
			'actions' : [_get_new_xml],
			'result' : {'type' : 'form',
				    'arch' : done_form,
				    'fields' : done_fields,
				    'state' : [('close', 'Ok','gtk-ok') ]}
			},
		'md5': {
			'actions': [_get_all_md5],
			'result': {'type':'form', 
				   'arch':invoices_form, 
				   'fields':invoices_fields, 
				   'state':[('end','Cancel'),('md5','MD5 to SHA1'),('export','Export')]}
			},
		'close': {
			'actions': [],
			'result': {'type': 'state', 'state':'end'}
			}
		
		}
wizard_redo_einvoice('account.invoice.redo.einvoice')

