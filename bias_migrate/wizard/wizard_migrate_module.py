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
import netsvc
import pooler
import wizard
import xmlrpclib
from osv import osv
import psycopg2
from tools import config
from string import lower
from re import sub
from tools.translate import _
from tools.misc import UpdateableStr

COUNT = {}

FIELDS = {}

FORM = '''<?xml version="1.0"?>
<form string="Sign On">
    <separator colspan="2" string="               Source DB          "/>
    <separator colspan="2" string="               Target DB          "/>
    <field name="url_from" readonly="1"/>
    <field name="url_to" readonly="1"/>
    <field name="db_from" />
    <field name="db_to" />
    <field name="login_from" required="1"/>
    <field name="login_to" required="1"/>
    <field name="password_from" required="1"/>
    <field name="password_to" required="1"/>
    <newline/>
    <field name="count"/>
</form>'''

FORM_END = UpdateableStr()

def _symbol_set(symb):
    if symb == None:# or symb == False:
        return None
    elif isinstance(symb, unicode):
        return symb.encode('utf-8')
    elif isinstance(symb, (int, float, long, complex)):
        return symb
    return str(symb)

class migrate_module(wizard.interface):

    def _load_db(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('migrate.migrate.module')
        mig_obj = pooler.get_pool(cr.dbname).get('migrate.migrate')
        script_obj = pooler.get_pool(cr.dbname).get('migrate.migrate.script')
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._get_cursor(cr, uid, data, context=context)
        cr_from, cr_to = res['cr_from'], res['cr_to']
        actual_one = mig_obj._get_actual_one(cr, uid, [data['id']], context=context)
        if actual_one and script_obj.browse(cr, uid, actual_one).object_id:
            migrate_module = script_obj.browse(cr, uid, actual_one).object_id
            print 'objet=',migrate_module.name
            limit, query_fields, order, other_fields, include_reg, exclude_reg = "", "", "", [], [], []
            for field in migrate_module.field_ids:
                if field.include and field.field_org: 
                    query_fields += query_fields and (", "+(field.field_org)) or field.field_org
                    if field.name == 'id':
                        COUNT['table_id'] = 1
                        order = " ORDER BY id"
                        if field.order: 
                            order = " ORDER BY "+field.field_org
                elif field.include and not field.field_org: 
                    other_fields += [field]
                if field.include_reg and not include_reg: 
                    include_reg = field
                if field.exclude_reg and not exclude_reg: 
                    exclude_reg = field
            if COUNT['table_id']:
                limit = " WHERE id > "+str(COUNT['i'])+ order +" LIMIT "+str(data['form']['count'])+" "
                cr_from.execute("SELECT MAX(id) FROM (SELECT id FROM "+migrate_module['model_org']+" " \
                                "WHERE id > "+str(COUNT['i'])+" ORDER BY id LIMIT "+str(data['form']['count'])+") as max ")
                res = cr_from.fetchone()
                if res[0] < data['form']['count']:
                    COUNT['i'] = data['form']['count']
                else:
                    COUNT['i'] = res[0]
            cr_from.execute("select "+query_fields+" from "+migrate_module['model_org']+limit)
            res = cr_from.fetchall()
            COUNT['res'] = res and 1 or 0 # When query return no result set flag for call next object
            if res:
                query_fields = self._get_query_fields(cr, uid, query_fields, other_fields)
                for reg in res:
                    COUNT['obj_counter'] += 1
                    if self._check_include(cr, uid, reg, include_reg, exclude_reg):
                        continue
                    if COUNT['table_id']:
                        write_result = self._write_reg(cr, uid, data, reg, migrate_module, other_fields, cr_from, cr_to)
                        if write_result:
                            continue
                    self._insert_reg(cr, uid, reg, migrate_module, other_fields, cr_from, cr_to, query_fields)
        else:
            COUNT['res'] = 0
        return data['form']

    def _write_reg(self, cr, uid, data, reg, migrate_module, other_fields, cr_from, cr_to, context={}):
        reg_id = reg['id']
        cr.execute("SELECT id FROM "+migrate_module['model_dest']+" WHERE id = "+str(reg_id)+" ")
        res = cr.fetchone()
        if not res:
            return False
        query = ""
        upd0 = []
        upd1 = []
        for key in reg.keys():
            field = filter(lambda x: key == x['name'], migrate_module.field_ids)
            val = self._applicable(cr, uid, field[0], reg, cr_from, cr_to, reg[key], context) #if python code
            upd0.append('"'+key+'"=%s')
            upd1.append(_symbol_set(val or reg[key]))
        for key in [x.name for x in other_fields]:
            field = filter(lambda x: key == x['name'], migrate_module.field_ids)
            val = self._applicable(cr, uid, field[0], reg, cr_from, cr_to, False, context) #if python code
            upd0.append('"'+key+'"=%s')
            upd1.append(_symbol_set(val))
#        reg_id == 17: print 'update ' + migrate_module['model_dest'] + ' set ' + ','.join(upd0) + ' where id = %s', upd1 + [reg_id]
        cr.execute('update ' + migrate_module['model_dest'] + ' set ' + ','.join(upd0) + ' where id = %s', upd1 + [reg_id])
        return True

    def _insert_reg(self, cr, uid, reg, migrate_module, other_fields, cr_from, cr_to, context={}):
        query_fields = ''
        (upd0, upd1, upd2) = ('', '', [])
        for key in reg.keys():
            query_fields += query_fields and ', '+ key or key
            field = filter(lambda x: key == x['name'], migrate_module.field_ids)
            val = self._applicable(cr, uid, field[0], reg, cr_from, cr_to, reg[key], context) #if python code
            upd0 = upd0 and (upd0 + ',"' + key + '"') or ('"' + key + '"')
            upd1 = upd1 and (upd1 + ',%s') or '%s'
            upd2.append(_symbol_set(val or reg[key]))
        for key in [x.name for x in other_fields]:
            query_fields += query_fields and ', '+ key or key
            field = filter(lambda x: key == x['name'], migrate_module.field_ids)
            val = self._applicable(cr, uid, field[0], reg, cr_from, cr_to, False, context) #if python code
            upd0 = upd0 and (upd0 + ',"' + key + '"') or ('"' + key + '"')
            upd1 = upd1 and (upd1 + ',%s') or '%s'
            upd2.append(_symbol_set(val))
#        print 'insert into "'+migrate_module['model_dest']+'" ('+upd0+") values ("+upd1+')', tuple(upd2)
        cr.execute('insert into "'+migrate_module['model_dest']+'" ('+upd0+") values ("+upd1+')', tuple(upd2))
        return True

    def _get_query_fields(self, cr, uid, query_fields, other_fields, context={}):
        for name in [x.field_dest for x in other_fields]:
            query_fields += query_fields and ', '+ name
        return query_fields

    def _applicable(self, cr, uid, field, reg, cr_from, cr_to, val, context):
        localdic = {}
        if field.code:
            localdic = eval(field.localdic)
            exec field.python in localdic
        return localdic.get('result', False)

    def _check_include(self, cr, uid, reg, include_reg, exclude_reg, context={}):
        if exclude_reg:
            if reg[exclude_reg.field_org] in eval(exclude_reg.exclude_reg):
                return True
        elif include_reg:
            pass
        return False

    def _check_end(self, cr, uid, data, context):
        if COUNT['res'] == 1:
            return 'db'
        else:
            COUNT['db_counter'] = COUNT['db_counter'] + COUNT['obj_counter']
            COUNT['i'] = COUNT['table_id'] = COUNT['obj_counter'] = 0
            run = pooler.get_pool(cr.dbname).get('migrate.migrate').run(cr, uid, [data['id']])
            if run:
                return 'db'
            return 'migration_end'
            
    def _report(self, cr, uid, data, context):
        FORM_END.string = '''<?xml version="1.0"?>'''
        FORM_END.string += '''<form string="Migration Complited">'''
        FORM_END.string += '''<separator colspan="4" string="Register Processed %s"/>'''%COUNT['db_counter']
        FORM_END.string += '''</form>'''
        return {}

    def _get_connection_data(self, cr, uid, data, context):
        migrate = pooler.get_pool(cr.dbname).get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        while COUNT:
            COUNT.popitem()
        COUNT.update({'i':0,'res':0,'table_id':0, 'obj_counter':0, 'db_counter':0})
        while FIELDS:
            FIELDS.popitem()
        FIELDS.update(pooler.get_pool(cr.dbname).get('migrate.migrate')._get_fields(cr, uid, data, context))
        form = pooler.get_pool(cr.dbname).get('migrate.migrate')._get_values(cr, uid, data, context)
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        return res['form']

    states = {
		'init': {
			'actions': [_get_connection_data],
			'result': {
				'type': 'form',
				'arch': FORM,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('db','Migrate DB','gtk-go-forward')]
			}
		},
        'check_end': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_end}
        },
        'db': {
            'actions': [],
            'result': {'type': 'action', 'action':_load_db, 'state':'check_end'}
        },
        'migration_end': {
            'actions': [_report],
			'result': {
				'type': 'form',
				'arch': FORM_END,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel')]
			}
        },

    }

migrate_module('migrate.migrate.module')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

