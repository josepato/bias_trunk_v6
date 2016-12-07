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
    'name': 'Bias Import Files',
    'version': '1.0',
    'category': 'Generic Modules/Import Files',
    'description': """Imports or prepares files to be imported to the OpenERP""",
    'author': 'Bias',
    'depends': ['base'],
    'website': 'http://www.bias.com.mx',
    'update_xml': [
        #'security/time_machine_security.xml',
        #'security/ir.model.access.csv',
        'catalog_import_view.xml',
        'catalog_import_wizard.xml'
        ],
    'installable': True,
    'active': False,
    'certificate': '0000014636068',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
