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
import StringIO
import base64
import re

pay_form = '''<?xml version="1.0"?>
<form string="Print Cheque">
    	<field name="amount"/>
    	<field name="balance"/>date_prefered
    	<field name="date"/>
    	<field name="journal_id"/>
	<field name="period_id"/>
	<field name="grouped" />
        <separator string="File" colspan="4"/>
    	<field name="file"/>
        <field name="view" colspan="4" height="300" width="800" nolabel="1"/>

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
	'file': {'string': 'File', 'type': 'binary', 'help': 'File created for this payment', 'readonly':True},
	'view': {'string': 'File Preview', 'type': 'text', 'help': 'File created for this payment', 'readonly':False},

}


class wizard_export_create(wizard.interface):

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

	def _check_required(self, cr, uid, exp_field, line, payment):
		currency_source = str(payment.mode.journal.currency.id or line.company_currency.id)
		currency_dest = str(payment.mode.journal.currency.id or line.company_currency.id)
		tax = ''
		vat = line.order_id.user_id.company_id.partner_id.vat
        	field_value = exp_field.std_field and eval(exp_field.std_field)
		if exp_field.type == 'date':
			field_value = eval(exp_field.std_field) or time.strftime('%Y-%m-%d')
	        if field_value or not exp_field.required:
	        	return
	        if not exp_field.condition:
		        raise wizard.except_wizard(_('Error !'), _("The field '%s' is required!") % (exp_field.name,))
		con = eval(exp_field.condition)+' '+exp_field.operator+' '+str(eval(exp_field.value))
	        if eval(con):
		        raise wizard.except_wizard(_('Error !'), _("The field '%s' is required!") % (exp_field.name,))
	        return

	def process_defaults(self, cr, uid, exp_field, line, payment, amount, com):
		now = time.strftime('%Y-%m-%d')
		currency_source = str(payment.mode.journal.currency.id or line.company_currency.id)
		currency_dest = str(payment.mode.journal.currency.id or line.company_currency.id)
		tax = ''
		vat = line.order_id.user_id.company_id.partner_id.vat
		value = eval(exp_field.std_field)
	        field_value = exp_field.std_field and value
	        field_length = exp_field.length and (eval(str(exp_field.length)))
	        zero = exp_field.zero
	        field_type = exp_field.type
		format = exp_field.export_id.date
		number = exp_field.export_id.number
		if exp_field.std_field == 'line.partner_id.name':	
			field_value = re.sub('[^a-zA-Z0-9 ]','',field_value)
		if exp_field.std_field == 'vat':
			field_value = re.sub('-','',field_value)
		if field_type == 'date':
			field_value = field_value or now
			if format == 'ddmmyyyy':
				field_value = time.strftime('%d%m%Y', time.strptime(field_value,'%Y-%m-%d'))
			if format == 'mmddyyyy':
				field_value = time.strftime('%m%d%Y', time.strptime(field_value,'%Y-%m-%d'))
			if format == 'YYYYMMDD':
				field_value = time.strftime('%Y%m%d', time.strptime(field_value,'%Y-%m-%d'))
		if exp_field.std_field == 'line.communication':
		    field_value = com or field_value
		    field_value = re.sub('[^a-zA-Z0-9]','',field_value)
		if field_value:
	        	field_value = str(field_value)[0:field_length]
	        if field_type == 'integer':
		    if value:
	            	try:
				field_value = str(int(field_value))
	        	except:
		        	raise wizard.except_wizard(_('Error !'), _("The field '%s' must be numeric!") % (exp_field.name,))
	        if field_type == 'float':
		    if exp_field.std_field == 'line.amount':
		    	value = amount or value
		    if value:
		    	n = '1' + '0' * int(number)
	            	try:
				field_value = str(int(float(value)*int(n)))
	            	except:
		        	raise wizard.except_wizard(_('Error !'), _("The field '%s' must be numeric!") % (exp_field.name,))
		length = field_value and len(field_value) or 0
	        if zero == 'left' and length < field_length:                    #add 0 to the left
	            field_value = '0'*(field_length - length) + (field_value or '')
	        if zero == 'rigth' and length < field_length:                    #add 0 to the rigth
	            field_value = (field_value or '') + '0'*(field_length - length)
	        if zero == 'sleft' and length < field_length:                    #add ' ' (space) to the left
	            field_value = ' '*(field_length - length) + (field_value or '')
	        if zero == 'srigth' and length < field_length:                    #add ' ' (space) to the rigth
	            field_value = (field_value or '') + ' '*(field_length - length)
	        return str(field_value)

	def _process_text(self, cr, uid, exp_field, line, payment, value, com):
		pool = pooler.get_pool(cr.dbname)
	        self._check_required(cr, uid, exp_field, line, payment)
		return self.process_defaults(cr, uid, exp_field, line, payment, value, com)
		
	def _get_text(self, cr, uid, lines_id, payment):
		lin_obj = pooler.get_pool(cr.dbname).get('payment.line')
		amount = False
		com = False
		for l in lines_id:
			text_line = ''
			line = lin_obj.browse(cr, uid, l)
			for exp_field in payment.mode.payment_export_id.line_id:
				if exp_field.std_field == 'line.communication':
					com =  line.name+'  '+ line.communication
				if exp_field.std_field == 'line.amount':
					amount += eval(exp_field.std_field)
				text_line += self._process_text(cr, uid, exp_field, line, payment, amount, com)
			if not line.cost_center_id:
        			raise wizard.except_wizard(_('Error !'), _("Cost Center field is missing in one of the payment lines!"))
		return text_line

	def _get_view(self, cr, uid, lines_id, payment, partner_id, text, view, context):
		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		lin_obj = pool.get('payment.line')
		text_line = self._get_text(cr, uid, lines_id, payment) #
		text += text_line + '\n'
		view += str(len(text_line))+'     '+text_line[0:2]+'   '+text_line[55:67]+'.'+text_line[67:69]+'   '+text_line[109:110]+'   '+text_line[110:111]+'     '+text_line[111:124]+'  '+text_line[79:109]+'   '+pool.get('res.partner').browse(cr, uid, partner_id).name+'\n'
		return view, text

	def _create_file(self, cr, uid, data, context):
		for line in pooler.get_pool(cr.dbname).get('payment.order').browse(cr, uid, data['id'], context).line_ids:
			if not line.cost_center_id:
				raise wizard.except_wizard(_('Error !'), _("Cost Center field is missing in one of the payment lines!"))
			if not (line.operation and line.code_id and line.bank_id):
				raise wizard.except_wizard(_('Error !'), _("Some field are missing in one of the payment lines!"))
		pool = pooler.get_pool(cr.dbname)
		pay_obj, lin_obj = pool.get('payment.order'), pool.get('payment.line')
    		payment   = pay_obj.browse(cr, uid, data['id'], context)
		lines_ids = pay_obj.read(cr, uid, data['id'], [('line_ids')])['line_ids']
		lines     = tuple(lines_ids)
		res, text, view = {}, '', 'Long. Oper        Importe           M1 M2  R.F.C.                   Ref/Comunicacion              Empresa\n'
		partners = self._get_partners(cr, uid, lines, context)
		context['period_id'] = data['form']['period_id']
		if payment.state == 'done':
			view, text = self._get_text_view(cr, uid, lines, payment, partners, view, context)
			out = self._make_file(cr, uid, text + '\n')
			res['file'], res['view']  = out, view
			return res 
		for part in partners:
			remove = []
			partner_id = part['partner_id']
#			print 'partner=',pool.get('res.partner').browse(cr, uid, partner_id).name
			all_lines_id = lin_obj.browse(cr, uid, map(lambda x: x[0], self._get_lines(cr, uid, lines, partner_id, context)))
			lines_id = []
			for l in all_lines_id:
				if l['move_line_id'] and len(l['move_line_id'].move_id.line_id) == 2:
					for t in l['move_line_id'].move_id.line_id:
						if t.account_id.user_type.code == 'tax':
							lines_id.append(l.id)
							remove.append(l)
#			print 'lineas de orden 0 tax 1% =',lines_id
			if lines_id:
				for l in remove:
					all_lines_id.remove(l)
				self._create_move(cr, uid, lines_id, context)
			lines_id = [x.id for x in filter(lambda x: x['move_line_id'] and not x['partial'], all_lines_id)]
#			print 'lineas de orden asiento y pago completo =',lines_id
			if lines_id:
				[all_lines_id.remove(x) for x in lin_obj.browse(cr, uid, lines_id)]
				self._create_move(cr, uid, lines_id, context)
			lines_id = [x.id for x in filter(lambda x: x['move_line_id'] and x['partial'], all_lines_id)]
#			print 'lineas de orden asiento y pago parcial =',lines_id
			if lines_id:
				[all_lines_id.remove(x) for x in lin_obj.browse(cr, uid, lines_id)]
				for line_id in lines_id:
					self._create_move(cr, uid, lines_id, context)
			lines_id = [x.id for x in filter(lambda x: not x['move_line_id'], all_lines_id)]
#			print 'lineas de orden sin asiento =',lines_id
			if lines_id:
				self._create_move(cr, uid, lines_id, context)
		pay_obj.write(cr, uid, data['id'], {'state': 'done','date_done': time.strftime('%Y-%m-%d')})
		self._consolidate_moves(cr, uid, partners, lines, data['id'], context)
		view, text = self._get_text_view(cr, uid, lines, payment, partners, view, context)
		out = self._make_file(cr, uid, text + '\n')
		res['file'], res['view']  = out, view
		return res 

	def _get_text_view(self, cr, uid, lines, payment, partners, view, context):
		text = ''
		for part in partners:
			cr.execute("SELECT id FROM payment_line WHERE id in %s AND partner_id = %s", (lines, part['partner_id']))
			lines_id = [x[0] for x in cr.fetchall()]
			view, text = self._get_view(cr, uid, lines_id, payment, part['partner_id'], text, view, context)
		return view, text

	def _create_move(self, cr, uid, lines_id, context):
		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		lin_obj = pool.get('payment.line')
        	move_id = chk_obj.action_open(cr, uid, False, lines_id, context) #
		cr.execute("UPDATE payment_line      SET move_id = %s WHERE id in %s", (move_id, tuple(lines_id)))
		return

	def _consolidate_moves(self, cr, uid, partners, lines, payment_id, context):
		pool = pooler.get_pool(cr.dbname)
		for part in partners:
			cr.execute("SELECT id FROM payment_line WHERE id in %s AND partner_id = %s", (lines, part['partner_id']))
			pay_lines_ids = [x[0] for x in cr.fetchall()]
			cr.execute("SELECT distinct(move_id) FROM payment_line WHERE id in %s AND partner_id = %s", (lines, part['partner_id']))
			move_ids = [x[0] for x in cr.fetchall()]
			cr.execute("SELECT id FROM account_move_line WHERE move_id in %s", (tuple(move_ids),))
			line_ids = [x[0] for x in cr.fetchall()]
			cr.execute("UPDATE payment_line      SET move_id = %s WHERE id in %s", (move_ids[0], tuple(pay_lines_ids)))
			cr.execute("UPDATE account_move      SET type = 'bank_pay_voucher' WHERE id = %s", (move_ids[0],))
			cr.execute("UPDATE account_move_line SET move_id = %s WHERE id in %s", (move_ids[0], tuple(line_ids)))
			cr.execute("select count(id) as count, sum(debit) as debit, sum(credit) as credit, "
				"max(account_id) as account_id, max(id) as id "
				"from account_move_line where move_id = %s and account_id = "
				"(select j.default_debit_account_id from payment_order p left join payment_mode m on (p.mode = m.id) "
				"left join account_journal j on (m.journal = j.id) where p.id = %s) ", (move_ids[0], payment_id,))
			r = cr.dictfetchall()
			if r[0]['count'] > 1:
				cr.execute("UPDATE account_move_line SET debit = %s, credit = %s WHERE id = %s", (r[0]['debit'],r[0]['credit'],r[0]['id']))
				cr.execute("DELETE FROM account_move_line WHERE move_id = %s and account_id = %s and id <> %s ", \
				(move_ids[0], r[0]['account_id'], r[0]['id']))
				move_ids.remove(move_ids[0])
				cr.execute("DELETE FROM account_move WHERE id in %s ", (tuple(move_ids),))
		cr.execute("SELECT move_id FROM payment_line WHERE id in %s ", (lines,))
		move_ids = [x[0] for x in cr.fetchall()]
		pool.get('account.move').post(cr, uid, move_ids)
		return

	def _make_file(self, cr, uid, text):
		buf=StringIO.StringIO()
		writer=buf.write(text)
		out=base64.encodestring(buf.getvalue())
		buf.close()
		return out

	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		period_obj = pool.get('account.period')
		chk_obj = pool.get('payment.cheque')
		pay_obj = pool.get('payment.order')
		fiscalyear_obj = pool.get('account.fiscalyear')
		fiscalyear = fiscalyear_obj.find(cr, uid)
		context['fiscalyear'] = fiscalyear
		ids = period_obj.find(cr, uid, context=context)
    		payment = pay_obj.browse(cr, uid, data['id'], context)
		period_id = False
		text = ''
		if payment.date_prefered == 'fixed':
			period_id = period_obj.find(cr, uid, payment.date_planned, context=context)[0]
    		elif len(ids):
        		period_id = ids[0]
		if payment.state == 'open' and payment.mode.payment_export_id:
			for line in payment.line_ids:
				if not line.cost_center_id:
	        			raise wizard.except_wizard(_('Error !'), _("Cost Center field is missing in one of the payment lines!"))
				if not (line.operation and line.code_id and line.bank_id and line.communication and (line.partner_id and line.partner_id.vat)):
					if not text:
						text += '                 Referencia   Error\n'
					if not (line.operation):
						text += 'ERROR !!!     ' + str(line.name) + '          Oper'+ '\n'
					if not (line.code_id):
						text += 'ERROR !!!     ' + str(line.name) + '          Codigo'+ '\n'
					if not (line.bank_id):
						text += 'ERROR !!!     ' + str(line.name) + '          Cuenta de Banco'+ '\n'
					if not (line.communication):
						text += 'ERROR !!!     ' + str(line.name) + '          Comunicacion'+ '\n'
					if not (line.partner_id.vat):
						partner = line.partner_id and line.partner_id.name 
						text += 'ERROR !!!     ' + str(line.name) + '          R.F.C.  '+ partner +'\n'
		cheques = chk_obj.search(cr, uid, [('payment_order_id','=',payment.id)])
		if not payment.mode.payment_export_id:
			raise wizard.except_wizard(_('Error !'), 
				_("The payment mode '%s' has not defined export file!") % (payment.mode.name,))
		if payment.state == 'done' and cheques:
			raise wizard.except_wizard(_('Error !'), 
					_("The payment order '%s' has not file to export!") % (payment.reference,))
    		if payment.date_prefered in ['now','due']:
        		date = time.strftime('%Y-%m-%d')
    		elif payment.date_prefered == 'fixed':
        		date = payment.date_planned

    		return {
        		'period_id': period_id,
        		'journal_id': payment.mode.journal.id,
        		'amount': payment.total,
        		'balance': payment.mode.balance_account_id.balance,
        		'date': date,
			'view': text,
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
					('create', 'Create File')
				]
			}
		},
		'create': {
			'actions': [_create_file],
			'result': {
				'type': 'form',
				'arch': pay_form,
				'fields': pay_fields,
				'state': [
					('end', 'OK'),
				]
			}
		},
	}

wizard_export_create('payment.create.export')

