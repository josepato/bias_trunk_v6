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

def _get_third_party_type(self, cr, uid, data, context={}):
    selection = pooler.get_pool(cr.dbname).get('res.partner')._third_party_type_get(cr, uid, context={})
    return selection 

def _tax_get(self, cr, uid, data, context={}):
    selection = pooler.get_pool(cr.dbname).get('account.tax.ietu.concept')._tax_get(cr, uid, context={})
    return selection 

form = '''<?xml version="1.0"?>
<form string="Tax Information">
    <group attrs="{'invisible':[('state','=','saved')]}" colspan="4">
        <label align="10.7" colspan="4" string="***** UNSAVED ******"/>
    </group>
    <group attrs="{'invisible':[('state','=','unsaved')]}" colspan="4">
        <label align="10.7" colspan="4" string="***** SAVED ******"/>
    </group>
        <group colspan="4" col="4" >
    	<field name="period_id"/>
        	<field name="diot"/>
        	<field name="serial"/>
        	<field name="folio"/>
        	<field name="reference"/>
        	<field name="move_id"/>
    	    <field name="entry_partner_id"/>
    	    <field name="entry_vat"/>
    	    <field name="tax_partner_id" on_change="onchange_partner_id(tax_partner_id)"/>
    	    <field name="tax_vat"/>
    	    <field name="property_account_position" colspan="4"/>
        </group>
    	<field name="third_party_type" colspan="4"/>
    	<field name="ietu"/>
    	<field name="ietu_concept"/>
    	<field name="base" on_change="onchange_amount(base, tax, amount, other, total)"/>
        <newline/>
    	<field name="tax" on_change="onchange_amount(base, tax, amount, other, total)"/>
        <label string="Amount - (Base - Tax)" align="20.0"/>
    	<field name="amount" on_change="onchange_amount(base, tax, amount, other, total)"/>
    	<field name="dif_amount"/>
    	<field name="other" on_change="onchange_amount(base, tax, amount, other, total)"/>
        <label string="Total - (Base + Tax + Other)" align="20.0"/>
    	<field name="total" on_change="onchange_amount(base, tax, amount, other, total)"/>
    	<field name="dif_total"/>
        <notebook colspan="4">
            <page string="Tax Lines">
            	<field name="tax_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1" on_change="onchange_tax(tax_lines, 'tax', amount, base, other, total)"/>
            </page>
            <page string="IETU Lines">
            	<field name="ietu_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"  on_change="onchange_tax(ietu_lines, 'ietu')"/>
            </page>
            <page string="amount Lines">
            	<field name="amount_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"/>
            </page>
            <page string="Base Lines">
            	<field name="base_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"/>
            </page>
            <page string="Other Lines">
            	<field name="other_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"/>
            </page>
            <page string="Total Lines">
            	<field name="total_lines" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"/>
            </page>
            <page string="Entries">
            	<field name="entries" height="200" colspan="4" context="move_id=move_id" default_get="{'move_id':move_id}" nolabel="1"/>
            </page>
        </notebook>

</form>'''

