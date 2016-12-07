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

from osv import osv, fields
import pooler

import math
#from _common import rounding

from tools import config
from tools.translate import _




def make_tuple(ids):
    res = ()
    if len(ids) == 1:
        return '(%s)'%ids[0]
    elif len(ids) >1 :
        for i in ids:
            if i:
                res += (i,)
        return str(tuple(res))
    else:
        return ()




def query_clauses(cr, uid,  offset=0,limit=None, order=None):
    query = ''
    if not order:
        order = 'id'
    if limit:
        query += ' order by %s  limit %s'%(order, limit)
    else:
        query += ' order by %s '%(order)
    return query
        
def _search(cr, uid, args, col_name, table_name, offset=0,limit=None, order=None, ):
    new_args = []
    ids = []
    where_clause = ""
    query2 = query = ""
    for arg in args:
        if arg[0] and arg[2] and arg[0] != 'id' and arg[0] != 'name':
            if where_clause:
                where_clause += " and %s=%s "%(arg[0], arg[2])
            else:
                where_clause += " %s=%s "%(arg[0], arg[2])
        if arg[0] in ('name', 'id'):
            if arg[1] == 'in':
                query2 = "SELECT id from %s where %s %s %s "%(table_name, arg[0], arg[1], make_tuple(arg[2]) )
            else:
                query2 = "SELECT id from %s where %s %s '%s' "%(table_name, arg[0], arg[1], '%' +str(arg[2]) + '%')
    if where_clause:
        query = "SELECT distinct(%s) as id from product_product where %s"%(col_name, where_clause,)
        query_cluses = query_clauses(cr, uid,  offset=0,limit=None, order=None)
        query += query_cluses
        cr.execute(query)
        ids = cr.fetchall()
        ids = [id[0] for id in ids]
    elif not query and not query2:
        query2 = "SELECT distinct(%s) as id  from product_product"%(col_name, )
    if query2 and ids:
        query2 += " and id in %s "%(make_tuple(ids))
    if query2:
        query_cluses = query_clauses(cr, uid,  offset=0,limit=None, order=None)
        query2 += query_cluses
        cr.execute(query2)
        ids = cr.fetchall()
        ids = [id[0] for id in ids]
    new_args.append(('id','in',ids))
    return new_args

#----------------------------------------------------------
# Product Line
#----------------------------------------------------------
class product_line(osv.osv):
    _name = 'product.line'
    _description = 'Product Line'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=14, required=False, ),

        }


    def _search(self, cr, uid, args,    offset=0,limit=None, order=None, context=None, count=False, access_rights_uid=None):
        new_args = _search( cr, uid, args, 'product_line_id', 'product_line' , offset=0,limit=None, order=None,)
        res =  super( product_line, self)._search(cr, uid, new_args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None)
        return res



    _sql_constraints = [
            ('product_line_uniq', 'unique (name)', 'The Product Line code must be unique !')
            ]
    _order = "name"
    
product_line()

#----------------------------------------------------------
# Product Colection
#----------------------------------------------------------
class product_colection(osv.osv):
    _name = 'product.colection'
    _description = 'Product Colection'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=14, required=False, ),
        'line_ids': fields.many2many('product.line', 'product_colection_line_rel','line_id','colection_id',  'Related Lines'),
        'product_brand_id': fields.many2many('product.brand', 'product_colection_line_rel', 'line_id','colection_id', 'Related Brands'),
        }





    def _search(self, cr, uid, args,    offset=0,limit=None, order=None, context=None, count=False, access_rights_uid=None):
        new_args = _search( cr, uid, args, 'product_colection_id', 'product_colection' , offset=0,limit=None, order=None,)
        res =  super(product_colection, self)._search(cr, uid, new_args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None)
        return res
        

        

    
    
    _sql_constraints = [
            ('product_colection_uniq', 'unique (name,code)', 'The Product colection name and colection code must be unique !')
            ]
    _order = "name"
    
product_colection()

