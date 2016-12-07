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


{
    'name': 'Customization Bias',
    'version': '1.0',
    'category': 'Generic Modules/Prints',
    'description': """Bias Print Forms Module""",
    'author': 'BIAS',
    "website" : "http://www.bias.com.mx",
    "license" : "AGPL-3",
    'depends': ['base',
##                'account',
##                'product',
                  'mrp',
                  'purchase',
                  'purchase_delivery',
                  'stock',
                  'sale',
                ],
        'data': [
        'wizard/print_installer.xml',
    ],
    'update_xml': [
#        'security/ir.model.access.csv',
#        'point_of_sale/wizard/pos_borrowing.xml',
#        'product/product_view.xml',
#        'account/account_invoice_report.xml',
#        'partners/res_partners_view.xml',
         'mrp/mrp_report.xml',
         'purchase/purchase_report.xml',
         'stock/stock_report.xml',
         'sale/sale_report.xml'
                   ],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
