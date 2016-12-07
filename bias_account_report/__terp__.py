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
    'name': 'Bias Account Custom Report',
    'version': '1.0',
    'category': 'Generic Modules/Account',
    'description': """ Add custom report capabilities """,
    'author': 'BIAS',
    'depends': ['account', 'bias_fiscal_statements'],
    'update_xml': [
                   'security/ir.model.access.csv',
                   'custom_report_view.xml',
                   'custom_report_wizard.xml',
                   'financial_reports_wizard.xml',
                   'financial_reports_report.xml',
                   'custom_report_report.xml',
                   ],
    'installable': True,
    'active': False,
    'certificate': '0048234520147',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
