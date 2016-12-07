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
                amount += line.amount_currency
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
        'line_id': fields.one2many('payment.cheque.line', 'cheque_id', 'Lines', readonly=True, states={'draft':[('readonly',False)]}),
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
                sequence = cheque.mode.cheque_sequence_id.code
                number = self.pool.get('ir.sequence').get(cr, uid, sequence)
                self.write(cr,uid,cheque.id,{'number':number})
            except:
                raise osv.except_osv(('Advertencia!'), ('Define el consecutivo de la chequera en el diario %s !')%cheque.mode.journal.name)
        return number        

    def action_open(self, cr, uid, ids, data=False, context={}, *args):
        move_line_obj = self.pool.get('account.move.line')
        values, values_pay, values_payed = {},{},{}
        for cheque in self.browse(cr, uid, ids):
            payed_lines = lines = []
            amount_currency = 0
            amount, debit, credit = 0.0, 0, 0
            if not cheque.number:
                number = self._get_cheque_number(cr, uid, cheque)
            else:
                number = cheque.number
            actual_period_id = self.pool.get('account.period').find(cr, uid, context=context)[0]
            company_currency_id = cheque.mode.journal.default_credit_account_id.company_currency_id.id
            journal_currency_id = cheque.mode.journal.currency and cheque.mode.journal.currency.id or company_currency_id
            currency_id = cheque.mode.journal.currency.id != company_currency_id and cheque.mode.journal.currency.id or False
            period_id = self.pool.get('account.period').find(cr, uid, cheque.date)[0]
            ref = ''
            move = {'journal_id': cheque.mode.journal.id, 'period_id': period_id, 'date': cheque.date, 'type': 'bank_pay_voucher'}
#            move = {'name': 'CHK'+number, 'journal_id': cheque.mode.journal.id, 'period_id': period_id, 'date': cheque.date}
            move_id = self.pool.get('account.move').create(cr, uid, move)
            for line in cheque.line_id:
                payment = line.amount_currency
                line_currency_id = False
                if line.move_line_id and (journal_currency_id == line.move_line_id.currency_id.id != company_currency_id):
                        payment = line.amount_currency
                        line_currency_id = line.move_line_id.currency_id.id
                elif line.move_line_id and (journal_currency_id == company_currency_id != line.move_line_id.currency_id.id):
                        payment = line.amount_currency
                        line_currency_id = line.move_line_id.currency_id.id
                reference = (line.ml_inv_ref and line.ml_inv_ref.reference) and line.ml_inv_ref.reference or line.move_line_id and \
                            line.move_line_id.ref or number
                l1 = {
                    'debit': payment>0 and payment or 0.0,
                    'credit': payment<0 and payment or 0.0,
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id.id,
        		    'ref': reference,
                    'date': line.date,
                    'currency_id': currency_id,
                    'amount_currency': currency_id and line.amount_currency,
                    'journal_id': cheque.mode.journal.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': reference
                }
                debit += l1['credit']
                credit += l1['debit']
                amount_currency += line.amount_currency
                ref += (ref and ',') + l1['ref']
                values[line.id] = l1
                values_payed[line.id] = line.move_line_id
                line_id = move_line_obj.create(cr, uid, l1)
                values_pay[line.id] = line_id
                move_line_obj.write(cr, uid, [line_id], {'ref': reference})
                print 'line=',move_line_obj.browse(cr, uid, line_id).ref
            l2 = {
                    'debit': debit,
                    'credit': credit,
                    'account_id': cheque.mode.journal.default_credit_account_id.id,
                    'partner_id': line.partner_id.id,
                    'ref': 'CHK'+number,
                    'date': line.date,
                    'currency_id': currency_id,
                    'amount_currency': currency_id and amount_currency * -1,
                    'journal_id': cheque.mode.journal.id,
                    'period_id': period_id,
                    'move_id': move_id,
                    'name': 'CHK'+number
            }
