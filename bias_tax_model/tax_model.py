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

#----------------------------------------------------------
# wizard_account_entry_tax_info
#----------------------------------------------------------
class wizard_account_entry_tax_info(osv.osv):
    _name = 'wizard.account.entry_tax_info'
    _description = 'wizard_account_entry_tax_info'
    
    def onchange_tax(self, cr, uid, ids, lines, label, amount=False, base=False, other=False, total=False, context={}):
        tax_amount = 0
        for l in lines:
            tax_amount += l[2]['active'] and l[2]['amount'] or 0
        if label == 'ietu':
            return {'value': {label: tax_amount}}
        dif_amount = amount - (base + tax_amount)
        dif_total = total + base + tax_amount + other
        return {'value': {label: tax_amount, 'dif_amount': dif_amount, 'dif_total':dif_total}}

    def onchange_amount(self, cr, uid, ids, base, tax, amount, other, total, context={}):
        dif_amount = amount - (base + tax)
        dif_total = total + base + tax + other
        return {'value': {'dif_amount': dif_amount, 'dif_total':dif_total}}

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {'value': {'tax_vat': False, 'property_account_position': False}}
        else:
            vat = self.pool.get('res.partner').browse(cr, uid, partner_id).vat
            fiscal = self.pool.get('res.partner').browse(cr, uid, partner_id).property_account_position.id
        return {'value': {'tax_vat': vat, 'property_account_position.id': fiscal}}

wizard_account_entry_tax_info()

#----------------------------------------------------------
# Account Tax Parameters
#----------------------------------------------------------
class account_tax_parameters(osv.osv):
    _name = "account.tax.parameters"
    _description = "Account Tax Parameters"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'third_party_type_ids': fields.one2many('third.party.type', 'tax_parameters_id', 'Third Party Type'),
        'third_party_operation_ids': fields.one2many('third.party.operation', 'tax_parameters_id', 'Third Party Operation'),
        'account_tax_ietu_ids': fields.one2many('account.tax.ietu.concept', 'tax_parameters_id', 'IETU Concept'),
        'tax_model': fields.one2many('account.tax.model', 'tax_parameters_id', 'Tax Model'),
        'amount': fields.many2many('account.account.type', 'account_amount_parameters_rel','parameter_id','account_type_id', 'Amount Accounts Types'),
        'base': fields.many2many('account.account.type', 'account_base_parameters_rel','parameter_id','account_type_id', 'Base Accounts Types'),
        'total': fields.many2many('account.account.type', 'account_total_parameters_rel','parameter_id','account_type_id', 'Total Accounts Types'),
        'ietu': fields.many2many('account.account.type', 'account_ietu_parameters_rel','parameter_id','account_type_id', 'IETU Accounts Types'),
        'tax': fields.many2many('account.account.type', 'account_tax_parameters_rel','parameter_id','account_type_id', 'Tax Accounts'),
        'other': fields.many2many('account.account.type', 'account_other_parameters_rel','parameter_id','account_id', 'Other Accounts'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }

    _defaults = {
    }
    _sql_constraints = [
        ('tax_parameters_company_uniq', 'unique (company_id)', 'The tax parameters of the must be unique per company !')
    ]

account_tax_parameters()

