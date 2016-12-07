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
import time
import netsvc
import re
from string import lower
from tools.translate import _

#******************************************************************************************
#   Query Category  
#******************************************************************************************
class query_category(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        res = self.name_get(cr, uid, ids, context)
        return dict(res)

    _name = "query.category"
    _description = "Query Category"
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'), 
        'parent_id': fields.many2one('query.category','Parent Category', select=True),
        'child_id': fields.one2many('query.category', 'parent_id', string='Child Categories'),
        'sequence': fields.integer('Sequence'),
    }
    _order = "sequence"
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from query_category where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

query_category()

#******************************************************************************************
#   Query Tool  
#******************************************************************************************
class query_tool(osv.osv):
    _name = 'query.tool'
    _description = 'Query Tool'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'query': fields.text('Query'),
        'parameters_ids': fields.one2many('query.tool.line', 'query_id', 'Parameters'),
        'label_ids': fields.one2many('query.label', 'query_id', 'Query Labels'),
        'desing_ids': fields.one2many('query.label', 'query_id', 'Query Labels'),
        'u_id': fields.many2one('query.tool', 'Query'),
        'categ_id': fields.many2one('query.category', 'Categories', required=True, change_default=True),
        'user_ids': fields.many2many('res.users', 'query_tool_rel', 'query_id', 'user_id', 'Users'),
        'python_examples': fields.text('python_examples'),
        'python': fields.text('Python'),
        'text2fields': fields.boolean('Text to Fields', help="Convert the query result text to colums using csv format"),
        'no_result': fields.boolean('No Result', help="Select when expect no result from query "),
        'portrait': fields.boolean('Portrait'),
        'page_size': fields.selection([
            ('letter', 'Letter'), 
            ('a4', 'A4'),
            ('A0','A0'),
            ('A1','A1'),
            ('A2','A2'),
            ('A3','A3'),
            ('A4', 'A4'),
            ('A5', 'A5'),
            ('A6','A6'),
            ('B0','B0'),
            ('B1','B1'),
            ('B2','B2'),
            ('B2','B2'),
            ('B3','B3'),
            ('B4','B4'),
            ('B5','B5'),
            ('B6','B6'),
            ('ELEVENSEVENTEEN', 'Eleven Seventeen'), 
            ('LEGAL','Legal'),
            ], 'Paper Size',required=True,),
        'rotation': fields.selection([
            ('0', '0'), 
            ('90', '90'),
            ('180','180'),
            ('270','270'),
            ], 'Rotation',required=False,),
        'count_pages': fields.boolean('Count Pages'),
        'margin_x': fields.integer('Left Margin'),
        'margin_y': fields.integer('Top Margin'),
    }

    _defaults = {
        'python_examples': lambda *a: "Obtener cuenta contable y sus hijos: \n\nParametros de Cosulta:\nand l.account_id in %s\n\nLocaldic:\n- {'value': form[p.code], 'pool': pooler.get_pool(cr.dbname), 'cr': cr, 'uid': uid}\n\nPython Code:\nresult = tuple(pool.get('account.account')._get_children_and_consol(cr, uid, [value]))",
        'page_size': lambda *a: 'letter',
        'count_pages': lambda *a: 1,
        'margin_x' : lambda * a: 10,
        'margin_y' : lambda * a: 10,
        'rotation': lambda *a:0,
    }


    def onchange_users(self, cr, uid, ids, user_ids, context=None):
        if not ids:
            raise osv.except_osv(_('Error !'), _('Save query before add users.'))
        res = {}
        res['user_ids'] = user_ids[0][2]
        menu_id = self.pool.get('ir.ui.menu').search(cr, uid, [('name','=','My Querys')])[0]
        group_id = self.pool.get('res.groups').search(cr, uid, [('name','=','Query / User')])[0]
        user_old_ids = [x.id for x in self.browse(cr, uid, ids[0]).user_ids]
        user_new_ids = []
        for user in res['user_ids']:
            if user not in user_old_ids:
                user_new_ids.append(user)
                shortcut = self.pool.get('ir.ui.view_sc').search(cr, uid, [('name','=','Mis Consultas'), ('user_id', '=', user)])
                for new_user in user_new_ids:
                    user_groups = [x.id for x in self.pool.get('res.users').browse(cr, uid, new_user).groups_id]
                    if group_id not in user_groups:
                        user_groups.append(group_id)
                        self.pool.get('res.users').write(cr, uid, [new_user], {'groups_id':[(6,0,user_groups)]})
                if not shortcut:
                    vals={
                        'user_id': user,
                        'res_id': menu_id,
                        'resource': 'ir.ui.menu',
                        'name': 'Mis Consultas',
                    }
                    self.pool.get('ir.ui.view_sc').create(cr, uid, vals, context=context)
        return {'value': res}

