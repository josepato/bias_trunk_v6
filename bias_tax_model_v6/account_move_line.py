# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc
from osv import fields, osv
from tools.translate import _

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def create(self, cr, uid, vals, context=None, check=True):
        line_id = super(account_move_line, self).create(cr, uid, vals, context=context)
        # CREATE Fiscal Lines
        fiscal_obj = self.pool.get('account.move.fiscal')
        line = self.browse(cr, uid, line_id)
        if line.journal_id.type == 'bank':
            if line.partner_id and line.partner_id.operation_type_id:
                res = self.get_base(cr, uid, line, line.partner_id.operation_type_id)
                if res['base']:
                    data = {
                        'move_id': line.move_id.id,
                        'line_id': line.id,
                        'partner_id': line.partner_id.id, 
                        'operation_type_id': line.partner_id.operation_type_id.id, 
                        'ietu_concept_id': line.partner_id.ietu_concept_id.id,
                        'base': res['base'],
                        'ietu': res['base'],
                        }
                    fiscal_id = fiscal_obj.create(cr, uid, data, context=context)
                    fiscal = fiscal_obj.browse(cr, uid, fiscal_id)
                    if fiscal.operation_type_id.auto:
                        fiscal_obj.button_tax_xfer(cr, uid, [fiscal.id], context=None)
        return line_id

    def get_base(self, cr, uid, line, operation):
        iva = ret_iva = ret_isr = False
        amount_iva = amount_ret_iva = amount_ret_isr = amount = base = rate = 0.0
        if line.account_id in operation.account_ids:
            iva = filter(lambda x: x.tax_type == 'iva', operation.tax_ids)
            ret_iva = filter(lambda x: x.tax_type == 'ret_iva', operation.tax_ids)
            ret_isr = filter(lambda x: x.tax_type == 'ret_isr', operation.tax_ids)
            amount_iva = iva and iva[0].tax_id.amount or 0.0
            amount_ret_iva = ret_iva and ret_iva[0].tax_id.amount or 0.0
            amount_ret_isr = ret_isr and ret_isr[0].tax_id.amount or 0.0
            tax = amount_iva + amount_ret_iva + amount_ret_isr
            amount = line.debit - line.credit
            base = amount / (1 + tax)
        elif line.account_id in operation.account_income_ids:
            iva = filter(lambda x: x.tax_type == 'iva', operation.tax_income_ids)
            ret_iva = filter(lambda x: x.tax_type == 'ret_iva', operation.tax_income_ids)
            ret_isr = filter(lambda x: x.tax_type == 'ret_isr', operation.tax_income_ids)
            amount_iva = iva and iva[0].tax_id.amount or 0.0
            amount_ret_iva = ret_iva and ret_iva[0].tax_id.amount or 0.0
            amount_ret_isr = ret_isr and ret_isr[0].tax_id.amount or 0.0
            tax = amount_iva + amount_ret_iva + amount_ret_isr
            amount = line.credit - line.debit
            base = amount / (1 + tax)
        return {'iva':iva and iva[0], 'amount_iva': amount_iva, 'amount_ret_iva':amount_ret_iva, 'amount_ret_isr':amount_ret_isr, 
                'rate':rate, 'base':base, 'amount':amount}
    
account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
