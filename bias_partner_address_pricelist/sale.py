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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order(osv.osv):
    _inherit = "sale.order"

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        delivery = self.pool.get('res.partner.address').browse(cr, uid, addr['delivery'])
        if delivery.property_product_pricelist:
            res['value']['pricelist_id'] = delivery.property_product_pricelist.id
        return res

    def onchange_partner_shipping_id(self, cr, uid, ids, shipping):
        if not shipping:
            return {}
        val = {}
        delivery = self.pool.get('res.partner.address').browse(cr, uid, shipping)
        if delivery.property_product_pricelist:
            val = {'pricelist_id': delivery.property_product_pricelist.id}
        return {'value': val}

sale_order()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