query_tool()

class query_tool_line(osv.osv):
    _name = 'query.tool.line'
    _description = 'Query Tool Line'

    _columns = {
        'name': fields.char('String', size=64, reuired=True),
        'code': fields.char('Code', size=64),
        'query_id': fields.many2one('query.tool', 'Query'),
        'f_type': fields.selection([
            ('char', 'Character'), 
            ('integer', 'Integer'), 
            ('float', 'Float'), 
            ('date', 'Date'),
            ('boolean', 'Boolean'),
            ('selection', 'Selection'),
            ('many2many', 'many2many'),
            ('one2many', 'one2many'),
            ('many2one', 'many2one'),
            ('orderby', 'order by'),
            ('newline', 'New Line'),
            ], 'Type',required=True),
        'relation': fields.many2one('ir.model', 'Relation'),
        'required': fields.boolean('Required'),
        'sequence': fields.integer('Sequence'),
        'default': fields.char('Default', size=64),
        'selection': fields.char('Selection', size=128, help="If parameter type = selection then set the selection options in the form [('code1','Label1'),('code2','Label2')...]"),
        'line_query': fields.char('Line Query', size=254),
        'python': fields.text('Paython Code'),
        'localdic': fields.text('Localdic'),
    }

    _defaults = {
        'sequence': lambda *a: 1,
        'required': lambda *a: True,
        'localdic': lambda *a: "{'value': form[p.code], 'pool': pooler.get_pool(cr.dbname), 'cr': cr, 'uid': uid}",
    }
    _order = "sequence"

    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'code':False}}
        res = {}
        code = re.compile(r'\W+').sub('_',lower(name))
        res['code'] = code
        return {'value': res}

    def onchange_relation(self, cr, uid, ids, f_type, relation, context=None):
        if not relation:
            return {'value': {'relation':False}}
        res = {}
        res['relation'] = f_type not in ('char','date','boolean','selection') and relation
        return {'value': res}

    def onchange_type(self, cr, uid, ids, f_type, required, context=None):
        res = {}
        if f_type == 'orderby':
            res['line_query'] = 'ORDER BY %s'
            res['name'] = 'Ordenar Por'
            res['code'] = 'ordenar_por'
            res['sequence'] = 1000
        if f_type == 'date' and not required:
            res['line_query'] = "AND *(table)*.date *(operator <>= etc.)* '%s'"
        return {'value': res}

query_tool_line()

