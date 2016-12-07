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
    'name': 'Concrete Sale Order',
    'version': '1.0',
    'category': 'Generic Modules/Sale',
    'description': """ Add the following fields in Sales Order:

    * Sale Order/Delivery Time.- First delivery time.
    * Sale Order/Delivery Spacing.- Spacing between truck and truck (or delivery and delivery).
    * Sale Order/Truck Capacity.- Maximum truck load capacity.
    * Sale Order/Transfer Time.- Estimated transfer time (to get at which time has to leave the truck).
    * Sale Order Line/Departure Time.- The time at which the truck has to go to deliver on time the product.

With this information, the module will be able to calculate how many stock moves have to be done and the right time for trucks departure based in delivery information, when order is confirmed or button Compute is clicked module generated right number of stock moves.

The module calculates delivery time using the following formula:

    First Departure Time  = Delibery Time - Estimated Transfer Time
    Second Departure Time = First Departure Time + Spacing Between Truck
    Third Departure Time  = Second Departure Time + Spacing Between Truck
    And so on...

The number of deliveries is calculated whith the folowing formula:

    Delivery List = [ Load_Capacity * integer(Product_qty/Load_Capacity) + Product_qty - Load_Capacity*int(Product_qty/Load_Capacity) ]

    Load_Capacity = Maximum truck load capacity.
    Product_qty = Total product quantity in sale order.
    
On Sale Order confirmation, or when click button Compute, the concrete module will do the folowing:
    * Check if one or more order products belong to a category with Check_Delivery field set, if so, check if delivery_time, delivery_spacing, load_capacity, and transfer_time fields Truck Delivery Information Tab are set, if not, raise a error menssage 'Missing Truck Delivery Information !'.
    * If some product category have Check Delivery field set, then the concrete module create one sale order lines for each Truck Departure with product UOM / UOS quantities and departure time according delivery information defined in sale order. 
    * The corresponding date/time is set in stock moves and procurements.

""",
    'author': 'BIAS',
    'depends': ['sale'],
    'update_xml': [
        'sale_view.xml',
        'sale_workflow.xml',
        'product_view.xml',
                   ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
