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

class res_partner_type(osv.osv):
    _name = "res.partner.type"
    _description = "Partner Type"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=32, required=True),
    }
res_partner_type()

class res_partner_operation_type(osv.osv):
    _name = "res.partner.operation.type"
    _description = "Operation Type"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=32, required=True),
        'tax_ids':fields.one2many('res.partner.operation.tax', 'operation_id', 'Tax Application'),
        'tax_income_ids':fields.one2many('res.partner.operation.income.tax', 'operation_id', 'Tax Application'),
        'auto': fields.boolean('Auto Tax Transfer'),
        'account_ids': fields.many2many('account.account', 'res_partner_operation_tax_rel', 'xfer_id', 'account_id', 'Cash Journal Account'),
        'account_income_ids': fields.many2many('account.account', 'res_partner_operation_tax_income_rel', 'xfer_id', 'account_id', 'Cash Journal Account'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
res_partner_operation_type()

class res_partner_operation_tax(osv.osv):
    _name = "res.partner.operation.tax"
    _description = "Operation Outcome Tax"
    _columns = {
        'operation_id': fields.many2one('res.partner.operation.type', 'Operation', ondelete="cascade"),
        'from_account_id': fields.many2one('account.account', 'From Account', domain="[('type','!=','view')]"),
        'to_account_id': fields.many2one('account.account', 'To Account', domain="[('type','!=','view')]"),
        'tax_id': fields.many2one('account.tax', 'Tax'),
		'tax_type':fields.selection( [('',''),('iva','Transfer IVA'), ('ieps','Transfer IEPS'), ('ret_iva','Retention IVA'), ('ret_isr','Retention ISR')], 'Tax Type'),
    }
res_partner_operation_tax()

class res_partner_operation_income_tax(osv.osv):
    _name = "res.partner.operation.income.tax"
    _description = "Operation Income Tax"
    _columns = {
        'operation_id': fields.many2one('res.partner.operation.type', 'Operation', ondelete="cascade"),
        'from_account_id': fields.many2one('account.account', 'From Account', domain="[('type','!=','view')]"),
        'to_account_id': fields.many2one('account.account', 'To Account', domain="[('type','!=','view')]"),
        'tax_id': fields.many2one('account.tax', 'Tax'),
		'tax_type':fields.selection( [('',''),('iva','Transfer IVA'), ('ieps','Transfer IEPS'), ('ret_iva','Retention IVA'), ('ret_isr','Retention ISR')], 'Tax Type'),
    }
res_partner_operation_income_tax()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'curp': fields.char('CURP', size=32),
        'partner_type_id': fields.many2one('res.partner.type', 'Partner Type'),
        'operation_type_id': fields.many2one('res.partner.operation.type', 'Operation Type'),
        'ietu_concept_id': fields.many2one('account.move.ietu.concept', 'IETU Concept'),
    }
res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

