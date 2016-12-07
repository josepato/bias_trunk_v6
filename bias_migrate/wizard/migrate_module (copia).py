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
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _
import re

import xmlrpclib
import psycopg2
from tools import config
from string import lower
from re import sub
from tools.misc import UpdateableStr
from tools import config
import optparse
import release

COUNT = {}

def _symbol_set(symb):
    if symb == None:# or symb == False:
        return None
    elif isinstance(symb, unicode):
        return symb.encode('utf-8')
    elif isinstance(symb, (int, float, long, complex)):
        return symb
    return str(symb)

class migrate_db(osv.osv_memory):
    _name = "migrate.db"
    _description = "Migrate Data Base"
    _columns = {
        'name': fields.char('Data Base', size=64, translate=True, required=True),
    }

migrate_db()

class migrate_module(osv.osv_memory):
    _name = "migrate.module"
    _description = "Migrate Module"

    def _url_from(self, cr, uid, context=None):
        version = "%s %s" % (release.description, release.version)
        print 'vesion=',version
        return self._get_defaults(cr, uid, 'url_from', context=context)

    def _url_to(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'url_to', context=context)

    def _db_from(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'db_from', context=context)

    def _db_to(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'db_to', context=context)

    def _login_from(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'login_from', context=context)

    def _password_from(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'password_from', context=context)

    def _server_from(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'server_from', context=context)

    def _port_from(self, cr, uid, context=None):
        return self._get_defaults(cr, uid, 'port_from', context=context)

#    def _login_to(self, cr, uid, context=None):
#        return self._get_defaults(cr, uid, 'login_to', context=context)
#    def _password_to(self, cr, uid, context=None):
#        return self._get_defaults(cr, uid, 'password_to', context=context)

    def _get_defaults(self, cr, uid, field_name, context=None):
        data = self._get_data(cr, uid, ids=[], context=context)
        form = data['form']
        mig_obj = self.pool.get('migrate.migrate')
        ids = mig_obj.search(cr, uid, [])
        res = False
        if ids:
            cr.execute("SELECT current_database()")
            db_name = cr.fetchone()[0]
            migrate = mig_obj.browse(cr, uid, ids, context=context)[0]
            form = {
                'server_from': migrate.server_from,
                'server_to': migrate.server_to,
                'port_from': migrate.port_from,
                'port_to': str(config.get('xmlrpc_port', 8069)),
                'url_from': 'http://'+migrate.server_from+':'+migrate.port_from,
                'url_to': 'http://'+migrate.server_to+':'+str(config.get('xmlrpc_port', 8069)),
                'db_from': False,#migrate.db_from,
                'db_to': db_name,
                'login_from': migrate.login_from,
                'password_from': migrate.password_from,
                'count': 1000,
#                'login_to': config.get('db_user', ''),
#                'password_to': migrate.password_to,
            }
        data['form'] = form
        res = self.pool.get('migrate.migrate')._list_db(cr, uid, data, context={})
#        print 'res=',res
        return form[field_name]

    _columns = {
        'url_from': fields.char('From url', size=64, required=True),
        'server_from': fields.char('From Server', size=64, required=True),
        'port_from': fields.char('From Port XML-RPC', size=5, required=True), 
        'login_from': fields.char('From DB User Name', size=64, required=True),
        'password_from': fields.char('From DB password', size=64, required=True, password=True),
        'url_to': fields.char('To url', size=64, required=True),
        'server_to': fields.char('to Server', size=64, required=True),
        'port_to': fields.char('To Port XML-RPC', size=5, required=True),
        'count': fields.integer('Count Control', required=True),
        'db_to': fields.char('Data Base', size=50, readonly=True),
        'db_from': fields.many2many('migrate.db', 'migrate_db_rel', 'migrate_id', 'db_id', 'Data Bases'),
        'state': fields.selection((('choose','choose'),   # choose parameters
                                   ('change','change'),   # change origin server
                                  )),
#        'db_from': fields.selection([('amci1', 'amci1')], 'Data Base'),
#        'login_to': fields.char('To DB User Name', size=64, required=True, readonly=True),
#        'password_to': fields.char('To DB password', size=64, required=True, password=True),
    }
    _defaults = {
        'server_from': _server_from,
        'port_from': _port_from,
        'server_to': 'localhost',
        'port_to': '8069',
        'url_from': _url_from,
        'url_to': _url_to,
        'db_from': _db_from,
        'db_to': _db_to,
        'login_from': _login_from,
        'password_from': _password_from,
        'count': 1000,
        'state': 'choose',
#        'login_to': _login_to,
#        'password_to': _password_to,
    }

    def _get_data(self, cr, uid, ids=[], context=None):
        if context is None:
            context = {}
        data = {}
        data['id'] = context.get('active_id', False)
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        values = self.read(cr, uid, data['ids'])
        data['form'] = values and values[0] or {}
        return data

    def change(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'change'}, context=context)

    def save(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        form = data['form']
        mig_obj = self.pool.get('migrate.migrate')
        mod_obj = self.pool.get('migrate.module')
        ids = mig_obj.search(cr, uid, [])
        url = 'http://'+form['server_from']+':'+form['port_from']
        db_from = []
        for db in self.pool.get('migrate.migrate')._list_db(cr, uid, data, context={}):
            db_id = self.pool.get('migrate.db').create(cr, uid, {'name':db[0]})
            db_from.append(db_id)
        print 'db_from=',db_from
        mig_obj.write(cr, uid, ids, {'server_from':form['server_from'], 'port_from':form['port_from']})
#        self.write(cr, uid, data['ids'], {'server_from':form['server_from'], 'port_from':form['port_from'], 'url_from':url, 'state':'choose',})
        return self.write(cr, uid, data['ids'], {'server_from':form['server_from'], 'port_from':form['port_from'], 'url_from':url, 'state':'choose', 'db_from': [(6, 0, db_from)]})
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'migrate.module',
            'domain': [],
            'res_id': int(data['id']),
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        

    def _load_db(self, cr, uid, data, context):
        mod_obj = self.pool.get('migrate.migrate.module')
        mig_obj = self.pool.get('migrate.migrate')
        script_obj = self.pool.get('migrate.migrate.script')
        res = self.pool.get('migrate.migrate')._get_cursor(cr, uid, data, context=context)
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
            run = self.pool.get('migrate.migrate').run(cr, uid, [data['id']])
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
        migrate = self.pool.get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        while COUNT:
            COUNT.popitem()
        COUNT.update({'i':0,'res':0,'table_id':0, 'obj_counter':0, 'db_counter':0})
        while FIELDS:
            FIELDS.popitem()
        FIELDS.update(self.pool.get('migrate.migrate')._get_fields(cr, uid, data, context))
        form = self.pool.get('migrate.migrate')._get_values(cr, uid, data, context)
        res = self.pool.get('migrate.migrate')._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        return res['form']

migrate_module()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

