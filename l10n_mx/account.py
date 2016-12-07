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


from osv import osv
from osv import fields

#----------------------------------------------------------
# Account Tax
#----------------------------------------------------------
class account_tax(osv.osv):
    _inherit = 'account.tax'
    
    _columns = {
        'amount': fields.float('Amount', required=True, digits=(14,9), help="For Tax Type percent enter % ratio between 0-1."),
        
    }
account_tax()

#----------------------------------------------------------
# Account Tax Code
#----------------------------------------------------------
class account_tax_code(osv.osv):
    _inherit = 'account.tax.code'

    _columns = {
        'account_debit_id': fields.many2one('account.account', 'Model Acc. debit', required=False, help="The account debit in the extra lines created after a reconcile."),
        'account_credit_id': fields.many2one('account.account', 'Model Acc. credit', required=False, help="The account credit in the extra lines created after a reconcile."),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Destination', help="If set, the reconcile process will create two extra line in bank entry to move tax from one account to the other."),
    }

account_tax_code()

#----------------------------------------------------------
# Account Tax Code Template
#----------------------------------------------------------
class account_tax_code_template(osv.osv):
    _inherit = 'account.tax.code.template'

    _columns = {
        'account_debit_id': fields.many2one('account.account', 'Model Acc. debit', required=False, help="The account debit in the extra lines created after a reconcile."),
        'account_credit_id': fields.many2one('account.account', 'Model Acc. credit', required=False, help="The account credit in the extra lines created after a reconcile."),
        'tax_code_id': fields.many2one('account.tax.code.template', 'Tax Destination', help="If set, the reconcile process will create two extra line in bank entry to move tax from one account to the other."),
    }

account_tax_code_template()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

