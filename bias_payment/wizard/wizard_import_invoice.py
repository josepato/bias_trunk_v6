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
    'entries': {'string':'Entries', 'type':'many2many', 'relation': 'account.move.line',},
}
field_duedate={
    'duedate': {'string':'Due Date', 'type':'date','required':True, 'default': lambda *a: time.strftime('%Y-%m-%d'),},
    }
arch_duedate='''<?xml version="1.0"?>
<form string="Search Payment lines">
    <field name="duedate" />
</form>'''


def _get_date(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    data['form']['duedate'] = pool.get('payment.cheque').browse(cr, uid, data['id'], context=context).date
    return data['form']

def search_entries(self, cr, uid, data, context):
    search_due_date=data['form']['duedate']

    pool = pooler.get_pool(cr.dbname)
    chk_obj = pool.get('payment.cheque')
    line_obj = pool.get('account.move.line')

    cheque = chk_obj.browse(cr, uid, data['id'],
            context=context)
    ctx = ''
    if cheque.mode:
        ctx = '''context="{'journal_id': %d}"''' % cheque.mode.journal.id

    # Search for move line to pay:
    domain = [('reconcile_id', '=', False),('account_id.type', 'in', ['payable','receivable']),('partner_id','=',cheque.partner_id.id),
                ('journal_id.type','!=','cash')]
    #('amount_to_pay', '>', 0)
    domain = domain + ['|',('date_maturity','<',search_due_date),('date_maturity','=',False)]
    line_ids = line_obj.search(cr, uid, domain, context=context)
    FORM.string = '''<?xml version="1.0"?>
<form string="Populate Payment:">
    <field name="entries" colspan="4" height="300" width="1000" nolabel="1"
        domain="[('id', 'in', [%s])]" %s/>
</form>''' % (','.join([str(x) for x in line_ids]), ctx)
    return {}

def create_payment(self, cr, uid, data, context):
    line_ids= data['form']['entries'][0][2]
    if not line_ids: return {}
    pool= pooler.get_pool(cr.dbname)
    order_obj = pool.get('payment.cheque')
    bnk_obj = pool.get('res.partner.bank')
    line_obj = pool.get('account.move.line')
    cur_obj = pool.get('res.currency')
    payment = order_obj.browse(cr, uid, data['id'], context=context)
    t = payment.mode and payment.mode.type.id or None
    line2bank = pool.get('account.move.line').line2bank(cr, uid,
            line_ids, t, context)
    chk_name = payment.concept or ''
    ## Finally populate the current payment with new lines:
    partial_rec = []
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        if chk_name:
            chk_name += ', '
        chk_name += line.ref or '/'
        if line.reconcile_partial_id:
            partial_rec = [x.id for x in line.reconcile_partial_id.line_partial_ids]
            partial_rec.remove(line.id)
    order_obj.write(cr, uid, data['id'], {'concept': chk_name, 'partial_line_id': map(lambda x: (4,x,False), partial_rec)})
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        amount_currency, pay_rate, rate = 0, 1, 1
        date_to_pay = payment.date
        currency = line.currency_id.id or (line.invoice and line.invoice.currency_id.id) or line.account_id.company_id.currency_id.id
        company_currency = line.account_id.company_id.currency_id.id
        journal_currency = payment.mode.journal.currency.id
        calc_amount = amount_currency = line.amount_to_pay
        calc_currency = company_currency
        if currency == journal_currency != company_currency:
            amount_currency = abs((line.invoice and (line.credit > 0 and -line.invoice.residual or line.invoice.residual)) \
                        or (line.amount_to_pay and (line.credit > 0 and -line.amount_to_pay or line.amount_to_pay)) \
                        or line.amount_currency or (line.debit - line.credit) or 0.0)
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency], 'rate', arg=None, context={'date':date_to_pay})[company_currency]
            calc_amount = amount_currency
            calc_currency = currency
        elif currency != company_currency:
            amount_currency = abs((line.invoice and (line.credit > 0 and -line.invoice.residual or line.invoice.residual)) \
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
            'calc_currency': calc_currency,
            'bank_id': line2bank.get(line.id),
            'cheque_id': payment.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            'communication': line.ref or '/',
            'date': date_to_pay,
            'rate': rate,
            'pay_rate': pay_rate,
            'account_id': line.account_id.id,
            'company_currency': company_currency,
            'cost_center_id': line.cost_center_id and line.cost_center_id.id,
            }, context=context)
    return {}

class wizard_invoice_import(wizard.interface):
    states = {

        'init': {
            'actions': [_get_date],
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

wizard_invoice_import('import_invoice')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

