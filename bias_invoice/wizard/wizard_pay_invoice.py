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

import wizard
import netsvc
import pooler
import time
from tools.translate import _
from tools.misc import UpdateableStr

FLAG = {'cc_installed':'0'}

pay_form = UpdateableStr()

pay_fields = {
    'amount': {'string': 'Amount paid', 'type':'float', 'required':True, 'readonly':True},
    'org_inv_amount': {'string': 'Invoice Amount', 'type':'float', 'readonly':True},
    'org_inv_amount_local': {'string': 'Invoice Amount', 'type':'float', 'readonly':True},
    'pay_inv_amount': {'string': 'To Pay Amount', 'type':'float', 'required':True, 'readonly':False},
    'inv_rate': {'string': 'Currency Rate', 'type':'float', 'digits':(14,4), 'readonly':True},
    'rate': {'string': 'Currency Rate', 'type':'float', 'digits':(14,4)},
    'name': {'string': 'Entry Name', 'type':'char', 'size': 64, 'required':True, 'readonly':True},
    'date': {'string': 'Payment date', 'type':'date', 'required':True, 'default':lambda *args: time.strftime('%Y-%m-%d')},
    'journal_id': {'string': 'Journal/Payment Mode', 'type': 'many2one', 'relation':'account.journal', 'required':True, 'domain':[('type','=','cash')]},
    'currency_id': {'string': 'Currency', 'type': 'many2one', 'relation':'res.currency', 'readonly':True},
    'inv_currency_id': {'string': 'Currency', 'type': 'many2one', 'relation':'res.currency', 'readonly':True},
    'inv_currency_id_local': {'string': 'Currency', 'type': 'many2one', 'relation':'res.currency', 'readonly':True},
    'pay_currency_id': {'string': 'Currency', 'type': 'many2one', 'relation':'res.currency', 'readonly':True},
    'invoice_id': {'string': 'Invoice', 'type': 'many2one', 'relation':'account.invoice', 'readonly':True},
    'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period', 'required':True},
    'cost_center_id': {'string': 'Cost Center', 'type': 'many2one', 'relation':'cost.center', 'required':False},
}


def _pay_and_reconcile(self, cr, uid, data, context):
    form = data['form']
    period_id = form.get('period_id', False)
    journal_id = form.get('journal_id', False)
    writeoff_account_id = form.get('writeoff_acc_id', False)
    writeoff_journal_id = form.get('writeoff_journal_id', False)
    pool = pooler.get_pool(cr.dbname)
    cur_obj = pool.get('res.currency')
    amount = form['amount']

    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context)
    if journal.currency and invoice.company_id.currency_id.id<>journal.currency.id:
        ctx = {'date':data['form']['date']}
        amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)

    # Take the choosen date
    if form.has_key('comment'):
        context={'date_p':form['date'],'comment':form['comment'],'amount_currency':form['pay_inv_amount']}
    else:
        context={'date_p':form['date'],'comment':False,'amount_currency':form['pay_inv_amount']}

    acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
    if not acc_id:
        raise wizard.except_wizard(_('Error !'), _('Your journal must have a default credit and debit account.'))
    pool.get('account.invoice').pay_and_reconcile(cr, uid, [data['id']],
            amount, acc_id, period_id, journal_id, writeoff_account_id,
            period_id, writeoff_journal_id, context, data['form']['name'], data['form']['cost_center_id'])
    return {}

def _wo_check(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context)
    if invoice.company_id.currency_id.id <> invoice.currency_id.id:
        return 'addendum'
    if journal.currency and (journal.currency.id <> invoice.currency_id.id):
        return 'addendum'
    if pool.get('res.currency').is_zero(cr, uid, invoice.currency_id, (data['form']['amount'] - invoice.amount_total)):
        return 'reconcile'
    return 'addendum'

_transaction_add_form = '''<?xml version="1.0"?>
<form string="Information addendum">
    <separator string="Write-Off Move" colspan="4"/>
    <field name="writeoff_acc_id" domain="[('type','&lt;&gt;','view'),('type','&lt;&gt;','consolidation')]"/>
    <field name="writeoff_journal_id"/>
    <field name="comment"/>
</form>'''

_transaction_add_fields = {
    'writeoff_acc_id': {'string':'Write-Off account', 'type':'many2one', 'relation':'account.account', 'required':True},
    'writeoff_journal_id': {'string': 'Write-Off journal', 'type': 'many2one', 'relation':'account.journal', 'required':True},
    'comment': {'string': 'Entry Name', 'type':'char', 'size': 64, 'required':True},
    'gain_loss': {'string': 'Gain/Loss', 'type':'float', 'readonly':True},
}

