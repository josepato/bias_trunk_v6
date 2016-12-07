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
#Bias Product / PriceList 
#
from osv import osv
from osv import fields
from tools import config
import time
import netsvc
import decimal_precision as dp

#----------------------------------------------------------
# Price List
#----------------------------------------------------------

class product_product(osv.osv):
    _inherit = "product.product"

    def _clon_price(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context=context):
		result[product.id] = product.standard_price or False
        return result

    _columns = {
        'extra_cost': fields.float('Extra Cost Price', digits=(14,4), help="Fixed cost added by product each time it is recived in the stock location."),
        'first_cost': fields.float('First Cost', digits_compute=dp.get_precision('Purchase Price'), help="Product's first cost."),
        'last_cost': fields.float('Last Cost', digits_compute=dp.get_precision('Purchase Price'), help="Product's last cost."),
        'purchase_standard_price': fields.float('Std. Purchase Price', digits_compute=dp.get_precision('Account'), help="Product's standard cost based in purchase only."),
        'clon_standard_price': fields.function(_clon_price, method=True, type='float', string='Cost Price', help="Product's standard cost based in purchase and related costs."),
        'related_cost_ids': fields.one2many('res.partner.related.cost.line', 'product_id', 'Related Cost'),
        }

product_product()
