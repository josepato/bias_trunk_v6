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

from osv import fields, osv
import time
import netsvc
from decimal import Decimal, getcontext


#******************************************************************************************
#   Multiple Invoice Payment
#******************************************************************************************
class multiple_payment(osv.osv):
    _name = 'multiple.payment'
    _description = 'Multiple Payment'

    def _amount_all(self, cr, uid, ids, field_name, arg, context):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for payment in self.browse(cr, uid, ids):
            res[payment.id] = {
                'amount_total': 0.0,
            }
            val = 0.0
            cur = payment.journal_id.currency
            if payment.payment_line:
                for line in payment.payment_line:
                    val += line.payment
                res[payment.id]['amount_total'] = cur_obj.round(cr, uid, cur, val)
            else:
                res[payment.id]['amount_total'] = 0.0
        return res

    def _get_order(self, cr, uid, ids, context={}):
        result = {}
        for line in self.pool.get('multiple.payment.line').browse(cr, uid, ids, context=context):
            result[line.payment_id.id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'payment_line': fields.one2many('multiple.payment.line', 'payment_id', 'Documents', readonly=True, states={'draft':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True, states={'draft':[('readonly',False)]}),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'amount': fields.float('Payment', digits=(14,2), readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft','Draft'),
                                   ('confirm','Confirm'),
                                   ('done','Done'),
                                   ('cancel','Cancel')], 'Status', required=True, readonly=True),
        'date': fields.date('Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'rate': fields.float('rate', digits=(6,4), readonly=True, states={'draft':[('readonly',False)]}),
        'move_id': fields.many2one('account.move', 'Entry', readonly=True, help="Link to the automatically generated account moves."),
        'amount_total': fields.function(_amount_all, method=True, string='Total Calc',
            store={
                'multiple.payment': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                'multiple.payment.line': (_get_order, None, 10),
            },
            multi='sums'),
    }
    _defaults = {
        'name': lambda *a: '/',
        'state': lambda *a: 'draft',
        'date': lambda *a:time.strftime('%Y-%m-%d'),
    }

    def button_compute(self, cr, uid, ids, context={}):
        line_obj = self.pool.get('multiple.payment.line')
        for payment in self.browse(cr, uid, ids):
            for line in payment.payment_line:
                v = line_obj._get_payment(cr, uid, line.line_id.id, payment.journal_id.id, payment.rate, context)
                line_obj.write(cr, uid, [line.id], {'name':v['name'], 'amount_to_pay':v['amount_to_pay'], 'currency_id':v['currency_id'], \
                                'amount_currency':v['amount_currency'], 'payment':v['payment'], 'payment_currency':v['payment_currency'], \
                                'partial': False})
        return True

    def _unreconcile(self, cr, uid, line_id, context):
        recs = filter(lambda x: x['reconcile_id'], line_id)
        rec_ids = [x['reconcile_id'].id for x in recs]
        if len(rec_ids):
            self.pool.get('account.move.reconcile').unlink(cr, uid, rec_ids)
        return True

    def button_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True

    def button_cancel(self, cr, uid, ids, context={}):
        for pay in self.browse(cr, uid, ids):
            self._unreconcile(cr, uid, pay.move_id.line_id, context=context)
            self.pool.get('account.move').unlink(cr, uid, [pay.move_id.id])
            for pay_line in pay.payment_line:
                if pay_line.payments_ids:
                    lines2reconcile = [pay_line.line_id.id] + [x.id for x in pay_line.payments_ids]
                    self.pool.get('account.move.line').reconcile_partial(cr, uid, lines2reconcile, 'simple')
            self.write(cr, uid, [pay.id], {'state': 'cancel'})
        return True

    def button_cancel_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def button_pay(self, cr, uid, ids, context={}):
        pay_line_obj = self.pool.get('multiple.payment.line')
        move_line_obj = self.pool.get('account.move.line')
        values = {}
        for pay in self.browse(cr, uid, ids):
            company_currency_id = pay.journal_id.default_credit_account_id.company_id.currency_id.id
            journal_currency_id = pay.journal_id.currency.id
            currency_id = pay.journal_id.currency.id != company_currency_id and pay.journal_id.currency.id or False
            period_id = self.pool.get('account.period').find(cr, uid, pay.date)[0]
            debit = credit = amount_currency = cost_center_id = currency_id = 0
            ref = ''
            move = {'ref': ref, 'journal_id': pay.journal_id.id, 'period_id': period_id, 'date': pay.date, 'type': 'bank_rec_voucher'}
            move_id = self.pool.get('account.move').create(cr, uid, move)
            for line in pay.payment_line:
                if journal_currency_id == line.line_id.currency_id.id != company_currency_id:
                    payment = line.amount_currency * pay.rate
                else:
                    payment = line.payment
                l1 = {
                    'debit': payment<0 and payment or 0.0,
                    'credit': payment>0 and payment or 0.0,
                    'account_id': line.line_id.account_id.id,
                    'partner_id': line.line_id.partner_id.id,
                    'ref': line.line_id.ref,
                    'date': pay.date,
                    'currency_id': line.line_id.currency_id.id,
                    'amount_currency': line.amount_currency,
                    'cost_center_id': line.line_id.cost_center_id.id,
                    'journal_id': pay.journal_id.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': line.line_id.name
                }
                debit += l1['credit']
                credit += l1['debit']
                amount_currency += l1['amount_currency'] * -1
                ref += (ref and ',') + l1['ref']
                if l1['cost_center_id'] and not cost_center_id:
                    cost_center_id = l1['cost_center_id'] 
                values[line.id] = l1
            l2 = {
                    'debit': debit,
                    'credit': credit,
                    'account_id': pay.journal_id.default_credit_account_id.id,
                    'partner_id': pay.partner_id.id,
                    'ref': ref,
                    'date': pay.date,
                    'currency_id': currency_id,
                    'amount_currency': currency_id and amount_currency,
                    'cost_center_id': cost_center_id,
                    'journal_id': pay.journal_id.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': ref
            }
            for key in values.keys():
                line_id = move_line_obj.create(cr, uid, values[key])
                pay_line_obj.write(cr, uid, [key], {'move_line_id': line_id}) 
            line_id = self.pool.get('account.move.line').create(cr, uid, l2)
            self.pool.get('account.move').write(cr, uid, [move_id], {'ref': ref})
            for key in values.keys():
                pay_line = pay_line_obj.browse(cr, uid, key)
                if pay.journal_id.debit_fluc_acc and pay.journal_id.credit_fluc_acc:
                    writeoff_acc_id = pay.journal_id.credit_fluc_acc.id
                    if ((pay_line.move_line_id.debit - pay_line.move_line_id.credit) - (pay_line.line_id.debit - pay_line.line_id.credit)) >= 0:
                        writeoff_acc_id = pay.journal_id.debit_fluc_acc.id
                lines2reconcile = [pay_line.line_id.id, pay_line.move_line_id.id]
                if pay_line.payments_ids:
                    lines2reconcile += [x.id for x in pay_line.payments_ids]
                if pay_line.partial:
                    move_line_obj.reconcile_partial(cr, uid, lines2reconcile, 'simple')
                else:
                    move_line_obj.reconcile(cr, uid, lines2reconcile, 'simple', writeoff_acc_id, period_id, pay.journal_id.id)
#        self.write(cr, uid, ids, {'move_id': move_id})
        self.write(cr, uid, ids, {'state': 'done', 'move_id': move_id})
        return True

    def onchange_journal_id(self, cr, uid, ids, journal_id, date):
        v = {'currency_id': False, 'rate': False}
        if journal_id:
            v['currency_id'] = self.pool.get('account.journal').browse(cr, uid, journal_id).currency.id
            v['rate'] = self.pool.get('res.currency')._current_rate_inv(cr, uid, [2], 'rate', arg=None, context={'date':date})[2]
        return {'value':v}

multiple_payment()

#******************************************************************************************
#   Multiple Invoice Payment Line
#******************************************************************************************
class multiple_payment_line(osv.osv):
    _name = 'multiple.payment.line'
    _description = 'Multiple Payment Line'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'payment_id': fields.many2one('multiple.payment', 'Payment', required=True, ondelete='cascade', select=True),
        'line_id': fields.many2one('account.move.line', 'Document', required=True, states={'posted':[('readonly',True)]}),
        'payment': fields.float('Payment', digits=(14,2)),
        'payment_currency': fields.float('Payment Currency', digits=(14,2)),
        'amount_to_pay': fields.float('Amount to pay', digits=(14,2)),
        'amount_currency': fields.float('Amount Currency', digits=(14,2)),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'partial': fields.boolean('Partial'),
        'move_line_id': fields.many2one('account.move.line', 'Entry Line', required=False, states={'posted':[('readonly',True)]}),
        'payments_ids': fields.many2many('account.move.line', 'multiple_payment_line_rel','account_move_line_id','line_id', 'Payments'),
    }

    _defaults = {
        'name': lambda *a: '/',
    }

    def onchange_line_id(self, cr, uid, ids, line_id, journal_id, rate):
        v = self._get_payment(cr, uid, line_id, journal_id, rate)
        return {'value':v}

    def onchange_payment(self, cr, uid, ids, line_id, journal_id, rate, payment=False, payment_currency=False):
        getcontext().prec = 2
        res = {}
        v = self._get_payment(cr, uid, line_id, journal_id, rate)
        if payment and Decimal(str(payment)) != Decimal(str(v['payment'])):
            res['partial'] = True
            res['payment_currency'] = (v['payment_currency'] and (payment / rate)) or 0.0
        elif payment:
            res['partial'] = False
        elif payment_currency and Decimal(str(payment_currency)) != Decimal(str(v['payment_currency'])):
            res['partial'] = True
            res['payment'] = (v['payment'] and (payment_currency * rate)) or 0.0
        else:
            res['partial'] = False
        return {'value': res}

    def _get_payment(self, cr, uid, line_id, journal_id, rate, context={}):
        line_obj = self.pool.get('account.move.line')
        v = {'name': '/', 'payment':0.0, 'payment_currency':0.0, 'amount_to_pay': 0.0, 'amount_currency': 0.0, 'currency_id': False, 'payments_ids': False, 'partial': False}
        payments_all, payments_other = [], []
        amount, amount_currency = 0, 0
        if line_id:
            line = line_obj.browse(cr, uid, line_id)
            if line.reconcile_partial_id:
                payments_all += map(lambda x: x.id, line.reconcile_partial_id.line_partial_ids)
                payments_other = filter(lambda x: x not in [line.id], payments_all)
            if payments_all:
                for pay in line_obj.browse(cr, uid, payments_all):
                    amount += (pay.debit - pay.credit)
                    amount_currency += pay.amount_currency
            else:
                amount = (line.debit - line.credit)
                amount_currency = line.amount_currency
#            curr_obj = self.pool.get('res.currency')
            line = self.pool.get('account.move.line').browse(cr, uid, line_id)
            company_currency_id = line.account_id.company_id.currency_id.id
            journal_currency_id = self.pool.get('account.journal').browse(cr, uid, journal_id).currency.id
            if (journal_currency_id == line.currency_id.id == company_currency_id) or \
                ((journal_currency_id == company_currency_id) and not line.currency_id.id):
                payment = amount
                payment_currency = 0.0
            elif journal_currency_id == line.currency_id.id != company_currency_id:
                payment = amount
                payment_currency = amount_currency
            else:
                payment = amount_currency * rate
                payment_currency = amount_currency
#                payment = curr_obj.compute(cr, uid, line.currency_id.id, journal_currency_id, amount_currency, context={'date': date_pay})
            v['name'] = line.ref
            v['payment'] = round(payment, 2)
            v['payment_currency'] = round(payment_currency, 2)
            v['amount_to_pay'] = amount
            v['amount_currency'] = amount_currency
            v['currency_id'] = line.currency_id.id
            v['payments_ids'] = payments_other
            v['partial'] = False
        return v


multiple_payment_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