def _get_value_addendum(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    form = data['form']
    pool = pooler.get_pool(cr.dbname)
    cur_obj = pool.get('res.currency')
    amount = form['amount']
    journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context)
    ctx = {'date':data['form']['date']}
    ctx_invoice = {'date': invoice.move_id.line_id[0].date}
    amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)
    ctx = {'date':invoice.date_invoice}
    invoice_amount = cur_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id, invoice.amount_total, context=ctx_invoice)
    gain_loss = amount - invoice_amount
    res = {'comment': invoice.number, 'gain_loss': gain_loss}
    if journal.gain_fluc_acc and journal.loss_fluc_acc:
        res = {'comment': invoice.number, 'writeoff_acc_id': journal.loss_fluc_acc.id, 
                'writeoff_journal_id': invoice.journal_id.id, 'gain_loss': gain_loss}
        if gain_loss >= 0:
            res = {'comment': invoice.number, 'writeoff_acc_id': journal.gain_fluc_acc.id, 
                'writeoff_journal_id': invoice.journal_id.id, 'gain_loss': gain_loss}
    return res

def _get_period(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    lin_obj = pool.get('account.move.line')
    ids = pool.get('account.period').find(cr, uid, context=context)
    period_id = False
    if len(ids):
        period_id = ids[0]
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    if invoice.state in ['draft', 'proforma2', 'cancel', 'paid']:
        raise wizard.except_wizard(_('Error !'), _('Can not pay paid/draft/proforma/cancel invoice.'))
    date = time.strftime('%Y-%m-%d')
    context['date'] = invoice.date_invoice
    if not invoice.move_id:
        raise wizard.except_wizard(_('Error !'), _('The invoice is open but without account entry.'))
    invoice_amount = [x.id for x in filter(lambda x: x.account_id.type in ('receivable','payable'), invoice.move_id.line_id)]
    invoice_amount = abs(lin_obj.browse(cr,uid,invoice_amount[0]).debit-lin_obj.browse(cr,uid,invoice_amount[0]).credit)
    inv_rate = invoice_amount / invoice.amount_total
    company_currency = invoice.account_id.company_id.currency_id.id
    context['date'] = date
    rate = 1
    if company_currency != invoice.currency_id.id:
        rate = pool.get('res.currency')._current_rate(cr, uid, [company_currency], 'rate', arg=None, context=context)[company_currency]
    values = {
        'period_id': period_id,
        'amount': invoice.residual,
        'org_inv_amount': invoice.residual,
        'org_inv_amount_local': invoice_amount,
        'pay_inv_amount': invoice.residual,
        'name': ((invoice.type == 'in_invoice') and invoice.reference) or invoice.number,
        'date': date,
        'rate': rate,
        'inv_rate': inv_rate,
        'currency_id': invoice.currency_id.id,
        'inv_currency_id': invoice.currency_id.id,
        'inv_currency_id_local': company_currency,
        'pay_currency_id': invoice.currency_id.id,
        'invoice_id': invoice.id,
    }
    cc_module = pool.get('ir.module.module').search(cr, uid, [('name','=','bias_cost_center')])
    pay_form.string = '''<?xml version="1.0"?>
<form string="Pay invoice">
    <separator string="Invoice Information" colspan="4"/>
    <field name="invoice_id"/>
    <field name="inv_rate"/>
    <field name="inv_currency_id"/>
    <field name="org_inv_amount"/>
    <field name="inv_currency_id_local"/>
    <field name="org_inv_amount_local"/>
    <separator string="Payment Information" colspan="4"/>
    <field name="currency_id"/>
    <field name="amount"/>
    <field name="pay_currency_id"/>
    <field name="pay_inv_amount"
        on_change="onchange_rate(journal_id, invoice_id, amount, currency_id, inv_currency_id, date, rate, inv_rate, pay_inv_amount)" />'''
    if cc_module and pool.get('ir.module.module').browse(cr, uid, cc_module[0]).state == 'installed':
        values['cost_center_id'] = invoice.cost_center_id and invoice.cost_center_id.id
        pay_form.string += '''<field name="cost_center_id" required="1"/>'''
    pay_form.string += '''
    <field name="rate" attrs="{'readonly':[('inv_currency_id','=',1),('currency_id','=',1)]}"
        on_change="onchange_rate(journal_id, invoice_id, amount, currency_id, inv_currency_id, date, rate, inv_rate, pay_inv_amount)" />
    <newline/>
    <field name="date" 
        on_change="onchange_journal_id(journal_id, invoice_id, amount, currency_id, inv_currency_id, date, rate, inv_rate, pay_inv_amount, period_id, 1)"/>
    <field name="journal_id" 
        on_change="onchange_journal_id(journal_id, invoice_id, amount, currency_id, inv_currency_id, date, rate, inv_rate, pay_inv_amount, period_id, 0)"/>
    <field name="period_id"/>
    <field name="name"/>
</form>'''
    return values

class wizard_pay_invoice(wizard.interface):
    states = {
        'init': {
            'actions': [_get_period],
            'result': {'type':'form', 'arch':pay_form, 'fields':pay_fields, 'state':[('end','Cancel'),('reconcile','Partial Payment'),('writeoff_check','Full Payment')]}
        },
        'writeoff_check': {
            'actions': [],
            'result' : {'type': 'choice', 'next_state': _wo_check }
        },
        'addendum': {
            'actions': [_get_value_addendum],
            'result': {'type': 'form', 'arch':_transaction_add_form, 'fields':_transaction_add_fields, 'state':[('end','Cancel'),('reconcile','Pay and reconcile')]}
        },
        'reconcile': {
            'actions': [_pay_and_reconcile],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_pay_invoice('account.invoice.pay.bias')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

