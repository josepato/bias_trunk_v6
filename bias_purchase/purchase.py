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
#
#Bias Account / purchase order
#

from osv import osv
from osv import fields
from tools import config
import time
import netsvc


#----------------------------------------------------------
# Purchase Order
#----------------------------------------------------------


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    _columns = {
        'date_order':fields.date('Date', required=False, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)]}, help="Date on which this document has been created."),
        'partner_id':fields.many2one('res.partner', 'Supplier', required=False, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)]}, change_default=True),

        }

purchase_order_line()
