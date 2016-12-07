# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://www.bias.com.mx>). All Rights Reserved
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
    'name': 'AAIA',
    'version': '0.1',
    'category': 'Generic Modules/Product',
    'description': """ AAIA Module """,
    'author': 'BIAS',
    'depends': ['base', 'product', 'product_images_olbs','bias_product_related_cost'],
    'update_xml': [
        'security/aaia_security.xml',
        'security/ir.model.access.csv',
        'aaia_product_view.xml',
        'res_partner_view.xml',
        'wizard/applications_xml_view.xml',
        'aaia_wizard.xml'
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