fields = {
    'diot': {'string': 'DIOT', 'type': 'boolean', 'default': lambda *a:False},
    'folio': {'string': 'Folio', 'type': 'char'},
    'state': {'string': 'State', 'type': 'char'},
    'serial': {'string': 'Serial', 'type': 'char'},
    'entry_vat': {'string': 'VAT', 'type': 'char', 'readonly': True},
    'tax_vat': {'string': 'VAT', 'type': 'char', 'readonly': True},
    'reference': {'string': 'reference', 'type': 'char', 'size': 64},
	'move_id': {'string': 'Entry', 'type': 'many2one', 'relation': 'account.move', 'readonly': True},
	'entry_partner_id': {'string': 'Entry Partner', 'type': 'many2one', 'relation': 'res.partner', 'readonly': True},
	'tax_partner_id': {'string': 'Tax Partner', 'type': 'many2one', 'relation': 'res.partner', 'required': True},
	'period_id': {'string': 'Fiscal Period', 'type': 'many2one', 'relation': 'account.period', 'readonly': True},
    'third_party_type':{'string':'Third Party Type', 'type':'selection', 'selection': _get_third_party_type},
    'ietu_concept':{'string':'IETU Concept', 'type':'selection', 'selection': _tax_get},
    'amount': {'string': 'Amount', 'type':'float', 'required':False, 'readonly':False},
    'base': {'string': 'Base', 'type':'float', 'required':False},
    'total': {'string': 'Total', 'type':'float', 'required':False},
	'tax': {'string': 'Tax', 'type': 'float'},
	'dif_amount': {'string': 'Diference', 'type': 'float'},
	'dif_total': {'string': 'Diference', 'type': 'float'},
    'ietu': {'string': 'IETU Deductible', 'type':'float', 'required':False, 'readonly':False},
    'other': {'string': 'Other', 'type':'float', 'required':False, 'readonly':False},
	'base_lines': {'string': 'Base Lines', 'type': 'one2many', 'relation': 'account.move.line', 'readonly':True},
	'amount_lines': {'string': 'Amount Lines', 'type': 'one2many', 'relation': 'account.move.line', 'readonly':True},
	'total_lines': {'string': 'Total Lines', 'type': 'one2many', 'relation': 'account.move.line', 'readonly':True},
	'other_lines': {'string': 'Other Lines', 'type': 'one2many', 'relation': 'account.move.line', 'readonly':True},
	'tax_lines': {'string': 'Tax Lines', 'type': 'one2many', 'relation': 'account.tax.fiscal'},
	'ietu_lines': {'string': 'Total IETU', 'type': 'one2many', 'relation': 'account.tax.ietu'},
	'entries': {'string': 'Entries', 'type': 'one2many', 'relation': 'account.move'},
    'property_account_position': {'string': 'Fiscal Position', 'type': 'many2one', 'relation': 'account.fiscal.position', 'readonly':True},
}

