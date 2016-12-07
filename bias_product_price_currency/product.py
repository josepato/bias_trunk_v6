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

#----------------------------------------------------------
# Price List
#----------------------------------------------------------

class product_product(osv.osv):
    _inherit = "product.product"

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        ## Get the normal price product.product would get
        res = super(product_product, self).price_get(cr, uid, ids, ptype, context)
        for product in self.browse(cr, uid, ids):
            ## if the product has an assigned currency, change the result (assume result is in company.currency)
            if product.currency_id:
                res[product.id] = self.pool.get('res.currency').compute(cr, uid,
                                                                        product.currency_id.id,
                                                                        product.company_id.currency_id.id,
                                                                        res[product.id], round=False)
        return res

    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency')
        }

product_product()
