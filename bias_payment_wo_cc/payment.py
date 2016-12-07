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

#
# The methods "check_vat_[a-z]{2}" are copyrighted:
#    - Cedric Krier.
#    - Bertrand Chenal
#    - B2CK
# 

from osv import osv
from osv import fields
import time
import netsvc
import xmlrpclib

#******************************************************************************************
#   Cheque Printing Configuration
#******************************************************************************************
class report_cheque(osv.osv):
	_name = 'report.cheque'
	_description = 'Report Cheque'

	_columns = {
        'name': fields.char('Name', size=64, required=True),
        'adjustment_x': fields.float('Adjustment x', required=False),
        'adjustment_y': fields.float('Adjustment y', required=False),
        'line_id': fields.one2many('report.cheque.line', 'report_id', 'Lines', readonly=False, ),
	}
	_defaults = {
	}

report_cheque()

class report_cheque_line(osv.osv):
    _name = 'report.cheque.line'
    _description = 'Report Cheque Line'

    _columns = {
		'report_id': fields.many2one('report.cheque','Report Cheque', required=1, help='.'),
		'field_id': fields.many2one('ir.model.fields', 'Field'),
       	'x': fields.float('Horizontal', required=True),
       	'y': fields.float('Vertical', required=True),
       	'size': fields.float('Size', required=False),
       	'angle': fields.float('Angle', required=False),
        'method': fields.selection([
            ('none','None'), 
            ('text.text','Amount to Text'), 
            ('text.moneyfmt','Money Format'), 
            ('text.formatLang','Mx Date Format')], 'Method', readonly=False, size=32),
        'font': fields.selection([
            ('Courier','Courier'), 
            ('Courier-Bold','Courier-Bold'), 
            ('Courier-BoldOblique','Courier-BoldOblique'), 
            ('Courier-Oblique','Courier-Oblique'), 
            ('Helvetica','Helvetica'), 
            ('Helvetica-Bold','Helvetica-Bold'), 
            ('Helvetica-BoldOblique','Helvetica-BoldOblique'), 
            ('Helvetica-Oblique','Helvetica-Oblique'), 
            ('Symbol','Symbol'), 
            ('Times-Bold','Times-Bold'), 
            ('Times-BoldItalic','Times-BoldItalic'), 
            ('Times-Italic','Times-Italic'), 
            ('Times-Roman','Times-Roman'), 
            ('ZapfDingbats','ZapfDingbats'), 
            ], 'Font', size=32),
    }

    _defaults = {
        'x': lambda *a: 5,
        'y': lambda *a: 5,
        'size': lambda *a: 10,
        'angle': lambda *a: 0,
        'font': lambda *a: 'Helvetica',
    }

report_cheque_line()

