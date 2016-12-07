##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging


#----------------------------------------------------------
# Stock Move Cost
#----------------------------------------------------------
class stock_move_cost(osv.osv):
    _name = "stock.move.cost"
    _description = "Stock Move Cost"
    _columns = {
        'name': fields.related('move_id', 'name', type='char', size=64, relation="stock.move", string="Name", store=True, readonly=True),
        'date': fields.related('move_id', 'date', type='datetime', relation="stock.move", string="Date", store=True, readonly=True),
        'product_id': fields.related('move_id', 'product_id', type='many2one', relation="product.product", store=True, string="Product"),
        'move_id': fields.many2one('stock.move', 'Move', required=True, readonly=True),
        'extra_cost': fields.float('Extra Cost Price', digits=(14,4), help="Fixed cost added by product each time it is recived in the stock location.", readonly=True),
        'related_cost': fields.float('Factor', digits=(14,4), readonly=True),
        'purchase_standard_price': fields.float('Std. Purchase Price', digits_compute=dp.get_precision('Account'), help="Product's standard cost based in purchase only.", readonly=True),
        'standard_price': fields.float('Cost Price', digits_compute=dp.get_precision('Account'), help="Product's cost for accounting stock valuation. It is the base price for the supplier price.", readonly=True),
        'last_cost': fields.float('Last Cost', digits_compute=dp.get_precision('Purchase Price'), help="Product's last cost.", readonly=True),
        'product_stock_qty': fields.float('Stock Qty', digits_compute=dp.get_precision('Product UoM'), readonly=True),
        'product_purchase_qty': fields.float('Purchase Qty', digits_compute=dp.get_precision('Product UoM'), readonly=True),
    }

stock_move_cost()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _related_cost(self, cr, uid, move):
        related_cost = 0
        extra_cost = 0
        res = {}
        if move.product_id.extra_cost:
            extra_cost += move.product_id.extra_cost
        if move.product_id.related_cost_ids:
            for rel in move.product_id.related_cost_ids:
                related_cost += rel.factor
                extra_cost += rel.extra_cost
        elif move.partner_id.related_cost_ids:
            for rel in move.partner_id.related_cost_ids:
                related_cost += rel.factor
                extra_cost += rel.extra_cost
        elif move.partner_id.category_id:
            for category in move.partner_id.category_id:
                if category.related_cost_ids:
                    for rel in category.related_cost_ids:
                        related_cost += rel.factor
                        extra_cost += rel.extra_cost
        res['related_cost'] = related_cost
        res['extra_cost'] = extra_cost
        res['first_cost'] = move.product_id.first_cost
        res['purchase_std_price'] = move.product_id.purchase_standard_price
        return res
    #
    # TODO: change and create a move if not parents
    #
    # FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!

    def _write_product_price(self, cr, uid, ids, partial_data, move, product, product_avail, qty, context=None):
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_currency = partial_data.get('product_currency',False)
        product_price = partial_data.get('product_price',0.0)
        product_uom = partial_data.get('product_uom',False)
        move_currency_id = move.company_id.currency_id.id
        new_price = currency_obj.compute(cr, uid, product_currency, move_currency_id, product_price)
        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)
        related_cost = self._related_cost(cr, uid, move)
        if product.qty_available <= 0:
            new_purchase_std_price = new_purchase_price = new_price
            new_std_price = new_price * (1 + related_cost['related_cost']) + related_cost['extra_cost']
        else:
            # Get the standard price
            new_purchase_price = new_price
            new_price = new_price * (1 + related_cost['related_cost']) + related_cost['extra_cost']
            amount_unit = product.price_get('standard_price', context)[product.id]
            new_std_price = ((amount_unit * product_avail[product.id]) + (new_price * qty))/(product_avail[product.id] + qty)
            new_purchase_std_price = related_cost['purchase_std_price'] and ((related_cost['purchase_std_price'] * product_avail[product.id])\
                                    + (new_purchase_price * qty))/(product_avail[product.id] + qty) or new_purchase_price
            # Write the field according to price type field
        product_obj.write(cr, uid, [product.id], {
            'standard_price': new_std_price, 
            'purchase_standard_price': new_purchase_std_price,
            'last_cost': new_purchase_price,
            'first_cost': related_cost['first_cost'] or new_purchase_price,
            })
        self.pool.get('stock.move.cost').create(cr, uid, {
            'move_id': move.id, 
            'standard_price': new_std_price,
            'purchase_standard_price': new_purchase_std_price,
            'extra_cost': related_cost['extra_cost'],
            'related_cost': related_cost['related_cost'],
            'last_cost': new_purchase_price,
            'product_stock_qty': product_avail[product.id],
            'product_purchase_qty': qty, 
            })
        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty = {}
            prodlot_ids = {}
            product_avail = {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), False)
                assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
            
                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available
                    if qty > 0:
                        self._write_product_price(cr, uid, ids, partial_data, move, product, product_avail, qty, context=None) 

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]

                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)

                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - product_qty,
                            'product_uos_qty':move.product_qty - product_qty, #TODO: put correct uos_qty
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
                for move in complete:
                    if prodlot_ids.get(move.id):
                        move_obj.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids[move.id]})
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)


            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

stock_picking()
# ----------------------------------------------------
# Move
# ----------------------------------------------------

#
# Fields:
#   location_dest_id is only used for predicting futur stocks
#
class stock_move(osv.osv):
    _inherit = "stock.move"
    # FIXME: needs refactoring, this code is partially duplicated in stock_picking.do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s'%(move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
            product_qty = partial_data.get('product_qty',0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom',False)
            product_price = partial_data.get('product_price',0.0)
            product_currency = partial_data.get('product_currency',False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                if qty > 0:
                    self.pool.get('stock.picking')._write_product_price(cr, uid, ids, partial_data, move, product, product_avail, qty, context=None) 
                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty' : move.product_qty - product_qty,
                        'product_uos_qty':move.product_qty - product_qty,
                    })


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],{'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]

stock_move()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
