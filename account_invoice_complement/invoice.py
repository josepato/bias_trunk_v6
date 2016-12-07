# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011
#        Pexego Sistemas Informáticos. (http://pexego.es) All Rights Reserved
#        Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import pooler

#----------------------------------------------------------
# PayMethod
#----------------------------------------------------------

#class invoice_paymethod(osv.osv):
#    _name = 'invoice.paymethod'
#    _description = 'Invoice Pay Method'
#    _columns = {
#        'name': fields.char('Name', size=64, required=True),
#        'code': fields.char('Code', size=14, required=False, ),
#        
#        }
#        
#invoice_paymethod()
#
#class invoice_bankname(osv.osv):
#    _name = 'invoice.bankname'
#    _description = 'Invoice Bank name'
#    _columns = {
#        'name': fields.char('Name', size=64, required=True),
#        'code': fields.char('Code', size=14, required=False, ),
#        
#        }
#        
#invoice_bankname()


class account_invoice(osv.osv):
    """
     Add fields complement for MX electronic invoice
    """
    _inherit = "account.invoice"
    
    _columns = {
        'invoice_peymethod': fields.selection([('unidentified','unidentified'),('Tarjeta de Credito o debito', 'Credit Card or debit'),('Transferencia Bancaria','Bank Tranfer'),('Efectivo','Cash')], 'Pay Method', required=False, help="Will change of invoice pay method."),
        'invoice_bankname': fields.selection([('unidentified','unidentified'),('Banamex', 'Banamex'),('BBVA Bancomer','BBVA Bancomer'),('HSBC','HSBC'),('Banorte', 'Banorte'),('Scotiabank Inverlat', 'Scotiabank Inverlat'),('Santander Serfin', 'Santander Serfin'),('Banejercito', 'Banejercito'),('AMEX', 'AMEX')], 'Bank institution', required=False, help="the name of institution bank."),
        'invoice_kindpay': fields.selection([('unidentified','unidentified'),('Credit Card', 'Credit Card '),('Bank Transfer','Bank Transfer'),('Cash','Cash')], 'pay kind', required=False, help="pay kind."),                                        
        'invoice_account_number': fields.char('Invoice account number', 64, required=False),                
	    }
    
    
account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
