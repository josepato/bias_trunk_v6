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
#Bias Product / PriceList 
#
from osv import osv
from osv import fields
import time
import netsvc

#----------------------------------------------------------
# Price List
#----------------------------------------------------------

OLDPRINTSTR = """XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4^MD0^JUS^LRN^CI0^XZ
^XA
^MMT
^LL0142
^LS0
^FT246,119^A0N,17,16^FH\^FD%s^FS
^FT164,18^A0N,17,16^FH\^FD%s^FS
^FT286,110^A0B,17,16^FH\^FD%s^FS
^FT21,136^A0N,17,16^FH\^FD%s^FS
^FT4,123^A0N,17,16^FH\^FD%s^FS
^FT193,51^A0N,17,16^FH\^FD%s^FS
^FT4,67^A0N,17,16^FH\^FD%s/%s^FS
^FT3,51^A0N,17,16^FH\^FD%s/%s^FS
^FT3,34^A0N,17,16^FH\^FD%s^FS
^FT8,18^A0N,17,16^FH\^FD%s^FS
^PQ%i,0,1,Y^XZ"""

PRINTSTR = """^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4^MD0^JUS^LRN^CI0^XZ
^XA
^MMT
^LL0850
^LS0
^FT48,731^A0I,17,16^FH\^F%sB^FS
^FT131,831^A0I,17,16^FH\^FD%s^FS
^FT8,740^A0R,17,16^FH\^FD%s^FS
^FT273,713^A0I,17,16^FH\^FD%s^FS
^FT290,727^A0I,17,16^FH\^FD%s^FS
^FT101,799^A0I,17,16^FH\^FD%s^FS
^FT291,782^A0I,17,16^FH\^FD%s/%s^FS
^FT291,799^A0I,17,16^FH\^FD%s/%s^FS
^FT291,815^A0I,17,16^FH\^FD%s^FS
^FT287,832^A0I,17,16^FH\^FD%s^FS
^BY1,3,22^FT291,755^BCI,,Y,N
^FD>:LA>50001>6BB^FS
^PQ%i,0,1,Y^XZ"""


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def getZebraData(self, cr, uid, ids):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        move_obj = self.pool.get('stock.move')
        for picking in self.browse(cr, uid, ids):
            mydict = {'id': picking.id}
            mylines = []
            for move in picking.move_lines:
                mystr = PRINTSTR %(move.product_id.product_writing_kind_id.name,
                                   move.product_id.product_colection_id.name,
                                   move.product_id.default_code,
                                   move.product_id.product_tmpl_id.categ_id.parent_id.name,
                                   move.product_id.product_writing_metaerial_id.name,
                                   (move.product_id.product_hardware_ids and move.product_id.product_hardware_ids[0].name) or "-",
                                   (move.product_id.product_top_material_ids and move.product_id.product_top_material_ids[0].name) or "-",
                                   (move.product_id.product_bottom_material_ids and move.product_id.product_bottom_material_ids[0].name) or "-",
                                   (move.product_id.product_top_color_ids and move.product_id.product_top_color_ids[0].name) or "-",
                                   (move.product_id.product_bottom_color_ids and move.product_id.product_bottom_color_ids[0].name) or "-",
                                   move.product_id.product_line_id.name,
                                   move.product_id.product_brand_id.name,
                                   move.product_qty)
                mylines.append(mystr)
            mydict['lines'] = mylines
            res.append(mydict)
        return res
            

stock_picking()
