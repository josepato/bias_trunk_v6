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

from osv import osv
from osv import fields
import urllib,re
import random, time
from tools.translate import _

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'related_cost_ids': fields.one2many('res.partner.related.cost.line', 'product_id', 'Related Cost'),
    }

res_partner()

class res_partner_category(osv.osv):
    _inherit = 'res.partner.category'
    _columns = {
        'related_cost_ids': fields.one2many('res.partner.related.cost.line', 'product_id', 'Related Cost'),
    }

res_partner_category()


class res_partner_related_cost(osv.osv):### ADD a name constrain !!!!!!
    _order = 'name'
    _name = 'res.partner.related.cost'

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, user, [('code', '=ilike', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' '+name
            res.append((record['id'], name))
        return res

    _columns = {
        'factor': fields.float('Factor', digits=(14,4)),
        'extra_cost': fields.float('Extra Cost Price', digits=(14,4), help="Fixed cost added by product each time it is recived in the stock location."),
        'active': fields.boolean('Active'),
        'name': fields.char('Name', required=True, size=32),
        'code': fields.char('Code', required=True, size=16),
    }
    _defaults = {
        'active': lambda *args: 1
    }

res_partner_related_cost()

class res_partner_related_cost_line(osv.osv):
    _name = 'res.partner.related.cost.line'

    def _get_factor(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context=context):
		result[product.id] = product.relaed_cost_id.factor or False
        return result

    def _get_extra(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context=context):
		result[product.id] = product.relaed_cost_id.extra_cost or False
        return result

    _columns = {
        'factor': fields.function(_get_factor, method=True, type='float', digits=(14,4),  string='Factor'),
        'extra_cost': fields.function(_get_extra, method=True, type='float', digits=(14,4),  string='Extra Cost Price', help="Fixed cost added by product each time it is recived in the stock location."),
        'active': fields.boolean('Active'),
        'product_id': fields.many2one('res.partner', 'Product', required=True, select=True),
        'relaed_cost_id': fields.many2one('res.partner.related.cost', 'Related Cost', required=True, select=True),
    }
    _defaults = {
        'active': lambda *args: 1
    }
res_partner_related_cost_line()




