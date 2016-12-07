# -*- encoding: utf-8 -*-
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
import wizard
import pooler
import osv

pay_form = '''<?xml version="1.0"?>
<form string="Print Cheque">
    	<field name="amount"/>
    	<field name="journal_id"/>
        <separator string="Cheques" colspan="4"/>
        <field name="cheque" colspan="4" height="300" width="800" nolabel="1"/>

</form>'''

pay_fields = {
    	'amount': {'string': 'Amount to paid', 'type':'float', 'required':True},
    	'balance': {'string': 'Balance', 'type':'float', 'required':False},
    	'date': {'string': 'Payment date', 'type':'date', 'required':False, 'default':lambda *args: time.strftime('%Y-%m-%d')},
    	'journal_id': {'string': 'Journal/Payment Mode', 'type': 'many2one', 'relation':'account.journal', 'required':False, 'domain':[('type','=','cash')]},
    	'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period', 'required':False},
    	'grouped' : {'string':'Group by Partner', 'type':'boolean', 'default': lambda x,y,z:True},
    	'auto' : {'string':'Autovalidate', 'type':'boolean', 'default': lambda x,y,z:True},
    	'name': {'string': 'Entry Name', 'type':'char', 'size': 64, 'required':False},
    	'rml': {'string': 'RML', 'type':'char', 'size': 64, 'required':False},
	'cheque': {'string': 'Cheques', 'type': 'one2many', 'relation': 'payment.cheque', 'help': 'Cheques of this payment', 'readonly':False},

}


class wizard_cheques_print(wizard.interface):
	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		pay_obj = pool.get('payment.order')
    		payment = pay_obj.browse(cr, uid, data['id'], context)
		cheques = chk_obj.search(cr, uid, [('payment_order_id','=',payment.id)])
		if payment.state == 'done' and not cheques:
			raise wizard.except_wizard(_('Error !'), 
					_("The payment order '%s' has not cheques to print!") % (payment.reference,))
    		return {
        		'journal_id': payment.mode.journal.id,
        		'amount': payment.total,
        		'cheque': cheques,
    		}

	states = {
		'init': {
			'actions': [_get_defaults],
			'result': {
				'type': 'form',
				'arch': pay_form,
				'fields': pay_fields,
				'state': [
					('end', 'Cancel'),
					('report', 'Print Cheque')
				]
			}
		},
		'report': {
			'actions': [],
			'result': {
				'type': 'print',
				'report': 'payment.cheque.print_from_wizard_a',
				'state':'end'
			}
		}
	}

wizard_cheques_print('payment.print.cheque')

