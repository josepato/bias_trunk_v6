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

import time
from osv import fields, osv
from tools.translate import _

from datetime import datetime
from dateutil.relativedelta import relativedelta

DT_FMT = '%Y-%m-%d %H:%M:%S'
TM_FMT = '%H:%M:%S'

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'delivery_time': fields.datetime('Delivery Time', help="First delivery time"),
        'delivery_spacing': fields.time('Delivery Spacing', help="Spacing between truck and truck (or delivery and delivery)."),
        'load_capacity': fields.float('Truck Capacity', help="Maximum truck load capacity"),
        'transfer_time': fields.time('Transfer Time', help="Estimated transfer time (to get at which time has to leave the truck)"),
    }

    def button_dummy(self, cr, uid, ids, context=None):
        self.check_delivery_information(cr, uid, ids, context)
        self.create_delivery_lines(cr, uid, ids, context)
        return True

    def create_delivery_lines(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('sale.order.line')
        so = self.browse(cr, uid, ids[0], context)
        for line in so.order_line:
            if line.product_id.categ_id.check_delivery:
                xfer = time.strptime(so.transfer_time, TM_FMT)
                delivery_time = (datetime.strptime(so.delivery_time, DT_FMT) - \
                                 relativedelta(hours=+xfer.tm_hour, minutes=+xfer.tm_min, seconds=+xfer.tm_sec)).strftime(DT_FMT)
                spacing = time.strptime(so.delivery_spacing, TM_FMT)
                qty_list = [so.load_capacity] * int(line.product_uom_qty/so.load_capacity) + \
                           [line.product_uom_qty - so.load_capacity*int(line.product_uom_qty/so.load_capacity)]
                while 0 in qty_list:
                    qty_list.remove(0)
                qty = qty_list.pop(0)

                res = line_obj.product_id_change(cr, uid, ids, so.pricelist_id.id, line.product_id.id, qty, line.product_uom.id, qty_uos=0, \
                    uos=line.product_uos.id, name='', partner_id=so.partner_id, lang=False, update_tax=True, date_order=False, packaging=False, \
                    fiscal_position=False, flag=False)
                line_obj.write(cr, uid, line.id, {'product_uom_qty':qty, 'delivery_time':line.delivery_time or delivery_time, 
                                                  'product_uos_qty':res['value']['product_uos_qty'], 'product_uos':res['value']['product_uos'],
                                                  'price_unit':res['value']['price_unit']})
                for qty in qty_list:
                    new_line_id = line_obj.copy(cr, uid, line.id)
                    delivery_time = (datetime.strptime(delivery_time, DT_FMT) + \
                                    relativedelta(hours=+spacing.tm_hour, minutes=+spacing.tm_min, seconds=+spacing.tm_sec)).strftime(DT_FMT)
                    res = line_obj.product_id_change(cr, uid, ids, so.pricelist_id.id, line.product_id.id, qty, line.product_uom.id, qty_uos=0, \
                        uos=line.product_uos.id, name='', partner_id=so.partner_id, lang=False, update_tax=True, date_order=False, packaging=False, \
                        fiscal_position=False, flag=False)
                    line_obj.write(cr, uid, new_line_id, {'product_uom_qty':qty, 'delivery_time':delivery_time or delivery_time, 
                                                  'product_uos_qty':res['value']['product_uos_qty'], 'product_uos':res['value']['product_uos'],
                                                  'price_unit':res['value']['price_unit']})
        return True

    def check_delivery_information(self, cr, uid, ids, context={}):
        so = self.browse(cr, uid, ids[0], context)
        check = False
        for line in so.order_line:
            if line.product_id.categ_id.check_delivery:
                check = True
        if not check:
            return True
        if so.delivery_time and (so.delivery_spacing!='00:00:00') and so.load_capacity and (so.transfer_time!='00:00:00'):
            self.create_delivery_lines(cr, uid, ids, context)
            return True
        fields = not so.delivery_time and 'Delivery Time' or ''
        fields += (not so.delivery_spacing or so.delivery_spacing=='00:00:00') and (fields and ', ' or '') + 'Delivery Spacing' or ''
        fields += not so.load_capacity and (fields and ', ' or '') +  'Truck Capacity' or ''
        fields += (not so.transfer_time or so.transfer_time=='00:00:00') and (fields and ', ' or '') + 'Transfer Time' or ''
        msg = "%s"%fields
        raise osv.except_osv(_('Missing Truck Delivery Information !'), _(msg))
        return False
        
    def action_ship_create(self, cr, uid, ids, *args):
        super(sale_order, self).action_ship_create(cr, uid, ids)
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        so = self.browse(cr, uid, ids[0], context={})
        for line in so.order_line:
            if line.product_id.categ_id.check_delivery:
                move_id = move_obj.search(cr, uid, [('sale_line_id','=',line.id)])
                move_obj.write(cr, uid, move_id, {'date':line.delivery_time, 'date_expected':line.delivery_time})
                proc_obj.write(cr, uid, line.procurement_id.id, {'date_planned':line.delivery_time})
        return True
        
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'delivery_time': fields.datetime('Departure Time', help="The time at which the truck has to go to deliver on time the product"),
    }
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

