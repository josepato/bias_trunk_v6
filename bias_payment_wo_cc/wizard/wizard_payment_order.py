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
import pooler
from tools.misc import UpdateableStr
import time


FORM = UpdateableStr()

FIELDS = {
    'entries': {'string':'Entries ', 'type':'many2many', 'relation': 'account.move.line',},
    'result': {'string': 'Lines Processed', 'type':'float', 'readonly':True},
}
field_duedate={
    'duedate': {'string':'Due Date', 'type':'date','required':True, 'default': lambda *a: time.strftime('%Y-%m-%d'),},
    'partner_id': {'string':'Partner', 'type':'many2many', 'relation': 'res.partner',},
    'journal_id': {'string':'Journal', 'type':'many2many', 'relation': 'account.journal','default': lambda *a: [],},
    }
arch_duedate='''<?xml version="1.0"?>
<form string="Search Payment lines">
    <field name="duedate" />
    <separator colspan="4" string="Select specific Partners or NON for all"/>
    <field name="partner_id" width="700" height="200" colspan="4" nolabel="1"/>
    <separator colspan="4" string="Select specific Journals or NON for all"/>
    <field name="journal_id" colspan="4" height="200" nolabel="1"/>
</form>'''


def search_entries(self, cr, uid, data, context):
    search_due_date=data['form']['duedate']

    pool = pooler.get_pool(cr.dbname)
    order_obj = pool.get('payment.order')
    line_obj = pool.get('account.move.line')
    payment = order_obj.browse(cr, uid, data['id'], context=context)
    ctx = ''
    if payment.mode:
        ctx = '''context="{'journal_id': %d}"''' % payment.mode.journal.id

    # Search for move line to pay:
    domain = [('reconcile_id', '=', False),('account_id.type', 'in', ['payable','receivable'])]#,('amount_to_pay', '>', 0)]
    if data['form']['partner_id'][0][2]:
        domain = domain + [('partner_id', 'in', data['form']['partner_id'][0][2])]
    if data['form']['journal_id'][0][2]:
        domain = domain + [('journal_id', 'in', data['form']['journal_id'][0][2])]
    domain = domain + ['|',('date_maturity','<',search_due_date),('date_maturity','=',False)]
    line_ids = line_obj.search(cr, uid, domain, context=context)
    data['form']['result'] = len(line_ids)
    FORM.string = '''<?xml version="1.0"?>
<form string="Populate Payment:">
    <field name="result"/>
    <field name="entries" colspan="4" height="300" width="800" nolabel="1"
        domain="[('id', 'in', [%s])]" %s/>
</form>''' % (','.join([str(x) for x in line_ids]), ctx)
    return data['form']

def create_payment(self, cr, uid, data, context):
    line_ids= data['form']['entries'][0][2]
    if not line_ids: return {}
    pool= pooler.get_pool(cr.dbname)
    order_obj = pool.get('payment.order')
    bnk_obj = pool.get('res.partner.bank')
    line_obj = pool.get('account.move.line')
    cur_obj = pool.get('res.currency')
    payment = order_obj.browse(cr, uid, data['id'], context=context)
    t = payment.mode and payment.mode.type.id or None
    line2bank = pool.get('account.move.line').line2bank(cr, uid, line_ids, t, context)
    ## Finally populate the current payment with new lines:
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        amount_currency, pay_rate, rate = 0, 1, 1
        if payment.date_prefered == "now":
            #no payment date => immediate payment
            date_to_pay = time.strftime('%Y-%m-%d')
        elif payment.date_prefered == 'due':
            date_to_pay = line.date_maturity or time.strftime('%Y-%m-%d')
        elif payment.date_prefered == 'fixed':
            date_to_pay = payment.date_planned
        currency = line.currency_id.id or (line.invoice and line.invoice.currency_id.id) or line.account_id.company_id.currency_id.id
        company_currency = line.account_id.company_id.currency_id.id
        calc_amount = amount_currency = line.amount_to_pay
        if currency != company_currency:
            amount_currency = -1 * ((line.invoice and (line.credit > 0 and -line.invoice.residual or line.invoice.residual)) \
                        or (line.amount_to_pay and (line.credit > 0 and -line.amount_to_pay or line.amount_to_pay)) \
                        or line.amount_currency or (line.debit - line.credit) or 0.0)
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency], 'rate', arg=None, context={'date':date_to_pay})[company_currency]
            rate = abs((line.debit - line.credit) / amount_currency)
            calc_amount = cur_obj.compute(cr, uid, currency, company_currency, amount_currency, context={'date': date_to_pay})
        pool.get('payment.line').create(cr,uid,{
            'move_line_id': line.id,
            'calc_amount': calc_amount or 0.0,
            'amount_currency': amount_currency or 0.0,
            'currency': currency,
            'bank_id': line2bank.get(line.id),
            'order_id': payment.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            'communication': line.ref or '/',
            'date': date_to_pay,
            'rate': rate,
            'pay_rate': pay_rate,
            'account_id': line.account_id.id,
            'company_currency': company_currency,
            }, context=context)
    return {}

