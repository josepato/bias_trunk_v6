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

from datetime import datetime
from osv import osv, fields
from tools.translate import _
import netsvc
import time
import tools

class sale_shop_property(osv.osv):
    _name = "sale.shop.property"
    _description = "Sales Shop Property"
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'property_ids': fields.many2many('mrp.property', 'sale_shop_property_rel', 'shop_id', 'property_id', 'Properties'),
    }

sale_shop_property()


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def create(self, cr, uid, vals, context=None):
        if vals.get('order_id', False):
            order_id = self.pool.get('sale.order').browse(cr, uid, vals['order_id'])
            shop_id = self.pool.get('sale.order').browse(cr, uid, vals['order_id']).shop_id.id
            shop_property_ids = self.pool.get('sale.shop.property').search(cr, uid, [('shop_id','=',shop_id)])
            if shop_property_ids:
                property_ids = [x.id for x in self.pool.get('sale.shop.property').browse(cr, uid, shop_property_ids[0]).property_ids]
                vals['property_ids'] = [(6, 0, property_ids)]
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
