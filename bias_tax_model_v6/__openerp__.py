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
    'name': 'Bias Account',
    'version': '1.0',
    'category': 'Generic Modules/Account',
    'description': """ Tax Model:
- Open menu Sales/Configuration/Address Book/Operation Type and set:
- "Name" and "Code", 
- Set "Auto Tax Transfer" if you want create tax transfer entry lines when bank entry is created and the conditions set in operation type are fulfilled, else, only fiscal lines are created,
- "Tax Income Details" operate in bank journal input entries
- "Tax Outcome Details" operate in bank journal output entries
- In "Operation Tax" select Tax, Tax Type, 
- If you want tax transfer, fill "From Account" with the source account and "To Account" with the target account,
- In "Accounts Where Operation Apply", set all accounts that when payed, a fiscal entry must be created.
- Open Sale/Address Book/Customer and select a customer, now go to Accounting an select the "Operation Type" for this customer.
- Open Purchase/Address Book/Suppliers and select a supplier, now go to Accounting an select the "Operation Type" for this supplier.
- When a new bank journal entry is created, and a this entry have a partner set, and Operation Type is set in this partner, and this entry use some account from the "Accounts Where Operation Apply" set in partner operation type, the model creates new fiscal lines and if Auto Tax Transfer is set, it create the tax transfer lines to.
""",
    'author': 'BIAS',
    'depends': ['account'],
    'update_xml': [
        'security/ir.model.access.csv',
        'account_view.xml',
        'partner_view.xml',
                   ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
