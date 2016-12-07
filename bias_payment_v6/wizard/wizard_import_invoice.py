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
    line_ids = line_obj.search(cr, uid, domain, context=context)
    FORM.string = '''<?xml version="1.0"?>
<form string="Populate Payment:">
    <field name="entries" colspan="4" height="300" width="1000" nolabel="1"
        domain="[('id', 'in', [%s])]" %s/>
</form>''' % (','.join([str(x) for x in line_ids]), ctx)
    return {}

def create_payment(self, cr, uid, data, context):
    line_ids= data['form']['entries'][0][2]
    if not line_ids: 
        return {}
    pool= pooler.get_pool(cr.dbname)
    order_obj = pool.get('payment.cheque')
    bnk_obj = pool.get('res.partner.bank')
    line_obj = pool.get('account.move.line')
    cur_obj = pool.get('res.currency')
    cheque = order_obj.browse(cr, uid, data['id'], context=context)
    chk_name = cheque.concept or ''
    ## Finally populate the current cheque with new lines:
    for line in line_obj.browse(cr, uid, line_ids, context=context):
        if chk_name:
            chk_name += ', '
        chk_name += (line.invoice and 'FAC.' or '') + line.ref or line.name or '/'
        amount_currency, pay_rate = 0, 1
        date_to_pay = cheque.date
        company_currency_id = line.account_id.company_id.currency_id.id
        currency_id = (line.currency_id and line.currency_id.id) or (line.invoice and line.invoice.currency_id.id) or company_currency_id
        journal_currency_id = cheque.mode.journal.currency and cheque.mode.journal.currency.id
        amount_currency = line.credit - line.debit
        calc_amount = line.amount_to_pay
        if currency_id == journal_currency_id != company_currency_id:
            amount_currency = line.invoice and line.invoice.amount_total or (-1 * line.amount_currency) or 0.0
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency_id], 'rate', arg=None, context={'date':date_to_pay})[company_currency_id]
            calc_amount = amount_currency
        elif currency_id != company_currency_id:
            amount_currency = line.invoice and line.invoice.amount_total or (-1 * line.amount_currency) or 0.0
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency_id], 'rate', arg=None, context={'date':date_to_pay})[company_currency_id]
            calc_amount = cur_obj.compute(cr, uid, currency_id, company_currency_id, line.amount_to_pay, context={'date': date_to_pay})
        pool.get('payment.cheque.line').create(cr,uid,{
            'move_line_id': line.id,
#            'amount_currency': line.amount_to_pay or 0.0,
            'amount_currency': cur_obj.compute(cr, uid, currency_id, journal_currency_id, line.amount_to_pay, context={'date': date_to_pay}),
            'amount': calc_amount or 0.0,
            'amount_document': amount_currency or 0.0,
            'currency': currency_id,
            'cheque_id': cheque.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            'date': date_to_pay,
            'pay_rate': pay_rate,
            'account_id': line.account_id.id,
            'company_currency': company_currency_id,
            }, context=context)
    order_obj.write(cr, uid, data['id'], {'concept': chk_name})
    return {}

class wizard_invoice_import(wizard.interface):
    states = {

        'init_back': {
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

        'init': {
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