#            for key in values.keys():
#                line_id = move_line_obj.create(cr, uid, values[key])
#                print key, values.keys(), values
#                values_pay[key] = line_id
#                move_line_obj.write(cr, uid, [line_id], {'ref': values[key]['ref']})
#                print 'line=',move_line_obj.browse(cr, uid, line_id).ref
            line_id = move_line_obj.create(cr, uid, l2)
            move_line_obj.write(cr, uid, [line_id], {'ref': ref})
            print 'line=',move_line_obj.browse(cr, uid, line_id).ref
#            self.pool.get('account.move').write(cr, uid, [move_id], {'ref': ref})
            for key in values.keys():
                if not values_payed[key]:
                    if cheque.mode.writeoff_acc_id:
                        writeoff_acc_id = cheque.mode.writeoff_acc_id.id
                    else:
                        raise osv.except_osv(('Advertencia!'), ('Define las cuentas de ajuste en el modo de pago %s !')%cheque.mode.name)
                elif journal_currency_id == company_currency_id and values_payed[key].currency_id.id in (company_currency_id, False):
                    if cheque.mode.writeoff_acc_id:
                        writeoff_acc_id = cheque.mode.writeoff_acc_id.id
                    else:
                        raise osv.except_osv(('Advertencia!'), ('Define las cuentas de ajuste en el modo de pago %s !')%cheque.mode.name)
                else:
                    if cheque.mode.gain_fluc_acc and cheque.mode.loss_fluc_acc:
                        writeoff_acc_id = cheque.mode.loss_fluc_acc.id
                        if (abs(values_payed[key].debit - values_payed[key].credit) - abs(values[key]['debit'] - values[key]['credit'])) >= 0:
                            writeoff_acc_id = cheque.mode.gain_fluc_acc.id
                    else:
                        raise osv.except_osv(('Advertencia!'), ('Define las cuentas de ajuste en el diario %s !')%cheque.mode.journal.name)
                if values_payed[key]:
                    lines2reconcile = [values_pay[key], values_payed[key].id]
                    if values_payed[key].reconcile_partial_id:
                        lines2reconcile += [x.id for x in values_payed[key].reconcile_partial_id.line_partial_ids]
                        lines2reconcile = [x for x in set(lines2reconcile)]
                    if self.pool.get('payment.cheque.line').browse(cr, uid, key).partial:
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
                raise osv.except_osv(('Error!'), ('No hay lineas de pago !'))
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
#   Payment Cheque Line
#******************************************************************************************
class payment_cheque_line(osv.osv):
    _name = 'payment.cheque.line'
    _description = 'Payment Cheque Line'

    def _line_rate(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            line = self.browse(cr, uid, id)
            ml = line.move_line_id
            res[id] = ml and ml.amount_currency and abs((ml.debit - ml.credit) / ml.amount_currency) or 1
        return res

    def _residual(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            res[id] = self.browse(cr, uid, id).move_line_id and self.browse(cr, uid, id).move_line_id.amount_to_pay
        return res

    def _get_ml_maturity_date(self, cr, uid, ids, *a):
        res={}
        for id in self.browse(cr, uid, ids):
            if id.move_line_id:
                res[id.id] = id.move_line_id.date_maturity
            else:
                res[id.id] = ""
        return res

    def _get_ml_inv_ref(self, cr, uid, ids, *a):
        res={}
        for id in self.browse(cr, uid, ids):
            res[id.id] = False
            if id.move_line_id:
                if id.move_line_id.invoice:
                    res[id.id] = id.move_line_id.invoice.id
        return res

    _columns = {
        'cheque_id': fields.many2one('payment.cheque', 'Cheque', required=False, ondelete="cascade"),
        'partial': fields.boolean('Partial', help="Check this for partial payments."),
        'account_id': fields.many2one('account.account', 'Account',required=True),

        'rate': fields.function(_line_rate, method=True, string="Rate", digits=(14,4)),
        'pay_rate': fields.float('Payment Rate', required=False, digits=(14,4)),

        'amount': fields.float('Amount in Company Currency', digits=(14,2), help='Payment amount in the company currency'),
        'amount_document': fields.float('Document', readonly=True, digits=(14,2), help='''Document's Total Amount'''),
        'amount_currency': fields.float('Payment', digits=(16,2), required=True, help='Payment amount in document currency'),
        'date': fields.date('Payment Date',help="If no payment date is specified, the bank will treat this payment line directly"),
        'partner_id': fields.many2one('res.partner', string="Partner",required=True,help='The Ordering Customer'),
        'company_currency': fields.many2one('res.currency','Company Currency',readonly=True),
        'move_line_id': fields.many2one('account.move.line','Entry line', domain=[('reconcile_id','=', False), ('account_id.type', '=','payable')],help='This Entry Line will be referred for the information of the ordering customer.'),
        'ml_maturity_date': fields.function(_get_ml_maturity_date, method=True, type='date', string='Maturity Date'),
        'ml_inv_ref': fields.function(_get_ml_inv_ref, method=True, type='many2one', relation='account.invoice', string='Invoice Ref.'),
        'currency': fields.many2one('res.currency','Document Currency',required=False),
    }

    _defaults = {
    }

    def onchange_account_id(self, cr, uid, ids, concept, context=None):
        return {'value': {'communication': 'CHK-'+(concept or '') or 'CHK'}}

    def onchange_rate(self, cr, uid, ids, amount_currency, company_currency, currency, date, pay_rate):
        cur_obj = self.pool.get('res.currency')
        if company_currency == currency:
            return {'value':{'amount': amount_currency, 'pay_rate': 1}}
        if pay_rate:
            amount = amount_currency * pay_rate
        else:
            pay_rate = cur_obj._current_rate(cr, uid, [company_currency], 'rate', arg=None, context={'date':date})[company_currency]
            amount = cur_obj.compute(cr, uid, currency, company_currency, amount_currency, context={'date':date})
      
        return {'value':{'amount': amount, 'pay_rate': pay_rate}}

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
        data = super(payment_cheque_line, self).default_get(cr, uid, fields, context)
        if 'partner_id' in fields and 'partner_id' in context:
            data['partner_id']=context['partner_id']
        if 'date' in fields and 'date' in context:
            data['date']=context['date']
        if 'communication' in fields and 'concept' in context:
            data['communication']=context['concept']
        return data

payment_cheque_line()

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
        'cheque_sequence_id': fields.many2one('ir.sequence', 'Cheque Sequence', help="The sequence used for cheque numbers in this payment mode."),
#       moved to account.journal because are used in bank statements to
#        'gain_loss_journal_id': fields.many2one('account.journal', 'Gain/Loss Journal', required=False, select=1),
        'gain_fluc_acc': fields.many2one('account.account', 'Gain Account'),
        'loss_fluc_acc': fields.many2one('account.account', 'Loss Account'),
        'report_cheque_id': fields.many2one('report.cheque', 'Report Cheque'),
   }

    def create(self, cr, uid, vals, context=None):
        if not 'cheque_sequence_id' in vals or not vals['cheque_sequence_id']:
            seq_pool = self.pool.get('ir.sequence')
            seq_typ_pool = self.pool.get('ir.sequence.type')
            name = vals['name'][:6]+'CHK'+str(vals['company_id'])
            code = (vals['name'][:6]+str(vals['company_id'])).lower()
            types = {
                'name': name,
                'code': code
            }
            seq_typ_pool.create(cr, uid, types)
            seq = {
                'name': name,
                'code': code,
                'active': True,
                'padding': 7,
                'number_increment': 1
            }
            sequence_id =  seq_pool.create(cr, uid, seq)
            vals.update({'cheque_sequence_id': sequence_id})
        return super(payment_mode, self).create(cr, uid, vals, context)

payment_mode()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