#----------------------------------------------------------
# Product Type
#----------------------------------------------------------
class product_type(osv.osv):
    _name = 'product.type'
    _description = 'Product Type'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=14, required=False, ),

        }


    
    _sql_constraints = [
        ('product_type_uniq', 'unique (name)', 'The Product type must be unique !')
        ]
    
product_type()


#----------------------------------------------------------
# Brand
#----------------------------------------------------------

class product_brand(osv.osv):
    _name = 'product.brand'
    _description = 'Product Brand'




    def _search(self, cr, uid, args,    offset=0,limit=None, order=None, context=None, count=False, access_rights_uid=None):
        count = 0 
        for arg in args:
            if arg[0] == 'type':
                args.pop(count)
            count +=1
        new_args = _search( cr, uid, args, 'product_brand_id', 'product_brand' , offset=0,limit=None, order=None,)
        res =  super(product_brand, self)._search(cr, uid, new_args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None)
        return res


    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=14, required=False, ),
        'type_ids': fields.many2many('product.type', 'product_brand_type_rel','type_id', 'bran_id',  'Available Types'),
        'colection_ids': fields.many2many('product.colection', 'product_brand_colection_rel','colection_id','bran_id', 'Available Colections'),

        }
    

    _sql_constraints = [
            ('product_brand_uniq', 'unique (name,code)', 'The Product brand name and brand code must be unique !')
            ]

    _order = "name"

product_brand()





###----------------------------------------------------------
### Material
###----------------------------------------------------------

class product_material(osv.osv):
    _name = 'product.material'
    _description = 'Product Material'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        }

    _sql_constraints = [
        ('product_material_uniq', 'unique (name)', 'The Product Material must be unique !')
        ]
    _order = "name"

product_material()

###----------------------------------------------------------
### Color
###----------------------------------------------------------

class product_color(osv.osv):
    _name = 'product.color'
    _description = 'Product Color'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        }
    
    _sql_constraints = [
        ('product_color_uniq', 'unique (name)', 'The Product Color must be unique !')
    ]
    _order = "name"

    
product_color()

###----------------------------------------------------------
### Hardware
###----------------------------------------------------------

class product_hardware(osv.osv):
    _name = 'product.hardware'
    _description = 'Product Hardware'
    _columns = {
        'name': fields.char('Hardware', size=64, required=True),
        }

    _sql_constraints = [
        ('product_hardware_uniq', 'unique (name)', 'The Product Hardware must be unique !')
    ]
    _order = "name"
product_hardware()


#----------------------------------------------------------
# writing kind
#----------------------------------------------------------

class product_writing_kind(osv.osv):
    _name = 'product.writing.kind'
    _description = 'Product Writing Kind'
    _columns = {
        'name': fields.char('Product Writing Kind', size=64, required=True),
        }

    _sql_constraints = [
        ('product_writing_kind_uniq', 'unique (name)', 'The writing Kind must be unique !')
    ]
    _order = "name"
    
product_writing_kind()

#----------------------------------------------------------
# writing Type
#----------------------------------------------------------

class product_writing_type(osv.osv):
    _name = 'product.writing.type'
    _description = 'Product Writing Type'
    _columns = {
        'name': fields.char('Product Writing Type', size=64, required=True),
        }



    def _search(self, cr, uid, args,    offset=0,limit=None, order=None, context=None, count=False, access_rights_uid=None):
        new_args = _search( cr, uid, args, 'product_writing_type_id', 'product_writing_type', offset=0,limit=None, order=None, )
        res =  super( product_writing_type, self)._search(cr, uid, new_args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None)
        return res


    _sql_constraints = [
        ('product_writing_type_uniq', 'unique (name)', 'The writing type must be unique !')
    ]
    _order = "name"
   
product_writing_type()




#----------------------------------------------------------
# writing Meterial
#----------------------------------------------------------

