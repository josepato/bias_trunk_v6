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
#Bias Stock Kardex
#

from osv import osv
from osv import fields
from tools import config
import time
import netsvc

#----------------------------------------------------------
# Location Stock Kardex Report
#----------------------------------------------------------

class report_location_stock_kardex(osv.osv):

	_name = "report.location.stock.kardex"
	_description = "Location Stock Kardex Report"
	_auto = False
	_columns = {
		'name': fields.char("Product", size=128, required=True, select=True),
		'stock_from_date': fields.float('Initial Stock', select=True),
		'stock_move_in': fields.float('Stock In', select=True),
		'stock_move_out': fields.float('Stock Out', select=True),
		'stock_to_date': fields.float('Final Stock', select=True),
		'cost_from_date': fields.float('Initial Cost', select=True),
		'cost_move_in': fields.float('Cost In', select=True),
		'cost_move_out': fields.float('Cost Out', select=True),
		'cost_to_date': fields.float('Final Cost', select=True),
		
	}
#	_order = 'name desc,categ desc'
	def init(self, cr):

		cr.execute("""
						
			create or replace view report_location_stock_kardex as (

				select
					p.id as id,
		            pt.name as name,
					sum(sm.product_qty) as stock_from_date,
					sum(sm.product_qty) as stock_move_in,
					sum(sm.product_qty) as stock_move_out,
					sum(sm.product_qty) as stock_to_date,
                    (select
                        sum(aml.credit)
                    from account_move_line aml
                        inner join account_move am on (aml.move_id=am.id)
                        inner join stock_inventory_move_rel simr on (am.id=simr.move_id)
                        inner join stock_move sm on (sm.id=simr.inventory_id)
                    where
                        sm.product_id=p.id
                    ) as cost_from_date,
                    (select
                        sum(aml.credit)
                    from account_move_line aml
                        inner join account_move am on (aml.move_id=am.id)
                        inner join stock_inventory_move_rel simr on (am.id=simr.move_id)
                        inner join stock_move sm on (sm.id=simr.inventory_id)
                    where
                        sm.product_id=p.id
                    ) as cost_move_in,
                    (select
                        sum(aml.credit)
                    from account_move_line aml
                        inner join account_move am on (aml.move_id=am.id)
                        inner join stock_inventory_move_rel simr on (am.id=simr.move_id)
                        inner join stock_move sm on (sm.id=simr.inventory_id)
                    where
                        sm.product_id=p.id
                    ) as cost_move_out,
                    (select
                        sum(aml.credit)
                    from account_move_line aml
                        inner join account_move am on (aml.move_id=am.id)
                        inner join stock_inventory_move_rel simr on (am.id=simr.move_id)
                        inner join stock_move sm on (sm.id=simr.inventory_id)
                    where
                        sm.product_id=p.id
                    ) as cost_to_date

				from product_product p

					inner join product_template pt on (pt.id=p.product_tmpl_id)
					inner join stock_move sm on (sm.product_id=p.id)

				group by
					p.id, pt.name, sm.product_qty
				
			)
		""")


	def init_get_obj(self, cr):


		return


report_location_stock_kardex()

#----------------------------------------------------------
# Product Stock Kardex
#----------------------------------------------------------

