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

class res_partner(osv.osv):
    _inherit = "res.partner"

    def _third_party_type_get(self, cr, uid, ids=[], context={}):
        obj = self.pool.get('third.party.type')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['code','name'])
        return [(r['code'], r['code']+'-'+r['name']) for r in res]

    def _third_party_operation_get(self, cr, uid, ids=[], context={}):
        obj = self.pool.get('third.party.operation')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['code','name'])
        return [(r['code'], r['code']+'-'+r['name']) for r in res]

    _columns = {
        'curp': fields.char('CURP', size=64, required=False),
        'id_fiscal': fields.char('ID Fiscal', size=64, required=False),
        'third_party_type': fields.selection(_third_party_type_get,  'Third Party Type', size=32 ),
        'third_party_operation': fields.selection(_third_party_operation_get, 'Third Party Operation', size=32),
    }

    def init(self, cr):
        cr.execute("""delete from ir_module_module_dependency where id =
            (select d.id from ir_module_module_dependency d left join ir_module_module m on(d.module_id = m.id)
            where d.name='base_vat');
        """)

    def _check_duplicated_vat(self, cr, uid, ids):
        cr.execute("""SELECT MAX(id) FROM (SELECT COUNT(id) AS id FROM res_partner WHERE vat IS NOT NULL 
                GROUP BY replace(replace(replace(vat, '-', ''), ' ',  ''), chr(10), '')) AS id """)
        res = cr.fetchone()[0] == 1
        return res

    _constraints = [
        (_check_duplicated_vat, 'unique (vat), The VAT of the partner must be unique !', ['vat'])
    ]

    _sql_constraints = [
        ('curp_uniq', 'unique (curp)', 'The CURP of the partner must be unique !')
    ]

res_partner()

class third_party_type(osv.osv):
    _name = "third.party.type"
    _description = "Third Party Type"

    _columns = {
        'tax_parameters_id': fields.many2one('account.tax.parameters', 'Tax Parameter', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
    }

third_party_type()

class third_party_operation(osv.osv):
    _name = "third.party.operation"
    _description = "Third Party operation"

    _columns = {
        'tax_parameters_id': fields.many2one('account.tax.parameters', 'Tax Parameter', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
    }

third_party_operation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

