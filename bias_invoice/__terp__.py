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
    'name': 'Bias Invoice',
    'version': '1.0',
    'category': 'Generic Modules/Account',
    'description': """ Invoice modification cover:
* Add custom invoice 
* Modify invoice lines adding field deductions, this lines will be printed in spetial place in the invoice
* Modify paiment method adding capabilities of: 
    - Show the invoice amount y both currency
    - Pay invoice with diffenet rate            
    - Fill reference automaticaly""",
    'author': 'BIAS',
    'depends': ['account'],
    'update_xml': [
                "security/ir.model.access.csv",
                "account_invoice_view.xml",    
                "account_view.xml",    
                "account_invoice_wizard.xml",
                "account_invoice_report.xml"],
    'installable': True,
    'active': False,
    'certificate': '0048234519953',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
