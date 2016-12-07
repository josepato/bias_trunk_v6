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
    'name': 'Mexico - Plan Contable',
    'version': '1.0',
    'category': 'Localisation/Account Charts',
    'description': """
    This is the base module to manage the accounting chart for Belgium in Open ERP.

    After Installing this module,The Configuration wizard for accounting is launched.
    * We have the account templates which can be helpful to generate Charts of Accounts.
    * On that particular wizard,You will be asked to pass the name of the company,the chart template to follow,the no. of digits to generate the code for your account and Bank account,currency  to create Journals.
        Thus,the pure copy of Chart Template is generated.
    * This is the same wizard that runs from Financial Management/Configuration/Financial Accounting/Financial Accounts/Generate Chart of Accounts from a Chart Template.

    Wizards provided by this module:
    * Enlist the partners with their related VAT  and invoiced amounts.Prepares an XML file format.Path to access : Financial Management/Reporting/Listing of VAT Customers.
    * Prepares an XML file for Vat Declaration of the Main company of the User currently Logged in.Path to access : Financial Management/Reporting/Listing of VAT Customers.

    """,
    'author': 'BIAS',
    'depends': [ 
                    'account', 
                    #'account_report', 
                    'base_vat', 
                    'account_chart'
                ],
    'init_xml': [],
    'update_xml': [
                    'account_view.xml',
                    'res_country_state.xml',
                    'res_partner_title.xml',
                    'account_user_type.xml',
                    'account_pcmn_mx.xml', 
                    'account_tax.xml',
                    'l10n_mx_wizard.xml',
                    'l10n_mx_sequence.xml', 
                   ],
    'demo_xml': [
#                   'account.report.report.csv'
                ],
    'installable': True,
    'certificate': '0048234521602',
}
#                    'base_iban', 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