class location_kardex(osv.osv):
    _name = "location.kardex"
    _description = "Location Stock Kardex"

    def _get_product_ids(self, cr, uid, ids, field_names=None, arg=False, context={}):

        res = {}

        for i in self.browse(cr, uid, ids):
            res[i.id] = []
            if i.name:
                location_ids = [i.name.id]
            else:
                location_ids = []
                wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
                for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                    location_ids.append(w.lot_stock_id.id)

            # build the list of ids of children of the location given by id
            if context.get('compute_child',True):
                child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
                location_ids= len(child_location_ids) and child_location_ids or location_ids
            else:
                location_ids= location_ids
            if i.from_date and i.to_date and i.from_date <= i.to_date:
                state = "'done'"
                date_str="date_planned>='%s' and date_planned<='%s'"%(i.from_date,i.to_date)
                sm_date_str="sm.date_planned>='%s' and sm.date_planned<='%s'"%(i.from_date,i.to_date)
                from_date="date_planned<'%s'"%(i.from_date)
                sm_from_date="sm.date_planned<'%s'"%(i.from_date)
                to_date="date_planned<'%s'"%(i.to_date)
                sm_to_date="sm.date_planned<'%s'"%(i.to_date)
                location_ids_str = ','.join(map(str, location_ids))
                prod_ids_str = ','.join(map(str, [i.name.id]))
                cr.execute(
                    'create or replace view report_location_stock_kardex as ( '\
                        'select '\
                            'p.id as id, '\
                            'pt.name as name, '\
                            'COALESCE ( '\
                                '( (select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id not in ('+location_ids_str+') '\
                                'and location_dest_id in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+from_date+' ) - '\
                                '( select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id in ('+location_ids_str+') '\
                                'and location_dest_id not in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+from_date+' ) '\
                                '), 0.0) as stock_from_date, '\
                            'COALESCE ( '\
                                '( select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id not in ('+location_ids_str+') '\
                                'and location_dest_id in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+date_str+' '\
                                '), 0.0) as stock_move_in, '\
                            'COALESCE ( '\
                                '( select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id in ('+location_ids_str+') '\
                                'and location_dest_id not in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+date_str+' '\
                                '), 0.0) as stock_move_out, '\
                            'COALESCE ( '\
                                '( (select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id not in ('+location_ids_str+') '\
                                'and location_dest_id in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+to_date+' ) - '\
                                '( select sum(sm.product_qty) '\
                                'from stock_move sm '\
                                'where location_id in ('+location_ids_str+') '\
                                'and location_dest_id not in ('+location_ids_str+') '\
                                'and product_id = p.id '\
                                'and state in ('+state+') '\
                                'and '+to_date+' ) '\
                                '), 0.0) as stock_to_date, '\
                        'COALESCE ( '\
                                '( (select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id not in ('+location_ids_str+') '\
                                'and sm.location_dest_id in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_from_date+' ) - '\
                                '(select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id in ('+location_ids_str+') '\
                                'and sm.location_dest_id not in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_from_date+' ) '\
                                '), 0.0) as cost_from_date, '\
                        'COALESCE ( '\
                                '(select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id not in ('+location_ids_str+') '\
                                'and sm.location_dest_id in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_date_str+' '\
                                '), 0.0) as cost_move_in, '\
                        'COALESCE ( '\
                                '(select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id in ('+location_ids_str+') '\
                                'and sm.location_dest_id not in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_date_str+' '\
                                '), 0.0) as cost_move_out, '\
                        'COALESCE ( '\
                                '( (select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id not in ('+location_ids_str+') '\
                                'and sm.location_dest_id in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_to_date+' ) - '\
                                '(select '\
                                    'sum (aml.credit) '\
                                    'from account_move_line aml '\
                                    'inner join account_move am on (aml.move_id=am.id) '\
                                    'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                                    'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                                'where sm.location_id in ('+location_ids_str+') '\
                                'and sm.location_dest_id not in ('+location_ids_str+') '\
                                'and sm.product_id = p.id '\
                                'and sm.state in ('+state+') '\
                                'and '+sm_to_date+' ) '\
                                '), 0.0) as cost_to_date '\
                        'from product_product p '\
                        'inner join product_template pt on (pt.id=p.product_tmpl_id) '\
                        'group by p.id, pt.name '\
                        ') '\

                    )
                obj_ids = self.pool.get('report.location.stock.kardex').search(cr, uid, [], context=context)
                res[i.id] = obj_ids
        return res

    _columns = {
#        'name': fields.many2one('product.product', 'Product', required=True),
        'name': fields.many2one('stock.location', 'Kardex Location', required=True),
        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),
        'product_ids': fields.function(_get_product_ids, type='one2many', obj="report.location.stock.kardex", method=True, string='Products'),
#        'stock_move_ids': fields.function(_get_stock_move_ids, type='one2many', obj="stock.move", method=True, string='Stock Move'),
#        'kardex_from_date': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Initial Stock', multi='stock_from_date'),
#        'cost_from_date': fields.function(_product_qty_kardex, method=True, type='float', string='Initial Stock Cost', multi='stock_from_date'),
#        'kardex_move_in': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Move In', multi='stock_from_date'),
#        'cost_move_in': fields.function(_product_qty_kardex, method=True, type='float', string='Move In Cost', multi='stock_from_date'),
#        'kardex_move_out': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Move Out', multi='stock_from_date'),
#        'cost_move_out': fields.function(_product_qty_kardex, method=True, type='float', string='Move Out Cost', multi='stock_from_date'),
#        'kardex_to_date': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Final Stock', multi='stock_from_date'),
#        'cost_to_date': fields.function(_product_qty_kardex, method=True, type='float', string='Final Stock Cost', multi='stock_from_date')

    }

    _defaults = {
 

    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The location must be unique !')
    ]

    def button_dummy(self, cr, uid, ids, context={}):
        return True

location_kardex()


#----------------------------------------------------------
# Product Stock Kardex
#----------------------------------------------------------

class stock_kardex(osv.osv):
    _name = "stock.kardex"
    _description = "Product Stock Kardex"

    def _get_stock_move_ids(self, cr, uid, ids, field_name, arg, context):

        res = {}

        for i in self.browse(cr, uid, ids):
            res[i.id] = []
            if i.kardex_location:
                location_ids = [i.kardex_location.id]
            else:
                location_ids = []
                wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
                for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                    location_ids.append(w.lot_stock_id.id)

            # build the list of ids of children of the location given by id
            if context.get('compute_child',True):
                child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
                location_ids= len(child_location_ids) and child_location_ids or location_ids
            else:
                location_ids= location_ids
            if i.from_date and i.to_date and i.from_date <= i.to_date:
                state = "'done'"
                date_str="date_planned>='%s' and date_planned<='%s'"%(i.from_date,i.to_date)
                location_ids_str = ','.join(map(str, location_ids))
                prod_ids_str = ','.join(map(str, [i.name.id]))
                cr.execute(
                    'select id '\
                    'from stock_move '\
                    'where (location_id in ('+location_ids_str+') '\
                    'or location_dest_id in ('+location_ids_str+')) '\
                    'and product_id in ('+prod_ids_str+') '\
                    'and state = ('+state+') and '+date_str+' '\
                    'order by date_planned '\
                    )
                results = cr.fetchall()
                move_ids = map(lambda x: x[0], results)
                res[i.id] = move_ids
        return res


    def _product_qty_kardex(self, cr, uid, ids, field_names=None, arg=False, context={}):

        if not field_names:
            field_names=[]
        if context.get('from_date',False):
            from_date = context['from_date']
            print 'from_date=',from_date
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for i in self.browse(cr, uid, ids):
            if i.from_date and i.to_date and i.from_date <= i.to_date:
                for f in field_names:
                    c = context.copy()
                    if f=='kardex_from_date':
                        c.update({ 'states':('done',), 'what':('in', 'out'), 'to_date':i.from_date, 'location':i.kardex_location.id })
                    if f=='cost_from_date':
                        c.update({ 'states':('done',), 'what':('in', 'out'), 'to_date':i.from_date, 'location':i.kardex_location.id, 'cost':True })
                    if f=='kardex_move_in':
                        c.update({ 'states':('done',), 'what':('in',), 'from_date':i.from_date, 'to_date':i.to_date, 'location':i.kardex_location.id })
                    if f=='cost_move_in':
                        c.update({ 'states':('done',), 'what':('in',), 'from_date':i.from_date, 'to_date':i.to_date, 'location':i.kardex_location.id, 'cost':True })
                    if f=='kardex_move_out':
                        c.update({ 'states':('done',), 'what':('out',), 'from_date':i.from_date, 'to_date':i.to_date, 'location':i.kardex_location.id })
                    if f=='cost_move_out':
                        c.update({ 'states':('done',), 'what':('out',), 'from_date':i.from_date, 'to_date':i.to_date, 'location':i.kardex_location.id, 'cost':True })
                    if f=='kardex_to_date':
                        c.update({ 'states':('done',), 'what':('in', 'out'), 'to_date':i.to_date, 'location':i.kardex_location.id })
                    if f=='cost_to_date':
                        c.update({ 'states':('done',), 'what':('in', 'out'), 'to_date':i.to_date, 'location':i.kardex_location.id, 'cost':True })
                    stock=self.pool.get('product.product').get_product_qty_kardex(cr,uid,[i.name.id,],context=c)
   
                    res[i.id][f] = stock.get(i.name.id, 0.0)
        return res

    _columns = {
        'name': fields.many2one('product.product', 'Product', required=True),
        'kardex_location': fields.many2one('stock.location', 'Kardex Location'),
        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),
        'stock_move_ids': fields.function(_get_stock_move_ids, type='one2many', obj="stock.move",
                                 method=True, string='Stock Move'),
        'kardex_from_date': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Initial Stock', multi='stock_from_date'),
        'cost_from_date': fields.function(_product_qty_kardex, method=True, type='float', string='Initial Stock Cost', multi='stock_from_date'),
        'kardex_move_in': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Move In', multi='stock_from_date'),
        'cost_move_in': fields.function(_product_qty_kardex, method=True, type='float', string='Move In Cost', multi='stock_from_date'),
        'kardex_move_out': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Move Out', multi='stock_from_date'),
        'cost_move_out': fields.function(_product_qty_kardex, method=True, type='float', string='Move Out Cost', multi='stock_from_date'),
        'kardex_to_date': fields.function(_product_qty_kardex, method=True, type='float', string='Kardex Final Stock', multi='stock_from_date'),
        'cost_to_date': fields.function(_product_qty_kardex, method=True, type='float', string='Final Stock Cost', multi='stock_from_date')

    }

    _defaults = {
 

    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The product must be unique !')
    ]

    def button_dummy(self, cr, uid, ids, context={}):
        return True