def create_payment_1(self, cr, uid, data, context):
    line_ids= data['form']['entries'][0][2]
    if not line_ids: return {}

    pool= pooler.get_pool(cr.dbname)
    order_obj = pool.get('payment.order')
    bnk_obj = pool.get('res.partner.bank')
    line_obj = pool.get('account.move.line')
    cur_obj = pool.get('res.currency')

    payment = order_obj.browse(cr, uid, data['id'],
            context=context)
    t = payment.mode and payment.mode.type.id or None
    line2bank = pool.get('account.move.line').line2bank(cr, uid,
            line_ids, t, context)

    ## Finally populate the current payment with new lines:
    partial_rec = []
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        if line.reconcile_partial_id:
            partial_rec = [x.id for x in line.reconcile_partial_id.line_partial_ids]
            partial_rec.remove(line.id)
            line_ids += partial_rec
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        if payment.date_prefered == "now":
            #no payment date => immediate payment
            date_to_pay = time.strftime('%Y-%m-%d')
        elif payment.date_prefered == 'due':
            date_to_pay = line.date_maturity or time.strftime('%Y-%m-%d')
        elif payment.date_prefered == 'fixed':
            date_to_pay = payment.date_planned
        bank_id = line2bank.get(line.id)
        code_id = False
        operation = False
        if line2bank.get(line.id):
            code_id = bnk_obj.browse(cr, uid, bank_id).name
            if bnk_obj.browse(cr,uid,bank_id).bank.id == payment.mode.bank_id.bank.id:
                operation = payment.mode.payment_export_id.same_bnk
            else:
                operation = payment.mode.payment_export_id.other_bnk
        
        amount_currency = (line.invoice and line.invoice.residual) or line.amount_to_pay or line.amount_currency or (line.debit - line.credit) or 0.0
        currency = line.currency_id.id or (line.invoice and line.invoice.currency_id.id) or line.account_id.company_id.currency_id.id
        company_currency = line.account_id.company_id.currency_id.id
        rate = 0
        if amount_currency:
            pay_rate = cur_obj._current_rate(cr, uid, [currency], 'rate', arg=None, context={'date':date_to_pay})[currency]
            rate = (line.debit - line.credit) / amount_currency
            calc_amount = cur_obj.compute(cr, uid, currency, company_currency, amount_currency, context={'date': date_to_pay})
        pool.get('payment.line').create(cr,uid,{
            'move_line_id': line.id,
            'calc_amount': (line.id not in partial_rec) and calc_amount or 0.0,
            'amount_currency': (line.id not in partial_rec) and amount_currency or 0.0,
            'currency': currency,
            'bank_id': bank_id,
            'order_id': payment.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            'code_id': code_id,
            'communication': line.ref or '/',
            'date': date_to_pay,
            'rate': rate,
            'pay_rate': pay_rate,
            'operation': operation,
            'account_id': line.account_id.id,
            }, context=context)
    return {}


class wizard_payment_order(wizard.interface):
    """
    Create a payment object with lines corresponding to the account move line
    to pay according to the date and the mode provided by the user.
    Hypothesis:
    - Small number of non-reconcilied move line , payment mode and bank account type,
    - Big number of partner and bank account.

    If a type is given, unsuitable account move lines are ignored.
    """
    states = {

        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': arch_duedate,
                'fields':field_duedate,
                'state': [
                    ('end','_Cancel'),
                    ('search','_Search', '', True)
                ]
            },
         },

        'search': {
            'actions': [search_entries],
            'result': {
                'type': 'form',
                'arch': FORM,
                'fields': FIELDS,
                'state': [
                    ('end','_Cancel'),
                    ('create','_Add to payment order', '', True)
                ]
            },
         },
        'create': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': create_payment,
                'state': 'end'}
            },
        }

wizard_payment_order('populate_pay')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