#******************************************************************************************
#   Payment Order
#******************************************************************************************
class payment_order(osv.osv):
    _inherit = 'payment.order'

    def get_wizard(self,type):
        logger = netsvc.Logger()
        logger.notifyChannel("warning", netsvc.LOG_WARNING,
                "No wizard found for the payment type '%s'." % type)
        return None

    def get_wizard_1(self,type):
        if type == 'chk':
            return 'bias_payment', 'wizard_create_cheque'
        elif type == 'exp':
            return 'bias_payment', 'wizard_create_export'
            
        logger = netsvc.Logger()
        logger.notifyChannel("warning", netsvc.LOG_WARNING,
                "No wizard found for the payment type '%s'." % type)
        return None

    def _total(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        for order in self.browse(cursor, user, ids, context=context):
            if order.mode and order.mode.balance_account_id:
                res[order.id] = order.mode and order.mode.balance_account_id.balance
            else:
                res[order.id] = 0.0
        return res

    _columns = {
    }

payment_order()

#******************************************************************************************
#   Bank Payment Export
#******************************************************************************************
class payment_export_file(osv.osv):
    _name = 'payment.export.file'
    _description = 'Payment Export File'
    _columns = {
        'name': fields.char('Name', size=32, required=True, readonly=False, ),
        'code': fields.char('Code', size=32, required=True, readonly=False, ),
        'date': fields.selection([
            ('ddmmyyyy','DDMMYYYY'), 
            ('mmddyyyy','MMDDYYYY'), 
            ('yyyymmdd','YYYYMMDD')], 'Type', readonly=False),
        'number': fields.selection([
            ('2','######00'), 
            ('3','#####000'), 
            ('4','####0000'), 
            ('5','###00000'), 
            ('6','##000000'), 
            ('7','#0000000'), ], 'Amount', readonly=False),
        'line_id': fields.one2many('payment.export.line', 'export_id', 'Fields', readonly=False),
        'other_bnk': fields.char('Other Bank Code', size=8),
        'same_bnk': fields.char('Same Bank Code', size=8),
   }

payment_export_file()

STD = [     ('line.operation','Operation'), 
            ('line.code_id','Code ID'), 
            ('payment.mode.bank_id.acc_number','Origin Account'), 
            ('line.bank_id.acc_number','Destiny Account'), 
            ('line.amount','Amount'), 
            ('line.name','Reference'), 
            ('line.communication','Dscription'), 
            ('currency_source','Currency Source'), 
            ('currency_dest','Currency Dest.'), 
            ('vat','VAT'), 
            ('tax','Tax'), 
            ('line.communication2','Partner email'), 
            ('line.date','Efective Date'), 
            ('line.partner_id.name','Payment Instruction')
]

class payment_export_line(osv.osv):
    _name = 'payment.export.line'
    _description = 'Payment Export File'
    def _col_get(self, cr, uid, context={}):
        result = []
        obj = self.pool.get('payment.export.line')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name','name'], context)
        return [(r['name'], r['name']) for r in res]
    _columns = {
        'name': fields.char('Name', size=32, required=True, readonly=False, ),
        'sequence': fields.integer('Sequence', required=True),
        'type': fields.selection([
            ('float','With Decimals'), 
            ('integer','Integer'), 
            ('char','Character'),
            ('date','Date')], 'Type', readonly=False),
        'zero': fields.selection([
            ('left','Add Zero Left'), 
            ('rigth','Add Zero Right'),
            ('sleft','Add Space Left'),
            ('srigth','Add Space Right'), ], 'Zero/Space', readonly=False),
        'std_field': fields.selection(STD, 'Standar Field', required=True),
        'length': fields.integer('Length', required=True),
        'start': fields.integer('Start', required=False),
        'end': fields.integer('End', required=False),
        'required': fields.boolean('Required'),
        'condition': fields.selection(STD, 'Condition', method=True, required=False, size=32),
        'operator': fields.selection([
            ('eq','=='), 
            ('gt','>'), 
            ('lt','<'), 
            ('in','In'), 
            ('nin','Not In')], 'Operator', readonly=False),
        'value': fields.char('Value', size=32, required=False),
        'notes': fields.text('Notes'),
        'export_id': fields.many2one('payment.export.file', 'Export', size=32, ondelete="cascade", readonly=True),
   }
    _defaults = {
        'sequence': lambda *a: 5,
    }
    _order = "sequence"

payment_export_line()

#******************************************************************************************
#   Payment Cheque
#******************************************************************************************
class payment_cheque(osv.osv):
    _name = 'payment.cheque'
    _description = 'Payment cheque'

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _reconciled(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            move_id = self.browse(cr, uid, id).move_id and self.browse(cr, uid, id).move_id
            rec = False
            if move_id:
                cr.execute('select reconcile_id from account_move_line where move_id=%s', (move_id.id,))
                rec = cr.fetchall()
                if not rec:
                    res[id] = rec
                    continue
                rec = bool(rec[-1][0])
            res[id] = rec
        return res

    def _sum_amount(self, cr, uid, ids, name, args, context):
        res = {}
        for chk in self.browse(cr, uid, ids):
            amount = 0.0
            for line in chk.line_id:
                amount += line.calc_amount
            res[chk.id] = amount
        return res

    _columns = {
        'number': fields.char('Cheque Number', size=32, required=False, readonly=True, ),
#        'amount': fields.float('Amount', required=False, digits=(14,4), readonly=True),
        'amount': fields.function(_sum_amount, method=True, string='Amount', type='float'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True ),
        'user_id': fields.many2one('res.users', 'User', help=""),
        'date': fields.date('Date', required=False),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'line_id': fields.one2many('payment.line', 'cheque_id', 'Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'partial_line_id': fields.many2many('account.move.line', 'payment_partial_rel', 'payment_line_id', 'line_id', 'Partial Payed Lines'),
        'state': fields.selection([('draft','Draft'), ('confirm','Confirmed'), ('done','Done'), ('printed','Printed'), ('cancel','Cancel')], 'Status', readonly=True),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'concept': fields.char('Concept', size=128, ),
        'payment_order_id': fields.many2one('payment.order', 'Payment Order'),
        'writeoff_acc_id': fields.many2one('account.account', 'Writeoff Account'),
        'writeoff_journal_id': fields.many2one('account.journal', 'Writeoff Journal', required=False, select=1),
        'mode': fields.many2one('payment.mode','Payment mode', select=True, required=1, states={'done':[('readonly',True)]}, help='Select the Payment Mode to be applied.'),
        'move_id': fields.many2one('account.move', 'Entry', readonly=True),
        'reconciled': fields.function(_reconciled, method=True, string='Paid/Reconciled', type='boolean', help="The account moves of the cheque have been reconciled with account moves of the invoice(s)."),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'period_id': _get_period,
        'user_id': lambda self,cr,uid,context: uid,
    }

    def onchange_line_id(self, cr, uid, ids, line_id, context=None):
        res = {}
        if 1 == 2:
            res['value']['partial_line_id'] = []
        return res

    def onchange_mode(self, cr, uid, ids, mode, context=None):
        if not mode:
            res = {'value': {'currency_id': False}}
        else:
            res = {'value': {'currency_id': self.pool.get('payment.mode').browse(cr, uid, mode).journal.currency.id}}
        return res

    #
    # TODO: Check if period is closed !
    #
    def create(self, cr, uid, vals, context={}):
        cheque_id = super(payment_cheque, self).create(cr, uid, vals, context)
        cheque = self.browse(cr,uid,cheque_id)
        amount = 0.0
        for line in cheque.line_id:
            amount += line.amount
        self.write(cr,uid,cheque_id,{'amount': amount})
        return cheque_id

    def _get_cheque_number(self, cr, uid, cheque):
        number = cheque.number
        if not number:
            try:
                sequence = cheque.mode.journal.invoice_sequence_id.code
                number = self.pool.get('ir.sequence').get(cr, uid, sequence)
                self.write(cr,uid,cheque.id,{'number':number})
            except:
                raise osv.except_osv(_('Advertencia!'), _('Define el consecutivo de la chequera en el diario %s !')%cheque.mode.journal.name)
        return number        

    def action_open(self, cr, uid, ids, data=False, context={}, *args):
        move_line_obj = self.pool.get('account.move.line')
        values, values_pay, values_payed = {},{},{}
        for cheque in self.browse(cr, uid, ids):
            payed_lines = lines = []
            amount_currency_1, amount_currency_2 = False, False
            amount = 0.0
            if not cheque.number:
                number = self._get_cheque_number(cr, uid, cheque)
            else:
                number = cheque.number
            actual_period_id = self.pool.get('account.period').find(cr, uid, context=context)[0]
            company_currency_id = cheque.mode.journal.default_credit_account_id.company_currency_id.id
            journal_currency_id = cheque.mode.journal.currency and cheque.mode.journal.currency.id or company_currency
            currency_id = cheque.mode.journal.currency.id != company_currency_id and cheque.mode.journal.currency.id or False
            period_id = self.pool.get('account.period').find(cr, uid, cheque.date)[0]
            debit = credit = amount_currency = 0
            ref = ''
            move = {'ref': ref, 'journal_id': cheque.mode.journal.id, 'period_id': period_id, 'date': cheque.date, 'type': 'bank_pay_voucher'}
            move_id = self.pool.get('account.move').create(cr, uid, move)
            for line in cheque.line_id:
                payment = line.calc_amount
                line_currency_id = False
                if line.move_line_id and (journal_currency_id == line.move_line_id.currency_id.id != company_currency_id):
                        payment = line.amount_currency * line.pay_rate
                        line_currency_id = line.move_line_id.currency_id.id
                l1 = {
                    'debit': payment>0 and payment or 0.0,
                    'credit': payment<0 and payment or 0.0,
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id.id,
                    'ref': line.move_line_id and line.move_line_id.ref or number,
                    'date': line.date,
                    'currency_id': line_currency_id,
                    'amount_currency': currency_id and line.amount_currency,
                    'journal_id': cheque.mode.journal.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': line.move_line_id and line.move_line_id.name or cheque.concept or 'CHK-'
                }
                debit += l1['credit']
                credit += l1['debit']
                amount_currency += line.amount_currency
                ref += (ref and ',') + l1['ref']
                values[line.id] = l1
                values_payed[line.id] = line.move_line_id
            l2 = {
                    'debit': debit,
                    'credit': credit,
                    'account_id': cheque.mode.journal.default_credit_account_id.id,
                    'partner_id': line.partner_id.id,
                    'ref': ref,
                    'date': line.date,
                    'currency_id': currency_id,
                    'amount_currency': currency_id and amount_currency * -1,
                    'journal_id': cheque.mode.journal.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': line.move_line_id and ref or cheque.concept or 'CHK-'
            }
            for key in values.keys():
                line_id = move_line_obj.create(cr, uid, values[key])
                values_pay[key] = line_id
            line_id = self.pool.get('account.move.line').create(cr, uid, l2)
            self.pool.get('account.move').write(cr, uid, [move_id], {'ref': ref})
            for key in values.keys():
                if not values_payed[key]:
                    if cheque.mode.writeoff_acc_id:
                        writeoff_acc_id = cheque.mode.writeoff_acc_id.id
                    else:
                        raise osv.except_osv(_('Advertencia!'), _('Define las cuentas de ajuste en el modo de pago %s !')%cheque.mode.name)
                elif journal_currency_id == company_currency_id and values_payed[key].currency_id.id in (company_currency_id, False):
                    if cheque.mode.writeoff_acc_id:
                        writeoff_acc_id = cheque.mode.writeoff_acc_id.id
                    else:
                        raise osv.except_osv(_('Advertencia!'), _('Define las cuentas de ajuste en el modo de pago %s !')%cheque.mode.name)
                else:
                    if cheque.mode.gain_acc_id and cheque.mode.loss_acc_id:
                        writeoff_acc_id = cheque.mode.loss_acc_id.id
                        if (abs(values_payed[key].debit - values_payed[key].credit) - abs(values[key]['debit'] - values[key]['credit'])) >= 0:
                            writeoff_acc_id = cheque.mode.gain_acc_id.id
                    else:
                        raise osv.except_osv(_('Advertencia!'), _('Define las cuentas de ajuste en el modo de pago %s !')%cheque.mode.name)
                if values_payed[key]:
                    lines2reconcile = [values_pay[key], values_payed[key].id]
                    if values_payed[key].reconcile_partial_id:
                        lines2reconcile += [x.id for x in values_payed[key].reconcile_partial_id.line_partial_ids]
                        lines2reconcile = [x for x in set(lines2reconcile)]
                    if self.pool.get('payment.line').browse(cr, uid, key).partial:
                        move_line_obj.reconcile_partial(cr, uid, lines2reconcile, 'manual', context)
                    else:
                        context['comment'] = values_payed[key].ref
                        move_line_obj.reconcile(cr, uid, lines2reconcile, 'manual', writeoff_acc_id, actual_period_id, cheque.mode.writeoff_journal_id.id, context)
            self.pool.get('account.move').post(cr, uid, [move_id])
            self.write(cr, uid, cheque.id, {'amount': abs(debit-credit),'state': 'done','move_id': move_id})
        return move_id

    def action_confirm(self, cr, uid, ids, *args):
        for cheque in self.browse(cr,uid,ids):
            if not cheque.line_id:
                raise osv.except_osv(_('Error!'), _('No hay lineas de pago !'))
            self.write(cr,uid,cheque.id,{'state':'confirm'})
        return True

    def action_draft(self, cr, uid, ids, *args):
        for cheque in self.browse(cr,uid,ids):
            self.write(cr,uid,cheque.id,{'state':'draft'})
        return True

    def _trans_unrec(self, cr, uid, ids, context={}):
        recs = self.pool.get('account.move.line').read(cr, uid, ids, ['reconcile_id',])
        recs = filter(lambda x: x['reconcile_id'], recs)
        rec_ids = [rec['reconcile_id'][0] for rec in recs]
        result = []
        if len(rec_ids):
            cr.execute("""SELECT DISTINCT(m.id) FROM account_move m LEFT JOIN account_move_line l ON (l.move_id = m.id)
            WHERE l.reconcile_id IN %s """, ((tuple(rec_ids)),))
            result = [x[0] for x in cr.fetchall()]
            self.pool.get('account.move.reconcile').unlink(cr, uid, rec_ids)
        return result

    def action_cancel(self, cr, uid, ids, *args):
        move_obj = self.pool.get('account.move')
        for chk in self.browse(cr, uid, ids):
            if chk.move_id:
                move_obj.button_cancel(cr, uid, [chk.move_id.id])
                payed_moves = [x.move_line_id.move_id.id for x in filter(lambda x: x.move_line_id and not x.partial, chk.line_id)]
                writeoff_moves = self._trans_unrec(cr, uid, [x.id for x in chk.move_id.line_id])
                if writeoff_moves:
                    for m in payed_moves + [chk.move_id.id]:
                        move = move_obj.browse(cr, uid, m)
                        advance = [x.id for x in filter(lambda x: x.account_id.user_type.name == 'cash' and x.move_id.id != chk.move_id.id , move.line_id)]
                        if not advance:
                            writeoff_moves.remove(m)
                
                move_obj.unlink(cr, uid, [chk.move_id.id] + writeoff_moves)
        self.write(cr, uid, ids, {'state':'cancel'})#, 'line_id': False})
        return True
#                lines = filter(lambda x: x.reconcile_id, chk.move_id.line_id)
#                chk = self.browse(cr, uid, ids[0])
#                date = time.strftime('%Y-%m-%d')
#                l1 = {
#                'debit': 0,
#                'credit': 0,
#                'account_id': chk.mode.journal.default_debit_account_id.id,
#                'partner_id': chk.partner_id.id,
#                'ref': 'CHK '+chk.number + ' CANCELADO',
#                'name': 'CHK '+chk.number + ' CANCELADO',
#                }
#                move = {'ref':  'CHK '+chk.number + ' CANCELADO', 'journal_id': chk.mode.journal.id, 'line_id': [(0, 0, l1)]}#, 'period_id': period_id, #'date': date}
#                move_id = self.pool.get('account.move').create(cr, uid, move)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'state':'draft', 'number':False, 'line_id':False, 'move_id':False})
        if 'date' not in default:
            default['date'] = False
        return super(payment_cheque, self).copy(cr, uid, id, default, context)

#    def unlink(self, cr, uid, id, context=None):
#        print 'cheque unlink'
#        return super(payment_cheque, self).unlink(cr, uid, id, context)

payment_cheque()

#******************************************************************************************
#   Payment Line
#******************************************************************************************
class payment_line(osv.osv):
    _inherit = 'payment.line'

    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    def _line_rate(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            line = self.browse(cr, uid, id)
            res[id] = line.amount_currency and line.amount / line.amount_currency or 0.0
        return res

    def _amount(self, cursor, user, ids, name, args, context=None):
        if not ids:
            return {}
        currency_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if line.company_currency.id == line.currency.id:
                res[line.id] = line.calc_amount
            elif line.pay_rate != 1:
                res[line.id] = line.amount_currency * line.pay_rate
            else:    
                ctx = context.copy()
                ctx['date'] = line.order_id.date_done or time.strftime('%Y-%m-%d')
                res[line.id] = currency_obj.compute(cursor, user, line.currency.id,
                        line.company_currency.id,
                        line.amount_currency, context=ctx)
        return res

    def _reconciled(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            ok = False
            cr.execute("""select l.reconcile_id from payment_line p, account_move m, account_move_line l
    	    where p.id=%s and p.move_id = m.id and l.move_id = m.id """, (id,))
            result = cr.fetchall()
            if result:
                for reconcile in [x[0] for x in result]:
                    if bool(reconcile):
                        ok = True
            res[id] = ok
        return res

    _columns = {
        'order_id': fields.many2one('payment.order', 'Order', required=False, ondelete='cascade', select=True),
        'cheque_id': fields.many2one('payment.cheque', 'Cheque', ondelete="cascade", readonly=True),
        'amount': fields.function(_amount, string='Amount in Company Currency',
            method=True, type='float',
            help='Payment amount in the company currency'),
        'operation': fields.char('Operation', size=4),
        'code_id': fields.char('Code ID', size=16),
        'move_id': fields.many2one('account.move', 'Entry', readonly=False),
        'rate': fields.function(_line_rate, method=True, string="Rate", digits=(14,4)),
        'pay_rate': fields.float('Payment Rate', required=False, digits=(14,4)),
        'calc_amount': fields.float('Calc Amount', required=False, digits=(14,2)),
        'calc_currency': fields.many2one('res.currency','Company Currency',readonly=True),
        'account_id': fields.many2one('account.account', 'Account'),
        'partial': fields.boolean('Partial', help="Check this for partial payments."),
        'reconciled': fields.function(_reconciled, method=True, string='Reconciled', type='boolean', help="The account moves of the invoice have been reconciled with account moves of the payment(s)."),
        'amount_currency': fields.float('Amount in Partner Currency', digits=(16,2),
            required=False, help='Payment amount in the partner currency'),
    }
    _defaults = {
        'calc_currency': _get_currency,
    }

    def onchange_account_id(self, cr, uid, ids, concept, context=None):
        return {'value': {'communication': 'CHK-'+(concept or '') or 'CHK'}}

    def onchange_amount(self, cr, uid, ids, amount, currency, cmpny_currency, pay_rate = False, context=None):
        res = super(payment_line,self).onchange_amount(cr, uid, ids, amount, currency, cmpny_currency, context)
        res['value']['calc_amount'] = res['value']['amount']
        if pay_rate and pay_rate != 1:
            res['value']['calc_amount'] = amount * pay_rate
            res['value']['amount'] = amount * pay_rate
        return res

    def onchange_rate(self, cr, uid, ids, amount_currency, company_currency, currency, date, pay_rate):
        cur_obj = self.pool.get('res.currency')
        if company_currency == currency:
            return {}
        if pay_rate:
            amount = amount_currency * pay_rate
        else:
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency], 'rate', arg=None, context={'date':date})[company_currency]
            amount = cur_obj.compute(cr, uid, currency, company_currency, amount_currency, context={'date':date})
        return {'value':{'calc_amount': amount, 'pay_rate': pay_rate}}

    def onchange_partner(self,cr,uid,ids,partner_id,payment_type,context=None):
        data={}
        data['info_partner']=data['bank_id']=False

        if partner_id:
            part_obj=self.pool.get('res.partner').browse(cr,uid,partner_id)
            partner=part_obj.name or ''

            if part_obj.address:
                for ads in part_obj.address:
                    if ads.type=='default':
                        st=ads.street and ads.street or ''
                        st1=ads.street2 and ads.street2 or ''

                        if 'zip_id' in ads:
                            zip_city= ads.zip_id and self.pool.get('res.partner.zip').name_get(cr,uid,[ads.zip_id.id])[0][1] or ''
                        else:
                            zip=ads.zip and ads.zip or ''
                            city= ads.city and ads.city or  ''
                            zip_city= zip + ' ' + city

                        cntry= ads.country_id and ads.country_id.name or ''
                        info=partner + "\n" + st + " " + st1 + "\n" + zip_city + "\n" +cntry

                        data['info_partner']=info
            if part_obj.bank_ids and payment_type:
                bank_type = self.pool.get('payment.mode').suitable_bank_types(cr, uid, payment_type, context=context)
                for bank in part_obj.bank_ids:
                    if bank.state in bank_type:
                        data['bank_id'] = bank.id
                        data['code_id'] = bank.name
                        break

        return {'value': data}

    def onchange_bank_id(self, cr, uid, ids, partner_id, bank_id, mode, move_line_id, context={}):
        if not bank_id:
            return {'value': {'code_id': False}}
        bank_obj = self.pool.get('res.partner.bank')
        mode_obj = self.pool.get('payment.mode')
        code_id = bank_obj.browse(cr, uid, bank_id).name
        if bank_obj.browse(cr,uid,bank_id).bank == mode_obj.browse(cr,uid,mode).bank_id.bank:
            operation = mode_obj.browse(cr,uid,mode).payment_export_id.same_bnk
        else:
            operation = mode_obj.browse(cr,uid,mode).payment_export_id.other_bnk
        return {'value': {'code_id': code_id, 'operation': operation}}

    def default_get(self, cr, uid, fields, context={}):
        data = super(payment_line, self).default_get(cr, uid, fields, context)
        if 'partner_id' in fields and 'partner_id' in context:
            data['partner_id']=context['partner_id']
        if 'date' in fields and 'date' in context:
            data['date']=context['date']
        if 'communication' in fields and 'concept' in context:
            data['communication']=context['concept']
        return data

payment_line()

#******************************************************************************************
#   Payment mode
#******************************************************************************************

class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = {
        'statement_account_id': fields.many2one('account.account', 'Statement Account'),
        'transit_account_id': fields.many2one('account.account', 'Transit Account'),
        'available_account_id': fields.many2one('account.account', 'Available Account'),
        'payment_export_id': fields.many2one('payment.export.file', 'Export File'),
        'writeoff_acc_id': fields.many2one('account.account', 'Writeoff Account'),
        'writeoff_journal_id': fields.many2one('account.journal', 'Writeoff Journal', required=False, select=1),
        'gain_loss_journal_id': fields.many2one('account.journal', 'Gain/Loss Journal', required=False, select=1),
        'gain_acc_id': fields.many2one('account.account', 'Gain Account'),
        'loss_acc_id': fields.many2one('account.account', 'Loss Account'),
        'report_cheque_id': fields.many2one('report.cheque', 'Report Cheque'),
   }

payment_mode()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
#    def onchange_partner_id(self, cursor, user, line_id, partner_id, type, currency_id, journal_id, account_id, context={}):
#        if not journal_id:
#            return
#        journal = self.pool.get('account.journal').browse(cursor, user, journal_id)
#        result = super(account_bank_statement_line,self).onchange_partner_id(cursor, user, line_id, partner_id, type, currency_id, context={})
#        if not partner_id:
#            return {'value': {'amount': 0.0, 'account_id': False}}
#        res_currency_obj = self.pool.get('res.currency')
#        res_users_obj = self.pool.get('res.users')

#        company_currency_id = res_users_obj.browse(cursor, user, user,
#                context=context).company_id.currency_id.id

#        if not currency_id:
#            currency_id = company_currency_id
#        if type == 'supplier':
#            result['value']['account_id'] = journal.credit_rec_acc.id or result['value']['account_id']
#        elif type == 'customer':
#            result['value']['account_id'] = journal.debit_rec_acc.id or result['value']['account_id']
#        account_id = result['value']['account_id']
#        cursor.execute('SELECT sum(debit-credit) \
#                FROM account_move_line \
#                WHERE (reconcile_id is null) \
#                    AND partner_id = %s \
#                    AND account_id=%s', (partner_id, account_id))
#        res = cursor.fetchone()
#        balance = res and res[0] or 0.0

#        balance = res_currency_obj.compute(cursor, user, company_currency_id,
#                currency_id, balance, context=context)
#        result['value']['amount'] = balance
#        return result

account_bank_statement_line()

class account_journal(osv.osv):
    _inherit="account.journal"

    _columns = {
#        'debit_rec_acc': fields.many2one('account.account', 'Debit Reconcile Acc.', domain="[('type','!=','view')]", help="Used as default account in for customer transaction in account statement population."),
#        'credit_rec_acc': fields.many2one('account.account', 'Credit Reconcile Acc.', domain="[('type','!=','view')]", help="Used as default account in for supplier transaction in account statement population."),
    }
account_journal()


#******************************************************************************************
#   Account Treasury
#******************************************************************************************
class account_global_treasury(osv.osv):
    _name = 'account.global.treasury'
    _description = 'Account Global Treasury'

    def _compute(self, cr, uid, ids, field_name, arg, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = fiscalyear_obj.find(cr, uid)
        context['fiscalyear'] = fiscalyear
        res = {}
        for treasure in self.browse(cr, uid, ids, context):
            res[treasure.id] = 0
            for line in treasure.line_ids:
                if field_name == 'statement_amount':
                    res[treasure.id] += line.statement_amount
                elif field_name == 'transit_amount':
                    res[treasure.id] += line.transit_amount
                elif field_name == 'available_amount':
                    res[treasure.id] += line.available_amount
                else:
                    res[treasure.id] += 0
        return res

    _columns = {
        'name': fields.char('Name', size=64),
        'company_id':fields.many2one('res.company','Company',required=True),
        'line_ids': fields.one2many('account.global.line', 'global_id', 'Bank Company Accounts'),
        'state': fields.selection([('draft','Draft'), ('done','Done')], 'Status', readonly=True),
		'statement_amount': fields.function(_compute, method=True, type='float', string='Cash in Bank'),
		'transit_amount': fields.function(_compute, method=True, type='float', string='Transit Payments'),
		'available_amount': fields.function(_compute, method=True, type='float', string='Cash Available'),
    }

    _defaults = {
        'state': lambda *a: 'draft',
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        if not company_id:
            return {'value': {'name': False}}
        return {'value': {'name': self.pool.get('res.company').browse(cr, uid, company_id).name}}

    def cancel(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'draft'})

    def confirm(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'done'})

    _sql_constraints = [
        ('treasury_company_uniq', 'unique (company_id)', 'The treasury must be unique per company !')
    ]

account_global_treasury()

class account_global_line(osv.osv):
    _name = "account.global.line"
    _description = "Global Treasury Line"

    def _compute(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = fiscalyear_obj.find(cr, uid)
        context['fiscalyear'] = fiscalyear
        for treasury in self.browse(cr, uid, ids, context):
            server = treasury.server
            port = treasury.port
            dbname = treasury.db
            user = treasury.login
            pwd = treasury.password
            try:
                rpc = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common'%(server,port))
                uid = rpc.login(dbname, user, pwd)
                rpc = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object'%(server,port))
                balance = rpc.execute(dbname, uid, pwd, 'account.treasury', 'read', [treasury.reg_id], \
                            ['statement_amount','transit_amount','available_amount'])
                res[treasury.id] = balance[0][field_name]
            except:
                res[treasury.id] = 0
        return res

    _columns = {
        'name': fields.char('Line Name', size=32),
        'global_id': fields.many2one('account.global.treasury', 'Global Treasury', required=True, select=True),
        'reg_id': fields.integer('Register ID'),
		'statement_amount': fields.function(_compute, method=True, type='float', string='Cash in Bank'),
		'transit_amount': fields.function(_compute, method=True, type='float', string='Transit Payments'),
		'available_amount': fields.function(_compute, method=True, type='float', string='Cash Available'),
        'url': fields.char('Server', size=64),
        'server': fields.char('Server', size=64),
        'port': fields.char('Port', size=5),
        'db': fields.char('Data Base', size=64),
        'login': fields.char('User Name', size=50),
        'password' : fields.char('Password', size=64),
    }
    _defaults = {
        'server': lambda *a: 'localhost',
        'port': lambda *a: '8069',
        'password' : lambda obj,cr,uid,context={} : '',
    }
    _sql_constraints = [
        ('treasury_line_uniq', 'unique (name)', 'The name line must be unique !')
    ]
account_global_line()

class account_treasury(osv.osv):
    _name = 'account.treasury'
    _description = 'Account Treasury'

    def _compute(self, cr, uid, ids, field_name, arg, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = fiscalyear_obj.find(cr, uid)
        context['fiscalyear'] = fiscalyear
        res = {}
        for treasure in self.browse(cr, uid, ids, context):
            res[treasure.id] = 0
            for line in treasure.line_ids:
                if field_name == 'statement_amount':
                    res[treasure.id] += line.statement_amount
                elif field_name == 'transit_amount':
                    res[treasure.id] += line.transit_amount
                elif field_name == 'available_amount':
                    res[treasure.id] += line.available_amount
        return res

    _columns = {
        'name': fields.char('Name', size=64),
        'company_id':fields.many2one('res.company','Company',required=True),
        'line_ids': fields.one2many('account.treasury.account', 'treasury_id', 'Bank Accounts'),
        'state': fields.selection([('draft','Draft'), ('done','Done')], 'Status', readonly=True),
		'statement_amount': fields.function(_compute, method=True, type='float', string='Cash in Bank'),
		'transit_amount': fields.function(_compute, method=True, type='float', string='Transit Payments'),
		'available_amount': fields.function(_compute, method=True, type='float', string='Cash Available'),
    }

    _defaults = {
        'state': lambda *a: 'draft',
    }
    _sql_constraints = [
        ('treasury_company_uniq', 'unique (company_id)', 'The treasury must be unique per company !')
    ]

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        if not company_id:
            return {'value': {'name': False}}
        return {'value': {'name': self.pool.get('res.company').browse(cr, uid, company_id).name}}

    def create_accounts(self,cr, uid, ids, context={}):
        mode_obj = self.pool.get('payment.mode')
        acc_obj = self.pool.get('account.treasury.account')
        mode_ids = mode_obj.search(cr, uid, [])
        for treasury_id in ids:
            acc_obj.unlink(cr, uid, acc_obj.search(cr, uid, [('treasury_id','=',treasury_id)]))
            for mode in mode_obj.browse(cr, uid, mode_ids, context):
                if not mode.journal.default_debit_account_id.reconcile:
                    acc_obj.create(cr, uid, {
                        'treasury_id': treasury_id,
                        'name': mode.name,
                        'mode': mode.id,
            		    'journal_id_statement': mode.journal.id,
                    })
        return self.write(cr, uid, ids, {'state': 'done'})

    def cancel(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'draft'})

account_treasury()

class account_treasury_account(osv.osv):
    _name = 'account.treasury.account'
    _description = 'Account Treasury Account'

    def _compute(self, cr, uid, ids, field_name, arg, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = fiscalyear_obj.find(cr, uid)
        context['fiscalyear'] = fiscalyear
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = 0
            if field_name == 'statement_amount':
                res[line.id] = line.mode.statement_account_id.balance
            if field_name == 'transit_amount':
                res[line.id] = line.mode.transit_account_id.balance
            if field_name == 'available_amount':
                res[line.id] = line.mode.available_account_id.balance
        return res

    _columns = {
        'name': fields.char('Name', size=64),
        'treasury_id': fields.many2one('account.treasury','Treasury', select=True, required=1),
        'mode': fields.many2one('payment.mode','Payment mode', select=True, required=1, help='Select the Payment Mode to be applied.'),
        'journal_id_statement': fields.many2one('account.journal', 'Bank Statement Journal', required=True, ondelete="cascade"),
        'statement_amount': fields.function(_compute, method=True, type='float', string='Cash in Bank'),
        'transit_amount': fields.function(_compute, method=True, type='float', string='Transit Payments'),
        'available_amount': fields.function(_compute, method=True, type='float', string='Cash Available'),
    }

account_treasury_account()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

