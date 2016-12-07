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
import netsvc
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import pooler

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

import tools


class account_move_ietu_concept(osv.osv):
    _name = "account.move.ietu.concept"
    _description = "IETU Concept"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=32, required=True),
    }
account_move_ietu_concept()

class res_partner_operation_type(osv.osv):
    _name = "res.partner.operation.type"
    _description = "Operation Type"
res_partner_operation_type()

class account_move_fiscal(osv.osv):
    _name = "account.move.fiscal"
    _description = "Fiscal Entries"

    def __compute(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            r = self.pool.get('account.move.line').get_base(cr, uid, line.line_id, line.operation_type_id)
            iva = line.base * r['amount_iva']
            other = r['amount'] - (line.base + line.base * r['rate'])
            amount_before_retension = line.base + iva + other
            total = amount_before_retension + line.base * (0 + r['amount_ret_iva']) + line.base * (0 + r['amount_ret_isr'])
            res[line.id] = {
                'amount': r['amount'],
                'iva': iva,
                'other': other,
                'amount_before_retension': amount_before_retension,
                'retained_iva': line.base * r['amount_ret_iva'],
                'retained_isr': line.base * r['amount_ret_isr'],
                'total': total,
                'rate_id': (r['iva'].tax_id.id, r['iva'].tax_id.name),
                }
        return res

    _columns = {
        'move_id': fields.many2one('account.move', 'Move', ondelete="cascade", help="The move of this entry line.", required=True),
        'line_id': fields.many2one('account.move.line', 'Entries'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'amount': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Amount', multi='all',store=True),
        'rate_id': fields.function(__compute, method=True, type='many2one', relation='account.tax', string='IVA Rate', multi='all',store=True),
        'base': fields.float('Base', digits_compute=dp.get_precision('Account')),
        'ietu': fields.float('IETU', digits_compute=dp.get_precision('Account')),
        'iva': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='IVA', multi='all',store=True),
        'other': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Other Expenses', multi='all',store=True),
        'amount_before_retension': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Amount Before Retension', multi='all',store=True),
        'retained_iva': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Retained IVA', multi='all',store=True),
        'retained_isr': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Retained ISR', multi='all',store=True),
        'total': fields.function(__compute, digits_compute=dp.get_precision('Account'), method=True, string='Total', multi='all',store=True),
        'iva_payed_na': fields.float('IVA Payed not accredited', digits_compute=dp.get_precision('Account')),
        'applies': fields.boolean('Applies to IVA Control'),
        'operation_type_id': fields.many2one('res.partner.operation.type', 'Operation Type', required=True),
        'ietu_concept_id': fields.many2one('account.move.ietu.concept', 'IETU Concept'),
        'xfer_ids': fields.many2many('account.move.line', 'account_move_fiscal_xfer_rel', 'fiscal_id', 'xfer_id', 'Tax Transfer Lines'),
        'state': fields.selection([('untransfer','Untransfer'),('transfer','Transfer')], 'State', readonly=True),
    }


    _defaults = {
        'applies': 1,
        'state': 'untransfer',
    }
    def _journal_check(self, cr, uid, period_id, context=None):
        period = self.pool.get('account.period').browse(cr, uid, period_id)
        if period.state == 'done':
            raise osv.except_osv(_('Error !'), _('You can not add/modify entries in a closed journal.'))
        return True

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def button_applies(self, cr, uid, ids, context=None):
        for fiscal in self.browse(cr, uid, ids):
            applies = True
            if fiscal.applies:
                applies = False
            self.write(cr, uid, ids, {'applies': applies}) 
            if fiscal.xfer_ids:
                self.button_tax_unxfer(cr, uid, [fiscal.id])
                self.button_tax_xfer(cr, uid, [fiscal.id], context=None)
        return True

    def button_tax_unxfer(self, cr, uid, ids, context=None):
        for fiscal in self.browse(cr, uid, ids):
            self._journal_check(cr, uid, fiscal.line_id.period_id.id)
            if fiscal.xfer_ids:
                super(osv.osv, self.pool.get('account.move.line')).unlink(cr, uid, [x.id for x in fiscal.xfer_ids])
        self.write(cr, uid, [x.id for x in fiscal.move_id.fiscal_ids], {'state': 'untransfer'}) 
        return True

    def button_tax_xfer(self, cr, uid, ids, context=None):
        tax = {'iva':'iva', 'retained_iva':'ret_iva', 'retained_isr':'ret_isr'} # {field_name: tax_type,....}
        for this_fiscal in self.browse(cr, uid, ids):
            for fiscal in this_fiscal.move_id.fiscal_ids:
                if fiscal.state == 'transfer':
                    self.button_tax_unxfer(cr, uid, [fiscal.id])
        for t in tax.keys():
            credit_1, credit_2, debit_1, debit_2 = 0,0,0,0
            fiscal2xfer, xfer_ids = [], []
            for this_fiscal in self.browse(cr, uid, ids):
                self._journal_check(cr, uid, this_fiscal.line_id.period_id.id)
                for fiscal in this_fiscal.move_id.fiscal_ids:
                    if eval('fiscal.' + t) and fiscal.applies:
                        fiscal2xfer.append(fiscal)
                        amount = eval('fiscal.' + t)
                        if amount > 0 and fiscal.line_id.debit or amount < 0 and fiscal.line_id.credit:
                            credit_1 += (amount > 0 and amount) or -amount
                            debit_2 = credit_1
                        elif amount < 0 and fiscal.line_id.debit or amount > 0 and fiscal.line_id.credit:
                            debit_1 += (amount > 0 and amount) or -amount
                            credit_2 = debit_1
                if (credit_1 + credit_2 + debit_1 + debit_2):
                    xfer_ids = self._create_tax_xfer(cr, uid, fiscal2xfer, tax[t], credit_1, credit_2, debit_1, debit_2)
                if xfer_ids:
                    self.write(cr, uid, [x.id for x in this_fiscal.move_id.fiscal_ids], {'state': 'transfer', 'xfer_ids': map(lambda x: (4, x), xfer_ids)}) 
        return True

    def _create_tax_xfer(self, cr, uid, fiscal2xfer, tax_type, credit_1, credit_2, debit_1, debit_2, context=None):
        for fiscal in fiscal2xfer:
            if fiscal.line_id.account_id in fiscal.operation_type_id.account_ids:
                tax = filter(lambda x: x.tax_type == tax_type, fiscal.operation_type_id.tax_ids)[0]
            elif fiscal.line_id.account_id in fiscal.operation_type_id.account_income_ids:
                tax = filter(lambda x: x.tax_type == tax_type, fiscal.operation_type_id.tax_income_ids)[0]
            else:
                return []
        if not tax.from_account_id:
            return []
        vals = {
            'move_id': fiscal.line_id.move_id.id,
            'journal_id': fiscal.line_id.journal_id.id,
            'period_id': fiscal.line_id.period_id.id,
            'name': fiscal.line_id.name,
            'date': fiscal.line_id.date,
            'partner_id': fiscal.line_id.partner_id.id,
            'ref': fiscal.line_id.ref,
            'account_id': tax.from_account_id.id,
            'credit': credit_1,
            'debit': debit_1,
            'state': 'valid',
            'currency_id': False,
            }
        line_id_1 = super(osv.osv, self.pool.get('account.move.line')).create(cr, uid, vals, context=context)
        vals = {
            'move_id': fiscal.line_id.move_id.id,
            'journal_id': fiscal.line_id.journal_id.id,
            'period_id': fiscal.line_id.period_id.id,
            'name': fiscal.line_id.name,
            'date': fiscal.line_id.date,
            'partner_id': fiscal.line_id.partner_id.id,
            'ref': fiscal.line_id.ref,
            'account_id': tax.to_account_id.id,
            'credit': credit_2,
            'debit': debit_2,
            'state': 'valid',
            'currency_id': False,
            }
        line_id_2 = super(osv.osv, self.pool.get('account.move.line')).create(cr, uid, vals, context=context)
        return [line_id_1, line_id_2]

    def onchange_base(self, cr, uid, ids, base, context=None):
        if not base:
            return {'value':{'ietu': 0}}
        return {'value':{'ietu': base}}

    def onchange_applies(self, cr, uid, ids, applies, context=None):
        if applies:
            return {'value':{'applies': False}}
        return {'value':{'applies': True}}

    def onchange_operation(self, cr, uid, ids, operation_type_id, line_id, context=None):
        if not operation_type_id or not line_id:
            return {'value':{'base': 0, 'ietu': 0}}
        line = self.pool.get('account.move.line').browse(cr, uid, line_id)
        operation = self.pool.get('res.partner.operation.type').browse(cr, uid, operation_type_id)
        res = self.pool.get('account.move.line').get_base(cr, uid, line, operation)
        return {'value':{'base': res['base'],'ietu': res['base']}}

account_move_fiscal()


class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'fiscal_ids': fields.one2many('account.move.fiscal', 'move_id', 'Fiscal Entries'),
    }

account_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

