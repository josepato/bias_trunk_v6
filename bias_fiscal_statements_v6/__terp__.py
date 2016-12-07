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
    'name': 'Bias Fiscal Statements',
    'version': '1.0',
    'category': 'Generic Modules/Account',
    'description': """ This Module add configurable fiscal statements reports """,
    'author': 'BIAS',
    'depends': ['account'],
    'update_xml': [
                   'security/ir.model.access.csv',
                   'fiscal_statements_view.xml',
                   'fiscal_statements_wizard.xml',
                   'fiscal_statements_report.xml',
                   ],
    'installable': True,
    'active': False,
#    'certificate': '0048234520729',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
