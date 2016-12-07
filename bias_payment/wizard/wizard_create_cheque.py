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
    	<field name="balance"/>date_prefered
    	<field name="date"/>
    	<field name="journal_id"/>
        <group col="6" colspan="4">
    		<field name="period_id"/>
    		<field name="grouped" />
    		<field name="auto" />
        </group>
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
	'cheque': {'string': 'Cheques', 'type': 'one2many', 'relation': 'payment.cheque', 'help': 'Cheques of this payment', 'readonly':True},

}


class wizard_cheque_create(wizard.interface):

    	def _get_partners(self, cr, uid, lines, context):
		query = 'in'
		if len(lines) == 1:
			query = '='
			lines = lines[0]
		cr.execute("SELECT DISTINCT partner_id " \
			"FROM payment_line AS line " \
			"WHERE line.id "+query+" %s", (lines,))
		return cr.dictfetchall()

    	def _get_amount(self, cr, uid, lines, partner_id, context):
		query = 'in'
		if len(lines) == 1:
			query = '='
			lines = lines[0]
		cr.execute("SELECT SUM (amount_currency) " \
			"FROM payment_line AS line " \
			"WHERE line.id "+query+" %s "
			"AND line.partner_id = %s", (lines, partner_id,))
		return cr.fetchone()[0]

    	def _get_lines(self, cr, uid, lines, partner_id, context):
		query = 'in'
		if len(lines) == 1:
			query = '='
			lines = lines[0]
		cr.execute("SELECT id " \
			"FROM payment_line AS line " \
			"WHERE line.id "+query+" %s "
			"AND line.partner_id = %s", (lines, partner_id))
		return cr.fetchall()

	def _create_cheque(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		pay_obj = pool.get('payment.order')
		lin_obj = pool.get('payment.line')
		part_obj = pool.get('res.partner')
    		payment = pay_obj.browse(cr, uid, data['id'], context)
		cheques = chk_obj.search(cr, uid, [('payment_order_id','=',payment.id)])
		if cheques:
			return {'cheque': cheques }

    		if payment.date_prefered in ['now','due']:
        		date = time.strftime('%Y-%m-%d')
    		elif payment.date_prefered == 'fixed':
        		date = payment.date_planned
		lines_ids = pay_obj.read(cr, uid, data['id'], [('line_ids')])['line_ids']
		lines = tuple(lines_ids)
		cheques = []
		if data['form']['grouped']:
			partners = self._get_partners(cr, uid, lines, context)
			for part in partners:
				partner_id = part['partner_id']
				lines_id = self._get_lines(cr, uid, lines, partner_id, context)
				ln = []
				for l in lines_id:
					lb = lin_obj.browse(cr, uid, l[0])
					if not lb.cost_center_id:
		        			raise wizard.except_wizard(_('Error !'), _("Cost Center field is missing in one of the payment lines!"))
					name = lb.ml_inv_ref.number or lb.move_line_id.move_id.name
		                	l = {
        			        'amount': lb.amount,
        			        'account_id': lb.move_line_id.account_id.id,
        			        'name': name,
					'pay_line_id': lb.id,
					'cost_center_id': lb.cost_center_id.id,
					'move_line_id': lb.move_line_id.id,
        		        	}
        		        	ln.append((0,0,l))
    				cheque = {
					'concept': lb.communication,
					'user_id': payment.user_id.id,
					'mode': payment.mode.id,
					'line_id': ln,
					'period_id': data['form']['period_id'],
					'date': date,
					'partner_id': partner_id,
					'payment_order_id': data['id'],
		    		}
            			cheque_id = chk_obj.create(cr, uid, cheque)
				chk_obj.action_confirm(cr, uid, [cheque_id])
				cheques.append(cheque_id)
				if data['form']['auto']:
					move_id = chk_obj.action_open(cr, uid, [cheque_id])
					for l in lines_id:
						lin_obj.write(cr,uid,l[0],{'move_id': move_id})				
		else:
			for pay in lin_obj.browse(cr, uid, lines_ids):
				partner_id = pay.partner_id
				lb = lin_obj.browse(cr, uid, pay.id)
	                	l = {
	       			        'amount': lb.amount,
       				        'account_id': lb.move_line_id.account_id.id,
       				        'name': name,
					'pay_line_id' : lb.id,
					'cost_center_id': lb.cost_center_id.id,
       		        	}
    				cheque = {
					'concept': lb.communication,
					'user_id': payment.user_id.id,
					'mode': payment.mode.id,
					'line_id': (0,0,l),
					'period_id': data['form']['period_id'],
					'date': date,
					'partner_id': partner_id,
					'payment_order_id': data['id'],
		    		}
            			cheque_id = chk_obj.create(cr, uid, cheque)
				chk_obj.action_confirm(cr, uid, [cheque_id])
				cheques.append(cheque_id)
				if data['form']['auto']:
					move_id = chk_obj.action_open(cr, uid, [cheque_id])
					lin_obj.write(cr,uid,pay.id,{'move_id': move_id})
		res = self._get_defaults(cr, uid, data, context)
		res['cheque'] = cheques
		pay_obj.write(cr,uid,data['id'],{'state': 'done','date_done': time.strftime('%Y-%m-%d')})
		return res 

	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		period_obj = pool.get('account.period')
		chk_obj = pool.get('payment.cheque')
		pay_obj = pool.get('payment.order')
		fiscalyear_obj = pool.get('account.fiscalyear')
		fiscalyear = fiscalyear_obj.find(cr, uid)
		context['fiscalyear'] = fiscalyear
		ids = period_obj.find(cr, uid, context=context)
		period_id = False
    		if len(ids):
        		period_id = ids[0]
    		payment = pay_obj.browse(cr, uid, data['id'], context)
    		if payment.date_prefered in ['now','due']:
        		date = time.strftime('%Y-%m-%d')
    		elif payment.date_prefered == 'fixed':
        		date = payment.date_planned
		cheques = chk_obj.search(cr, uid, [('payment_order_id','=',payment.id)])

    		return {
        		'period_id': period_id,
        		'journal_id': payment.mode.journal.id,
        		'amount': payment.total,
        		'balance': payment.mode.balance_account_id.balance,
        		'date': date,
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
					('create', 'Create Cheque')
				]
			}
		},
		'create': {
			'actions': [_create_cheque],
			'result': {
				'type': 'form',
				'arch': pay_form,
				'fields': pay_fields,
				'state': [
					('end', 'OK'),
				]
			}
		},
		'report': {
			'actions': [],
			'result': {
				'type': 'print',
				'report': 'payment.cheque.print',
				'state':'end'
			}
		}
	}

wizard_cheque_create('payment.create.cheque')