class product_writing_material(osv.osv):
    _name = 'product.writing.material'
    _description = 'Product Writing Material'
    _columns = {
        'name': fields.char('Product Writing Material', size=64, required=True),
        }


    _sql_constraints = [
        ('product_writing_material_uniq', 'unique (name)', 'The writing material must be unique !')
    ]
    _order = "name"
product_writing_material()


#----------------------------------------------------------
# Product Observations
#----------------------------------------------------------

class product_observations(osv.osv):
    _name = 'product.observations'
    _description = 'Product observations'
    _columns = {
        'name': fields.char('Product Observations', size=64, required=True),
        }


    _sql_constraints = [
        ('product_observations_unique', 'unique (name)', 'The writing material must be unique !')
    ]
    _order = "name"
   
product_observations()




###----------------------------------------------------------
### Product
###----------------------------------------------------------

class product_product(osv.osv):



    def search(self, cr, uid, args, offset=0, limit=100,order=None,context=None, count=False):
        new_args = []
        for arg in args:
            #if arg
            if arg[2]:
                new_args.append(arg)
                if arg[0] == 'default_code':
                    try:
                        int(arg[2])
                        new_args.append(('name', arg[1], arg[2]))
                    except:
                        continue
        res =  super(product_product, self).search(cr, uid, new_args, offset=0, limit=None,order=None,context=None, count=False)
        return res

    
    _inherit = 'product.product'
    _columns = {
        'product_writing_kind_id': fields.many2one('product.writing.kind', 'Product Writing Kind', required=False),
        'product_writing_type_id': fields.many2one('product.writing.type', 'Product Writing Type', required=False),
        'product_writing_metaerial_id': fields.many2one('product.writing.material', 'Product Writing Metaerial', required=False),
        'product_top_color_ids': fields.many2many('product.color', 'product_top_color_rel','color_id', 'product_id', 'Top Colors'),
        'product_bottom_color_ids': fields.many2many('product.color', 'product_bottom_color_rel','color_id', 'product_id', 'Bottom Colors'),
        'product_top_material_ids': fields.many2many('product.material', 'product_top_material_rel','material_id', 'product_id', 'Top Materials'),
        'product_bottom_material_ids': fields.many2many('product.material', 'product_bottom_material_rel','material_id', 'product_id', 'Bottom Materials'),
        'product_hardware_ids': fields.many2many('product.hardware', 'product_hardware_rel','hardware_id', 'product_id', 'Product Hardwares'),
        'product_consumable_ids': fields.many2many('product.product', 'product_consumable_rel','consumable_id', 'product_id', 'Product Consumables'),
        'product_observations_ids': fields.many2many('product.observations', 'product_observations_res','observation_id', 'product_id', 'Product Observations'),
        'product_brand_id': fields.many2one('product.brand', 'Product Brand', required=False, change_default=True, domain="[('type','=','normal')]" ),
        'product_line_id': fields.many2one('product.line', 'Product Line', required=False),
        'product_colection_id': fields.many2one('product.colection', 'Product Colection', required=False),
        'product_type_id': fields.many2one('product.type', 'Product Type', required=False),
        'kit_type' : fields.selection([('unit','Unit'),('pack','Pack'),('part', 'Part')], 'Kit Type', required=True),
        'picture': fields.binary('Picture'),
        
        }

    _defaults = {
        'kit_type': lambda *a: 'unit',

        }

    def name_get(self, cr, uid, ids, context=None):
        res = super(product_product, self).name_get(cr, uid, ids, context)
        result = dict([[i[0],i[1]] for i in res])
        for product in self.browse(cr, uid, ids):
            #if product.product_brand_id:
                #result[product.id] += ' - %s'%(product.product_brand_id.code)
            if product.product_colection_id:
                result[product.id] += ' - %s'%(product.product_colection_id.name)
            if product.product_line_id:     
                result[product.id] += ' - %s'%(product.product_line_id.name)
            if product.product_writing_type_id:
                result[product.id] += ' - %s'%(product.product_writing_type_id.name)
        res = []
        for res_id in result:
            res.append((res_id, result[res_id]))
        return res

    
product_product()