stock_kardex()

#----------------------------------------------------------
# Product Stock Kardex
#----------------------------------------------------------

class product_product(osv.osv):
    _inherit = "product.product"


    def get_product_qty_kardex(self,cr,uid,ids,context=None):
        if not context:
            context = {}
        states=context.get('states',[])
        what=context.get('what',())
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res
        if not context.get('cost'):
            cost = False
        else:
            cost = context['cost']

        if context.get('shop', False):
            cr.execute('select warehouse_id from sale_shop where id=%s', (int(context['shop']),))
            res2 = cr.fetchone()
            if res2:
                context['warehouse'] = res2[0]

        if context.get('warehouse', False):
            cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(context['warehouse']),))
            res2 = cr.fetchone()
            if res2:
                context['location'] = res2[0]

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
            for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids= len(child_location_ids) and child_location_ids or location_ids
        else:
            location_ids= location_ids

        states_str = ','.join(map(lambda s: "'%s'" % s, states))

        uoms_o = {}
        product2uom = {}
        for product in self.browse(cr, uid, ids, context=context):
            product2uom[product.id] = product.uom_id.id
            uoms_o[product.uom_id.id] = product.uom_id

        prod_ids_str = ','.join(map(str, ids))
        location_ids_str = ','.join(map(str, location_ids))
        results = []
        results2 = []

        from_date=context.get('from_date',False)
        to_date=context.get('to_date',False)
        if cost:
            sm = 'sm.'
        else:
            sm = ''
        date_str=False
        if from_date and to_date:
            date_str="%sdate_planned>='%s' and %sdate_planned<='%s'"%(sm,from_date,sm,to_date)
        elif from_date:
            date_str="%sdate_planned>'%s'"%(sm,from_date)
        elif to_date:
            date_str="%sdate_planned<'%s'"%(sm,to_date)

        if 'in' in what and not cost:
            # all moves from a location out of the set to a location in the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id not in ('+location_ids_str+') '\
                'and location_dest_id in ('+location_ids_str+') '\
                'and product_id in ('+prod_ids_str+') '\
                'and state in ('+states_str+') '+ (date_str and 'and '+date_str+' ' or '') +''\
                'group by product_id,product_uom'
            )
            results = cr.fetchall()
        if 'out' in what and not cost:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id in ('+location_ids_str+') '\
                'and location_dest_id not in ('+location_ids_str+') '\
                'and product_id in ('+prod_ids_str+') '\
                'and state in ('+states_str+') '+ (date_str and 'and '+date_str+' ' or '') + ''\
                'group by product_id,product_uom'
            )
            results2 = cr.fetchall()
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]

        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
        for o in uoms:
            uoms_o[o.id] = o
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]])
            res[prod_id] += amount
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]])
            res[prod_id] -= amount
        results3 = []
        results4 = []
        if cost:
            for i in ids:
                if 'in' in what and context.get('cost',True):
                    # the cost of all moves from a location out of the set to a location in the set
                    cr.execute(
                        'select sum(aml.credit) '\
                        'from account_move_line aml '\
                        'inner join account_move am on (am.id=aml.move_id) '\
                        'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                        'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                        'where sm.location_id not in ('+location_ids_str+') '\
                        'and sm.location_dest_id in ('+location_ids_str+') '\
                        'and sm.product_id in ('+prod_ids_str+') '\
                        'and sm.state in ('+states_str+') '+ (date_str and 'and '+date_str+' ' or '') + ''\
                        'group by sm.product_id'
                    )
                    results3 = cr.fetchall()
                    if results3:
                        res[i] += results3[0][0]
                if 'out' in what and context.get('cost',True):
                    # the cost of all moves from a location out of the set to a location in the set
                    cr.execute(
                        'select sum(aml.credit) '\
                        'from account_move_line aml '\
                        'inner join account_move am on (am.id=aml.move_id) '\
                        'inner join stock_kardex_rel skr on (am.id=skr.account_move_id) '\
                        'inner join stock_move sm on (sm.id=skr.stock_move_id) '\
                        'where sm.location_id in ('+location_ids_str+') '\
                        'and sm.location_dest_id not in ('+location_ids_str+') '\
                        'and sm.product_id in ('+prod_ids_str+') '\
                        'and sm.state in ('+states_str+') '+ (date_str and 'and '+date_str+' ' or '') + ''\
                        'group by sm.product_id'
                    )
                    results4 = cr.fetchall()
                    if results4:
                        res[i] -= results4[0][0]
           
        return res



    _columns = {


    }