class wizard_account_entry_tax_info(wizard.interface):

    def _get_move_amount(self, cr, uid, move_ids, types, context={}):
        types = ','.join(map(str,[x.id for x in types])) 
        cr.execute('SELECT SUM(debit)-SUM(credit) FROM account_move_line l ' \
                    'LEFT JOIN account_account a ON (l.account_id = a.id) ' \
                    'LEFT JOIN account_account_type t ON (a.user_type = t.id) ' \
                    'WHERE l.move_id IN '+move_ids+' AND t.id IN ('+types+')' )
        return cr.fetchone()[0]

    def _get_move_amount_tax(self, cr, uid, move_ids, types, obj, context={}):
        types = ','.join(map(str,[x.id for x in types])) 
        cr.execute('SELECT SUM(debit)-SUM(credit) FROM account_move_line l ' \
                    'LEFT JOIN account_account a ON (l.account_id = a.id) ' \
                    'LEFT JOIN account_account_type t ON (a.user_type = t.id) ' \
                    'LEFT JOIN '+obj+' i ON (l.id = i.line_id) ' \
                    'WHERE l.move_id IN '+move_ids+' AND t.id IN ('+types+') AND i.active = True ' )
        res = cr.fetchone()[0]
        return res

    def _get_move_lines(self, cr, uid, move_ids, types, context={}):
        types = ','.join(map(str,[x.id for x in types])) 
        cr.execute('SELECT l.id FROM account_move_line l ' \
                    'LEFT JOIN account_account a ON (l.account_id = a.id) ' \
                    'LEFT JOIN account_account_type t ON (a.user_type = t.id) ' \
                    'WHERE l.move_id IN '+move_ids+' AND t.id IN ('+types+')' )
        return [x[0] for x in cr.fetchall()]

    def _get_move_ids(self, cr, uid, move, context={}):
        pool = pooler.get_pool(cr.dbname)
        move_ids = False
        type_bnk = filter(lambda x: x.account_id.user_type['code'] == 'cash', move.line_id)
        pay_rec = filter(lambda x: x.account_id['type'] in ('payable','receivable') and x.reconcile_id, move.line_id)
        if type_bnk and pay_rec:
            cr.execute("SELECT m.id FROM account_move_line l LEFT JOIN account_move m ON (l.move_id = m.id) WHERE l.reconcile_id IN " \
                        "(SELECT reconcile_id FROM account_move_line WHERE move_id = "+str(move.id)+") ")
            move_ids = [x[0] for x in cr.fetchall()]
        elif type_bnk:
            move_ids = [move.id, 0]
        elif pay_rec:
            cr.execute("SELECT m.name FROM account_move_line l LEFT JOIN account_move m ON (l.move_id = m.id) " \
                        "WHERE m.id <> "+str(move.id)+" AND l.reconcile_id IN " \
                        "(SELECT reconcile_id FROM account_move_line WHERE move_id = "+str(move.id)+") ")
            move_ids = [str(x[0]) for x in cr.fetchall()]
            raise wizard.except_wizard(_('Información'), _('El asiento esta conciliado con los asientos %s !')%move_ids)
        else:
            raise wizard.except_wizard(_('Error de Usuario'), _('El asiento debe ser de Ingresos o Egresos !'))
        return move_ids

    def _get_period(self, cr, uid, move, move_ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        period_id = False
        type_bnk = filter(lambda x: x.account_id.user_type['code'] == 'cash', move.line_id)
        pay_rec = filter(lambda x: x.account_id['type'] in ('payable','receivable') and x.reconcile_id, move.line_id)
        if type_bnk:# and pay_rec:
                cr.execute("SELECT MAX(period_id) FROM account_move_line l LEFT JOIN account_account a ON (l.account_id = a.id) " \
                        " WHERE move_id = "+str(move.id) )
                period_id = cr.fetchone()[0]
        return period_id

    def _get_folio(self, cr, uid, move_ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        folio = ''
        cr.execute("SELECT i.type, i.number, i.reference FROM account_move m LEFT JOIN account_invoice i ON (i.move_id = m.id) " \
                   " WHERE move_id IN "+move_ids)
        invoice = cr.dictfetchall()
        for inv in invoice:
            if inv['type'] in ('in_invoice'):
                ref = inv['reference']
            else:
                ref = inv['number']
            if folio == '':
                folio += ref
            else:
                folio += ', ' + ref
        return folio

    def _process_tax(self, cr, uid, data, label, move_ids, context):
        pool = pooler.get_pool(cr.dbname)
        tax_fiscal_obj = pool.get('account.tax.fiscal')
        tax_ietu_obj = pool.get('account.tax.ietu')
        par_obj = pool.get('account.tax.parameters')
        user = pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
           company_id = user.company_id.id
        else:
           company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        par = par_obj.search(cr, uid, [('company_id','=',company_id)])
        if not par:
            return form
        else:
            par = par[0]
        parameters = pool.get('account.tax.parameters').browse(cr, uid, par)
        parameters = pool.get('account.tax.parameters').browse(cr, uid, par)
        move = pool.get('account.move').browse(cr, uid, data['id'])
        cr.execute('SELECT id FROM account_move_line WHERE move_id IN '+move_ids)
        move_lines = pool.get('account.move.line').browse(cr, uid, [x[0] for x in cr.fetchall()])
        cr.execute('SELECT id FROM account_tax_fiscal WHERE move_id = '+str(data['id']))
        tax = [x[0] for x in cr.fetchall()]
        if not tax or label == 'regenerate':
            tax_fiscal_obj.unlink(cr, uid, tax)
            tax = []
            for account in parameters.tax:
                for line_id in move_lines:
                    if account.id == line_id.account_id.user_type.id:
                        xfer = False
                        for model in parameters.tax_model:
                            if model.tax == line_id.account_id.code:
                                xfer = model.xfer
                        value = {
                        'move_id': move.id,
                        'line_id': line_id.id,
                        'tax': line_id.account_id.code,
                        'xfer': xfer,
                        'amount': line_id.debit - line_id.credit,
                        'name': line_id.name,
                        'active': True,
                        }
                        tax.append(tax_fiscal_obj.create(cr, uid, value))
        cr.execute('SELECT id FROM account_tax_ietu WHERE move_id = '+str(data['id']))
        ietu = [x[0] for x in cr.fetchall()]
        if not ietu or label == 'regenerate':
            tax_ietu_obj.unlink(cr, uid, ietu)
            ietu = []
            for account in parameters.ietu:
                for line_id in move_lines:
                    if account.id == line_id.account_id.user_type.id:
                        value = {
                        'move_id': move.id,
                        'line_id': line_id.id,
                        'account_id': line_id.account_id.id,
                        'amount': line_id.debit - line_id.credit,
                        'name': line_id.name,
                        'active': True,
                        }
                        ietu.append(tax_ietu_obj.create(cr, uid, value))
        return tax, ietu, parameters

    def _get_defaults(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        form = data['form']
        move = pool.get('account.move').browse(cr, uid, data['id'])
        partner_id = move.line_id[0] and move.line_id[0].partner_id.id
        form['entries'] = [int(x) for x in self._get_move_ids(cr, uid, move)]
        move_ids = str(tuple(form['entries']))
        tax, ietu, parameters = self._process_tax(cr, uid, data, 'default', move_ids, context)
        meta_obj = pool.get('account.tax.meta')
        meta_id = meta_obj.search(cr, uid, [('move_id','=', data['id'])])
        meta = meta_id and meta_obj.browse(cr, uid, meta_id[0]) or False
        form['third_party_type'] = meta and meta.third_party_type or move.line_id[0].partner_id.third_party_type
        form['ietu_concept'] = meta and meta.ietu_concept or False
        form['entry_partner_id'] = partner_id
        form['entry_vat'] = move.line_id[0] and move.line_id[0].partner_id.vat
        form['tax_partner_id'] = meta and meta.partner_id.id or partner_id
        form['tax_vat'] = meta and meta.partner_id.vat or move.line_id[0] and move.line_id[0].partner_id.vat
        form['move_id'] = data['id']
        form['amount'] = meta and meta.amount or (parameters.amount and self._get_move_amount(cr, uid, move_ids, parameters.amount)) or 0
        form['amount_lines'] = parameters.amount and self._get_move_lines(cr, uid, move_ids, parameters.amount) or 0
        form['base'] = meta and meta.base or (parameters.base and self._get_move_amount(cr, uid, move_ids, parameters.base)) or 0
        form['base_lines'] = parameters.base and self._get_move_lines(cr, uid, move_ids, parameters.base) or 0
        form['total'] = meta and meta.total or (parameters.total and self._get_move_amount(cr, uid, move_ids, parameters.total)) or 0
        form['total_lines'] = parameters.total and self._get_move_lines(cr, uid, move_ids, parameters.total) or 0
        form['other'] = meta and meta.other or (parameters.other and self._get_move_amount(cr, uid, move_ids, parameters.other)) or 0
        form['other_lines'] = parameters.other and self._get_move_lines(cr, uid, move_ids, parameters.other) or 0
        form['ietu'] = meta and meta.ietu or (parameters.ietu and self._get_move_amount_tax(cr, uid, move_ids, parameters.ietu, 'account_tax_ietu')) or 0
        form['ietu_lines'] = ietu
        form['tax'] = meta and meta.tax or (parameters.tax and self._get_move_amount_tax(cr, uid, move_ids, parameters.tax, 'account_tax_fiscal')) or 0
        form['tax_lines'] = tax
        form['serial'] = meta and meta.serial or ''
        form['folio'] = meta and meta.folio or self._get_folio(cr, uid, move_ids)
        form['reference'] = meta and meta.reference or move.ref
        form['dif_amount'] = form['amount'] - (form['base'] + form['tax'])
        form['dif_total'] = form['total'] + (form['base'] + form['tax'] + form['other'])
        form['period_id'] = self._get_period(cr, uid, move, move_ids)
        form['diot'] = meta and meta.diot or False
        form['state'] = meta and meta.state or 'unsaved'
        form['property_account_position'] = move.line_id[0] and move.line_id[0].partner_id.property_account_position.id
        return form

    def _unlink(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        form = data['form']
        move = pool.get('account.move').browse(cr, uid, data['id'])
        if move.state == 'posted':
            raise wizard.except_wizard(_('Error de Usuario'), _('El asiento debe estar en estado borrador !'))
        meta_obj = pool.get('account.tax.meta')
        meta_id = meta_obj.search(cr, uid, [('move_id','=', data['id'])])
        meta_obj.unlink(cr, uid, meta_id)
        cr.execute('SELECT id FROM account_tax_fiscal WHERE move_id = '+str(data['id']))
        tax = [x[0] for x in cr.fetchall()]
        pool.get('account.tax.fiscal').unlink(cr, uid, tax)
        cr.execute('SELECT id FROM account_tax_ietu WHERE move_id = '+str(data['id']))
        tax = [x[0] for x in cr.fetchall()]
        pool.get('account.tax.ietu').unlink(cr, uid, tax)
        return self._get_defaults(cr, uid, data, context)

    def _save_tax(self, cr, uid, data, obj, sql_obj, lines, context):
        pool = pooler.get_pool(cr.dbname)
        tax_obj = pool.get(obj)
        par_obj = pool.get('account.tax.parameters')
        user = pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
           company_id = user.company_id.id
        else:
           company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        par = par_obj.search(cr, uid, [('company_id','=',company_id)])
        if not par:
            return True
        cr.execute('SELECT id FROM '+sql_obj+' WHERE move_id = '+str(data['id']))
        tax = [x[0] for x in cr.fetchall()]
        if tax:
            for t in tax:
                for f in lines:
                    if t == f[1] and not f[2]:
                        tax_obj.unlink(cr, uid, [t])
                    elif t == f[1]:
                        tax_obj.write(cr, uid, [t], f[2])
        else:
            for f in lines:
                tax_obj.create(cr, uid, f[2]) #   write(cr, uid, [f[1]], f[2])
        return True

    def _action_save(self, cr, uid, data, context):
        form = data['form']
        pool = pooler.get_pool(cr.dbname)
        move = pool.get('account.move').browse(cr, uid, data['id'])
        if move.state == 'posted':
            raise wizard.except_wizard(_('Error de Usuario'), _('El asiento debe estar en estado borrador !'))
        meta_obj = pool.get('account.tax.meta')
        self._save_tax(cr, uid, data, 'account.tax.fiscal', 'account_tax_fiscal', data['form']['tax_lines'], context)
        self._save_tax(cr, uid, data, 'account.tax.ietu', 'account_tax_ietu', data['form']['ietu_lines'], context)
        meta_id = meta_obj.search(cr, uid, [('move_id','=', data['id'])])
        if meta_id:
            meta_obj.write(cr, uid, meta_id, {
                'serial': form['serial'],
                'folio': form['folio'],
                'reference': form['reference'],
                'move_id': form['move_id'],
                'partner_id': form['tax_partner_id'],
                'third_party_type': form['third_party_type'],
                'amount': form['amount'],
                'base': form['base'],
                'ietu': form['ietu'],
                'ietu_concept': form['ietu_concept'],
                'tax': form['tax'],
                'total': form['total'],
                'other': form['other'],
                'diot': form['diot'],
                'state': 'saved',
            })
        else:
            meta_obj.create(cr, uid, {
                'serial': form['serial'],
                'folio': form['folio'],
                'reference': form['reference'],
                'move_id': form['move_id'],
                'partner_id': form['tax_partner_id'],
                'third_party_type': form['third_party_type'],
                'amount': form['amount'],
                'base': form['base'],
                'ietu': form['ietu'],
                'ietu_concept': form['ietu_concept'],
                'tax': form['tax'],
                'total': form['total'],
                'other': form['other'],
                'diot': form['diot'],
                'state': 'saved',
            })
        return {}

    def _check_user(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        move = pool.get('account.move').browse(cr, uid, data['id'])
        if move.state == 'posted':
            return 'view'
        for group in pool.get('res.users').browse(cr, uid, uid).groups_id:
            if group.name == 'Finance / Manager':
                return 'select'
        return 'select'

    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_user}
        },
        'select': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel','gtk-cancel'),('unlink','Delete'),('save','Save')]}
        },
        'view': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel','gtk-cancel')]}
        },
        'save': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_save, 'state':'end'}
        },
        'unlink': {
            'actions': [_unlink],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel','gtk-cancel'),('unlink','Delete'),('save','Save')]}
        },

    }
wizard_account_entry_tax_info('account.entry_tax_info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