class query_label(osv.osv):
    _name = 'query.label'
    _description = 'Query Label'

    _columns = {
        'style_ids': fields.one2many('query.style.condition', 'lable_id', 'Query Styles'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Query Select', size=64, reuired=True),
        'query_id': fields.many2one('query.tool', 'Query'),
        'label': fields.char('label', size=64, reuired=True),
        'label_new': fields.char('New label', size=64, reuired=True),
        'size': fields.integer('Size', default=64),
        'sum': fields.boolean('Sum'),
        'invisible': fields.boolean('Invisible'),
        'f_type': fields.selection([
            ('', ''), 
            ('char', 'Character'), 
            ('integer', 'Integer'), 
            ('float', 'Float'),
            ('pct', 'Porcentage'), 
            ('date', 'Date'),
            ('boolean', 'Boolean'),
            ('selection', 'Selection'),
            ('many2many', 'many2many'),
            ('one2many', 'one2many'),
            ('many2one', 'many2one'),
            ], 'Type',required=False),
        'align': fields.selection([
            ('LEFT', 'Left'), 
            ('CENTER', 'Center'), 
            ('RIGHT', 'Right'), 
            ('JUSTIFY', 'Justify'),
            ], 'Alignment',required=False),
        'fontname': fields.selection([
            ('Courier-Bold', 'Courier-Bold'),
            ('Courier-BoldOblique','Courier-BoldOblique'),
            ('Courier-Oblique','Courier-Oblique'),
            ('Helvetica','Helvetica'),
            ('Helvetica-Bold','Helvetica-Bold'),
            ('Helvetica-BoldOblique','Helvetica-BoldOblique'),
            ('Helvetica-Oblique','Helvetica-Oblique'),
            ('Symbol','Symbol'),
            ('Times-Bold','Times-Bold'),
            ('Times-BoldItalic','Times-BoldItalic'),
            ('Times-Italic','Times-Italic'),
            ('Times-Roman','Times-Roman'),
            ('ZapfDingbats','ZapfDingbats'),
            ], 'Font Name',required=False),
        'fontsize': fields.integer('Font Size', default=64),
        'textcolor': fields.selection([
            ('red', 'Red'),
            ('black', 'Black'),
            ('aliceblue', 'Alice Blue'),
            ('blue', 'Blue'),
            ('gold', 'Gold'),
            ('green', 'Green'),
            ('white', 'White'),
            ], 'Text Color'),
        'backcolor': fields.selection([
            ('red', 'Red'),
            ('black', 'Black'),
            ('aliceblue', 'Alice Blue'),
            ('blue', 'Blue'),
            ('gold', 'Gold'),
            ('green', 'Green'),
            ('white', 'White'),
            ], 'BackGround Color'),
    }

    _defaults = {
        'sequence': lambda *a: 1,
        'fontname': lambda *a: 'Helvetica',
        'fontsize': lambda *a: 10,
        'size': lambda *a: 64,
        'align': lambda *a: 'LEFT',
        'textcolor': lambda *a: 'black',
        'backcolor': lambda *a: 'white',
    }
    _order = "sequence"


query_label()


class query_style_condition(osv.osv):
    _name = 'query.style.condition'
    _description = 'Query Style Condition'
    

    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.selection([
            ('==', '='),
            ('<=', '<='),
            ('<', '<'),
            ('>=', '>='),
            ('>', '>'),
            ('in', 'IN'),            
            ('not in', 'NOT IN'),            
            ], 'IF'),
        'value': fields.char('Value', size=64, required=True),
        'lable_id': fields.many2one('query.label', 'Conditioning Style'),
        'align': fields.selection([
            ('LEFT', 'Left'), 
            ('CENTER', 'Center'), 
            ('RIGHT', 'Right'), 
            ('JUSTIFY', 'Justify'),
            ], 'Alignment',required=False),
        'fontname': fields.selection([
            ('Courier-Bold', 'Courier-Bold'),
            ('Courier-BoldOblique','Courier-BoldOblique'),
            ('Courier-Oblique','Courier-Oblique'),
            ('Helvetica','Helvetica'),
            ('Helvetica-Bold','Helvetica-Bold'),
            ('Helvetica-BoldOblique','Helvetica-BoldOblique'),
            ('Helvetica-Oblique','Helvetica-Oblique'),
            ('Symbol','Symbol'),
            ('Times-Bold','Times-Bold'),
            ('Times-BoldItalic','Times-BoldItalic'),
            ('Times-Italic','Times-Italic'),
            ('Times-Roman','Times-Roman'),
            ('ZapfDingbats','ZapfDingbats'),
            ], 'Font Name',required=False),
        'fontsize': fields.integer('Font Size', default=64),
        'textcolor': fields.selection([
            ('red', 'Red'),
            ('black', 'Black'),
            ('aliceblue', 'Alice Blue'),
            ('blue', 'Blue'),
            ('gold', 'Gold'),
            ('green', 'Green'),
            ('white', 'White'),
            ], 'Text Color'),
        'backcolor': fields.selection([
            ('red', 'Red'),
            ('black', 'Black'),
            ('aliceblue', 'Alice Blue'),
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('gold', 'Gold'),
            ('white', 'White'),
            ], 'BackGround Color'),
        }

    _defaults = {
        'sequence': lambda *a: 1,
        'fontname': lambda *a: 'Helvetica',
        'fontsize': lambda *a: 10,
        'align': lambda *a: 'LEFT',
        'textcolor': lambda *a: 'black',
        'backcolor': lambda *a: 'white',
        }
    
    _order = "sequence"

query_style_condition()





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

