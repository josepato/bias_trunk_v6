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


from osv import osv
from osv import fields
from tools import config
import decimal
from decimal import Decimal

#----------------------------------------------------------
# Account Journal
#----------------------------------------------------------
class account_journal(osv.osv):
    _inherit="account.journal"

    _columns = {
        'gain_fluc_acc': fields.many2one('account.account', 'Gain Fluctuation Acc.', domain="[('type','!=','view')]", help="Used as write off account when the currency fluctuation result in gain."),
        'loss_fluc_acc': fields.many2one('account.account', 'Loss Fluctuation Acc.', domain="[('type','!=','view')]", help="Used as write off account when the currency fluctuation result in loss."),
        'reconcile_tolerance': fields.float('Reconcile Tolerance', help="Difference tolerated in payment transaction. "),
    }
account_journal()

#----------------------------------------------------------
# wizard_account_invoice_pay_bias
#----------------------------------------------------------
class wizard_account_invoice_pay_bias(osv.osv):
    _name = 'wizard.account.invoice.pay.bias'
    def onchange_journal_id(self, cr, uid, ids, journal_id, invoice_id, amount, currency_id, 
                            inv_currency_id, date, rate, inv_rate, pay_inv_amount, period_id, d):
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        currency_source = inv_currency_id
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            currency_dest = journal.currency.id or invoice.company_id.currency_id.id
        else: 
            currency_dest = invoice.currency_id.id
            return {'value':{}}
        decimal.getcontext().prec = 6
        if d:
            currency_dest = invoice.company_id.currency_id.id
            rate = self.pool.get('res.currency')._current_rate(cr, uid, [currency_dest], 'rate', arg=None, context={'date':date})[currency_dest]
            period_id = self.pool.get('account.period').find(cr, uid, date)[0]
        if not journal_id:
            return {'value':{'currency_id': invoice.currency_id.id, 'amount': pay_inv_amount, 'rate': rate, 'period_id': period_id}}
        if currency_dest == inv_currency_id:
            return {'value':{'currency_id': invoice.currency_id.id, 'amount': pay_inv_amount, 'rate': 1, 'period_id': period_id}}
        else:
            amount = pay_inv_amount * rate
        val = {'currency_id': currency_dest, 'amount': amount, 'rate': rate, 'period_id': period_id}
        return {'value':val}

    def onchange_rate(self, cr, uid, ids, journal_id, invoice_id, amount, currency_id, inv_currency_id, date, rate, inv_rate, pay_inv_amount):
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            currency_dest = journal.currency.id or invoice.company_id.currency_id.id
        else: 
            return {'value':{}}
        if currency_dest == inv_currency_id:
            return {'value':{'amount': pay_inv_amount}}
        else:
            amount = pay_inv_amount * rate #invoice.residual * rate
        val = {'currency_id': currency_dest, 'amount': amount, 'rate': rate}
        return {'value':val}

wizard_account_invoice_pay_bias()

#----------------------------------------------------------
# Account Invoice Line
#----------------------------------------------------------
class account_invoice_line(osv.osv):
    _inherit="account.invoice.line"

    _columns = {
        'deduction':fields.boolean('Deduction', required=False),
    }
account_invoice_line()

#----------------------------------------------------------
# Account Invoice
#----------------------------------------------------------
class account_invoice(osv.osv):
    _inherit="account.invoice"

    _columns = {
        'supplier_document':fields.selection([('copy', 'Copy'), ('original', 'Original')], 'Document',required=False),
    }

    def validate(self, obj):
        res = []
        for invoice_id in obj:
            if not invoice_id.move_id.id:
                return []
            else:
                res.append(invoice_id.move_id)
        return res
        
    def pay_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name='', cc=False):
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        assert len(ids)==1, "Can only pay one invoice at a time"
        invoice = self.browse(cr, uid, ids[0])
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        #take the choosen date
        if 'date_p' in context and context['date_p']:
            date=context['date_p']
        else:
            date=time.strftime('%Y-%m-%d')
#        date = line.date
        company_currency = invoice.company_id.currency_id
        if invoice.currency_id != company_currency:
            currency_id = invoice.currency_id.id
            amount_currency = context.has_key('amount_currency') and context['amount_currency'] or 0.0
        else:
            currency_id = False
            amount_currency, currency_id = False, False

        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':((invoice.type == 'in_invoice') and invoice.reference) or invoice.number,
            'date': date,
            'currency_id': currency_id,
            'amount_currency': direction *  amount_currency,
            'cost_center_id': cc
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':((invoice.type == 'in_invoice') and invoice.reference) or invoice.number,
            'date': date,
            'currency_id': currency_id,
            'amount_currency':  - direction * amount_currency,
            'cost_center_id': cc
        }
        if not name:
            name = invoice.invoice_line and invoice.invoice_line[0].name or invoice.number
        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        if invoice.type in ('out_invoice','in_refund'):
            move_type = 'bank_rec_voucher'
        if invoice.type in ('in_invoice','out_refund'):
            move_type = 'bank_pay_voucher'
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date, 'type':move_type}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id==src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total,int(config['price_accuracy']))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return True

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