#----------------------------------------------------------
# Meta Data
#----------------------------------------------------------
class account_tax_meta(osv.osv):
    _name = "account.tax.meta"
    _description = "Account Tax Meta"

    _columns = {
        'serial': fields.char('Serial', size=32),
        'folio': fields.char('Sequence', size=32),
        'state': fields.char('State', size=32),
        'reference': fields.char('Reference', size=64),
        'move_id': fields.many2one('account.move', 'Entry'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'third_party_type': fields.char('Third Party Type', size=8),
        'ietu_concept': fields.char('IETU Concept', size=8),
        'amount': fields.float('Amount'),
        'base': fields.float('Base'),
        'ietu': fields.float('IETU'),
        'other': fields.float('Other'),
        'tax': fields.float('tax'),
        'total': fields.float('Total'),
        'diot': fields.boolean('DIOT'),
    }

account_tax_meta()

#----------------------------------------------------------
# Account Tax Model
#----------------------------------------------------------
class account_tax_model(osv.osv):
    _name = "account.tax.model"
    _description = "Account Tax Model"

    def _tax_get(self, cr, uid, context={}):
        obj = self.pool.get('account.account')
        type_id = self.pool.get('account.account.type').search(cr, uid, [('code','=','tax')])[0]
        ids = obj.search(cr, uid, [('user_type','=',type_id)])
        res = obj.read(cr, uid, ids, ['code','name'])
        return [(r['code'], r['code']+'-'+r['name']) for r in res]

    _columns = {
        'tax_parameters_id': fields.many2one('account.tax.parameters', 'Tax Parameter', required=True),
        'tax': fields.selection(_tax_get, 'Tax', size=32, required=True ),
        'xfer': fields.selection(_tax_get, 'Tranfer', size=32, required=True ),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': lambda *a: True,
    }

account_tax_model()

#----------------------------------------------------------
# Account Fiscal Tax
#----------------------------------------------------------
class account_tax_fiscal(osv.osv):
    _name = "account.tax.fiscal"
    _description = "Account Tax Fiscal"

    def _tax_get(self, cr, uid, context={}):
        obj = self.pool.get('account.account')
        type_id = self.pool.get('account.account.type').search(cr, uid, [('code','=','tax')])[0]
        ids = obj.search(cr, uid, [('user_type','=',type_id)])
        res = obj.read(cr, uid, ids, ['code','name'])
        return [(r['code'], r['code']+'-'+r['name']) for r in res]

    _columns = {
        'move_id': fields.many2one('account.move', 'Entry', required=True),
        'line_id': fields.many2one('account.move.line', 'Line', required=False),
        'tax': fields.selection(_tax_get, 'Tax', size=32, required=False ),
        'xfer': fields.selection(_tax_get, 'Xfer', size=32, required=False ),
        'amount': fields.float('Amount', required=False),
        'active': fields.boolean('Active'),
        'name': fields.char('Name', size=64, required=True),
    }

    _defaults = {
        'active': lambda *a: True,
    }

    def default_get(self, cr, uid, fields, context={}):
        data = super(account_tax_fiscal, self).default_get(cr, uid, fields, context)
        if 'move_id' in fields and 'move_id' in context:
            data['move_id'] = context['move_id']
        return data

account_tax_fiscal()

#----------------------------------------------------------
# Account Tax IETU
#----------------------------------------------------------
class account_tax_ietu(osv.osv):
    _name = "account.tax.ietu"
    _description = "Account Tax IETU"

    _columns = {
        'move_id': fields.many2one('account.move', 'Entry', required=True),
        'line_id': fields.many2one('account.move.line', 'Line', required=True),
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'amount': fields.float('Amount', required=False),
        'active': fields.boolean('Active'),
        'name': fields.char('Name', size=64, required=True),
    }

    _defaults = {
        'active': lambda *a: True,
    }

    def default_get(self, cr, uid, fields, context={}):
        data = super(account_tax_ietu, self).default_get(cr, uid, fields, context)
        if 'move_id' in fields and 'move_id' in context:
            data['move_id'] = context['move_id']
        return data

account_tax_ietu()

#----------------------------------------------------------
# IETU Concept
#----------------------------------------------------------
class account_tax_ietu_concept(osv.osv):
    _name = "account.tax.ietu.concept"
    _description = "Tax IETU Concept"

    def _tax_get(self, cr, uid, context={}):
        ids = self.search(cr, uid, [])
        res = self.read(cr, uid, ids, ['code','name'])
        return [(r['code'], r['code']+'-'+r['name']) for r in res]

    _columns = {
        'tax_parameters_id': fields.many2one('account.tax.parameters', 'Tax Parameter', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
    }

account_tax_ietu_concept()

#----------------------------------------------------------
# Account Bank Entries
#----------------------------------------------------------
class account_bank_entries(osv.osv):
    _name = "account.bank.entries"
    _description = "Account Bank Entries"

    def __compute(self, cr, uid, ids, field_names, arg, context={}):
        result = {}
        query = """SELECT b.id, SUM(l.debit) - SUM(l.credit) AS amount
                FROM account_bank_entries b
                LEFT JOIN account_move m ON (b.bank_move_id = m.id)
                LEFT JOIN account_move_line l ON (l.move_id = m.id) 
                LEFT JOIN account_account a ON (l.account_id = a.id) 
                LEFT JOIN account_account_type t ON (a.user_type = t.id) 
                WHERE t.code = 'cash' AND b.id IN ("""+",".join(map(str, ids))+""") GROUP BY b.id"""
        cr.execute(query)
        for res in cr.dictfetchall():
            result[res['id']] = res
        res = {}
        for id in ids:
            res[id] = result[id]['amount']
        return res

    def _get_partner(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.bank_move_id.line_id and rec.bank_move_id.line_id[0].partner_id.id
        return result

    def _get_vat(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.bank_move_id.line_id and rec.bank_move_id.line_id[0].partner_id.vat
        return result

    _columns = {
        'name': fields.char('Line Name', size=32, required=True),
        'bank_move_id': fields.many2one('account.move', 'Bank Entry', required=True, select=True),
        'date': fields.date('Date', required=True),
        'amount': fields.function(__compute, digits=(16, 2), method=True, string='Amount'),
        'partner_id': fields.function(_get_partner, method=True, type='many2one', relation='res.partner', string='Partner'),
        'vat': fields.function(_get_vat, method=True, type="char", string='VAT'),
    }
    _order = 'date,bank_move_id'

account_bank_entries()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