product_product()

class stock_move(osv.osv):
    _inherit = "stock.move"


    def _account_move_hook(self, cr, uid, stock_move_id, account_move_id):
        '''Call after the creation of the account move'''
        super(stock_move, self)._account_move_hook(cr, uid, stock_move_id, account_move_id)
        sk_rel_id = self.pool.get('stock.kardex.rel').create(cr, uid, {
            'stock_move_id': stock_move_id,
            'account_move_id': account_move_id,
            })        
        return sk_rel_id

    def _qty_kardex(self, cr, uid, ids, field_names=None, arg=False, context={}):
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = []
            sk_id = self.pool.get('stock.kardex').search(cr, uid, [('name', '=', i.product_id.id)])
            sk_list = self.pool.get('stock.kardex').read(cr, uid, sk_id, ['name', 'kardex_location', 'from_date', 'to_date'])
            sk_list = sk_list[0]
            if sk_list['kardex_location']:
                location_ids = [sk_list['kardex_location'][0]]
            else:
                location_ids = []
                wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
                for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                    location_ids.append(w.lot_stock_id.id)
            
            # build the list of ids of children of the location given by id
            if context.get('compute_child',True):
                child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
                location_ids= len(child_location_ids) and child_location_ids or location_ids
            else:
                location_ids= location_ids
            if i.location_id.id in location_ids and i.location_dest_id.id in location_ids:
                res[i.id] = 0
            elif i.location_id.id in location_ids:
                res[i.id] = i.product_qty * -1
            else:
                res[i.id] = i.product_qty

        return res

    def _move_cost_kardex(self, cr, uid, ids, field_names=None, arg=False, context={}):
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = []
            sk_rel_id = self.pool.get('stock.kardex.rel').search(cr, uid, [('stock_move_id', '=', i.id)])
            if not sk_rel_id:
                continue
            sk_rel = self.pool.get('stock.kardex.rel').read(cr, uid, sk_rel_id,)
            sk_rel = sk_rel[0]
            am_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id', '=', sk_rel['account_move_id'])])
            m_cost = self.pool.get('account.move.line').read(cr, uid, am_line_ids[0], ['credit', 'debit'])
            m_cost = m_cost['credit'] or m_cost['debit']
            sk_id = self.pool.get('stock.kardex').search(cr, uid, [('name', '=', i.product_id.id)])
            sk_list = self.pool.get('stock.kardex').read(cr, uid, sk_id, ['name', 'kardex_location', 'from_date', 'to_date'])
            sk_list = sk_list[0]
            if sk_list['kardex_location']:
                location_ids = [sk_list['kardex_location'][0]]
            else:
                location_ids = []
                wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
                for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                    location_ids.append(w.lot_stock_id.id)
            
            # build the list of ids of children of the location given by id
            if context.get('compute_child',True):
                child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
                location_ids= len(child_location_ids) and child_location_ids or location_ids
            else:
                location_ids= location_ids
            if i.location_id.id in location_ids and i.location_dest_id.id in location_ids:
                res[i.id] = 0
            elif i.location_id.id in location_ids:
                res[i.id] = m_cost * -1
            else:
                res[i.id] = m_cost

        return res

    def _get_move_id(self, cr, uid, ids, field_name, arg, context):

        res = {}
        sk_rel_obj = self.pool.get('stock.kardex.rel')
        for i in self.browse(cr, uid, ids):
            sk_rel_id = sk_rel_obj.search(cr, uid, [('stock_move_id', '=', i.id)])
            if sk_rel_id:
                res[i.id] = sk_rel_obj.browse(cr,uid,sk_rel_id)[0].account_move_id
            else:
                res[i.id] = []              
            
        return res

    _columns = {
        'kardex_qty': fields.function(_qty_kardex, method=True, type='float', string='Kardex Qty'),
        'kardex_move_cost': fields.function(_move_cost_kardex, method=True, type='float', string='Kardex Move Cost'),
        'move_id': fields.function(_get_move_id, type='many2one', obj="account.move",
                                 method=True, string='Account Move'),

    }


stock_move()

#----------------------------------------------------------
# Product Stock Kardex Rel
#----------------------------------------------------------

class stock_kardex_rel(osv.osv):
    _name = "stock.kardex.rel"
    _description = "Stock Move and Account Move relation table"
    _rec_name = "stock_move_id"
    _columns = {
        'stock_move_id': fields.integer('Stock Move id', select=True),
        'account_move_id': fields.integer('Account Move id', select=True),

    }


stock_kardex_rel()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
