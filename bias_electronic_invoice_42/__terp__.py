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
    'name' : 'Electronic Invoice',
    'version' : '1.0',
    'author' : 'BIAS',
    'category' : 'Generic Modules/Accounting',
    'description': ''' Makes a WebService conection with Buzon Fiscal \
    Stores an xml of the invoice\
    Sotres a digital certificate of the invice
    ''',
    'depends' : ['base', 'account'],
    'update_xml' : [
        #'security/ir.model.access.csv',
        'invoice_view.xml',
        'res_company_view.xml',
        'account_invoice_workflow.xml',
        'partner_view.xml',
        'invoice_report.xml',
        'invoice_wizard.xml'
    ],
    'active': False,
    'installable': True,
#    'certificate': '0048234518886',
    
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:{

