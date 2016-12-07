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
import psycopg2.extras
from tools import config
from tools.translate import _

FIELDS = {}

FORM = '''<?xml version="1.0"?>
<form string="Select Servers">
    <separator colspan="2" string="               Source DB          "/>
    <separator colspan="2" string="               Destiny DB          "/>
    <field name="server_from" />
    <field name="server_to" />
    <field name="port_from" />
    <field name="port_to" />
</form>'''

CONNECT_FORM = '''<?xml version="1.0"?>
<form string="Sign On">
    <separator colspan="2" string="               Source DB          "/>
    <separator colspan="2" string="               Destiny DB          "/>
    <field name="url_from" readonly="1"/>
    <field name="url_to" readonly="1"/>
    <field name="db_from" />
    <field name="db_to" />
    <field name="login_from" required="1"/>
    <field name="login_to" required="1"/>
    <field name="password_from" required="1"/>
    <field name="password_to" required="1"/>
</form>'''

db_form = '''<?xml version="1.0"?>
<form string="Select DB Connection Information">
    <separator colspan="2" string="               Source DB          "/>
    <separator colspan="2" string="               Destiny DB          "/>
    <field name="server_from"/>
    <field name="server_to"/>
    <field name="port_from"/>
    <field name="port_to"/>
    <field name="db_from"/>
    <field name="db_to"/>
</form>'''

class load_module(wizard.interface):

    def _load_db(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        form = data['form']
        ids = pool.get('migrate.migrate.module').search(cr, uid, [('migrate_id','=',data['id'])])
        pool.get('migrate.migrate.module').unlink(cr, uid, ids)
        dbname_from, user_from, pwd_from = form['db_from'], form['login_from'], form['password_from']
        dbname_to, user_to, pwd_to = form['db_to'], form['login_to'], form['password_to']
        try:
            conn_from = psycopg2.connect("dbname="+dbname_from+" user="+user_from+" host="+form['server_from']+" password="+pwd_from+" ");
        except:
            raise wizard.except_wizard(_('Connection Error'), _('Unable to connect to "Origin Database" !'))
        try:
            conn_to = psycopg2.connect("dbname="+dbname_to+" user="+user_to+" host="+form['server_to']+" password="+pwd_to+" ");
        except:
                raise wizard.except_wizard(_('Connection Error'), _('Unable to connect to the "Destiny Database" !'))
        cr_from = conn_from.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cr_from.execute("SELECT tablename from pg_tables where schemaname = 'public' order by tablename")
        tables_from = [x[0] for x in cr_from.fetchall()]
        cr_to = conn_to.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cr_to.execute("SELECT tablename from pg_tables where schemaname = 'public' order by tablename")
        tables_to = [x[0] for x in cr_to.fetchall()]
        for row in tables_from:
            cr_from.execute("SELECT * from "+row+" ")
            if cr_from.rowcount:
                res = cr_from.fetchall()
                pool.get('migrate.migrate.module').create(cr, uid, {
                    'name': row,
                    'migrate_id': data['id'],
                    'reg': len(res),
                    'include': True,
                    'seq': 100, #row.startswith('ir') and 30 or row.startswith('res') and 10 or 20,
                    'model_org': row,
                    'model_dest': row in tables_to and row or False,
                }) 
        pool.get('migrate.migrate').write(cr, uid, data['id'], {
                    'state': 'modules',
                    'server_from': form['server_from'],
                    'port_from': form['port_from'],
                    'db_from': form['db_from'],
                    'login_from': form['login_from'],
                    'password_from': form['password_from'],
                    'server_to': form['server_to'],
                    'port_to': form['port_to'],
                    'db_to': form['db_to'],
                    'login_to': form['login_to'],
                    'password_to': form['password_to'],
                    })
        module_ids = []
        for module in pool.get('migrate.migrate').browse(cr, uid, data['id']).module_ids:
            module_ids.append(module.id)
        if not module_ids:
            raise wizard.except_wizard(_('Module Error'), _('No module selected !'))
        form['module_ids'] = module_ids
        return self._load_fields(cr, uid, data, context)

    def _load_fields(self, cr, uid, data, context):
        field_obj = pooler.get_pool(cr.dbname).get('migrate.migrate.field')
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._get_cursor(cr, uid, data, context=context)
        cr_from, cr_to = res['cr_from'], res['cr_to']
        for m in data['form']['module_ids']:
            field_obj.unlink(cr, uid, field_obj.search(cr, uid, [('module_id','=',m)]))
            module = pooler.get_pool(cr.dbname).get('migrate.migrate.module').browse(cr, uid, m)
            cr_from.execute("SELECT c.oid, n.nspname, c.relname FROM pg_catalog.pg_class c " \
                            "LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace " \
                            "WHERE c.relname ~ '^("+module.model_org+")$' AND pg_catalog.pg_table_is_visible(c.oid) ORDER BY 2, 3; ")
            res_from = cr_from.fetchone()
            cr_from.execute("SELECT a.attname, pg_catalog.format_type(a.atttypid, a.atttypmod), (SELECT substring(pg_catalog.pg_get_expr(d.adbin, " \
                            "d.adrelid) for 128) FROM pg_catalog.pg_attrdef d WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef), " \
                            "a.attnotnull, a.attnum FROM pg_catalog.pg_attribute a " \
                            "WHERE a.attrelid = "+str(res_from['oid'])+" AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum")
            res_from = cr_from.fetchall()
            if module.model_dest:
                cr_to.execute("SELECT c.oid, n.nspname, c.relname FROM pg_catalog.pg_class c " \
                            "LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace " \
                            "WHERE c.relname ~ '^("+module.model_dest+")$' AND pg_catalog.pg_table_is_visible(c.oid) ORDER BY 2, 3; ")
                res_to = cr_to.fetchone()
                cr_to.execute("SELECT a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod),(SELECT substring(pg_catalog.pg_get_expr(d.adbin, " \
                            "d.adrelid) for 128) FROM pg_catalog.pg_attrdef d WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef), " \
                            "a.attnotnull, a.attnum FROM pg_catalog.pg_attribute a " \
                            "WHERE a.attrelid = "+str(res_to['oid'])+" AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum")
                res_to = cr_to.fetchall()
                old_field = []
                for field in res_from:
                    dest = dest_type = False
                    for field_to in res_to:
                        if field['attname'] == field_to['attname']:
                            dest = field_to['attname']
                            dest_type = field_to['format_type']
                    old_field.append(field['attname'])
                    field_obj.create(cr, uid, {
                        'name': field['attname'],
                        'module_id': m,
                        'seq': field['attnum'],
                        'field_org': field['attname'],
                        'field_dest': dest,
                        'field_org_type': field['format_type'],
                        'field_dest_type': dest_type,
                        'include': field['format_type'] == dest_type,
                    })
                for field_to in res_to:
                    if field_to['attname'] not in old_field:
                        field_obj.create(cr, uid, {
                            'name': field_to['attname'],
                            'module_id': m,
                            'seq': field_to['attnum'],
                            'field_org': False,
                            'field_dest': field_to['attname'],
                            'field_org_type': False,
                            'field_dest_type': field_to['format_type'],
                        })
                pooler.get_pool(cr.dbname).get('migrate.migrate.module').write(cr, uid, m, {'state': 'field'})
        pooler.get_pool(cr.dbname).get('migrate.migrate').exclude(cr, uid, [data['id']], context=context)
        pooler.get_pool(cr.dbname).get('migrate.migrate').write(cr, uid, data['id'], {'state': 'pause'})
        return {}

    def _get_fields(self, cr, uid, data, context):
        form = data['form']
        while FIELDS:
            FIELDS.popitem()
        FIELDS.update(pooler.get_pool(cr.dbname).get('migrate.migrate')._get_fields(cr, uid, data, context))
        return pooler.get_pool(cr.dbname).get('migrate.migrate')._get_values(cr, uid, data, context)

    def _list_db(self, cr, uid, data, context={}):
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        return res['form']

    states = {
		'init': {
			'actions': [_get_fields],
			'result': {
				'type': 'form',
				'arch': FORM,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('connect','Connect','gtk-go-forward')]
			}
		},
        'connect': {
            'actions': [_list_db],
			'result': {
				'type': 'form',
				'arch': CONNECT_FORM,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('modules','Load Modules','gtk-go-forward')]
			}
		},
        'modules': {
            'actions': [],
            'result': {'type': 'action', 'action':_load_db, 'state':'end'}
        },

    }

load_module('migrate.load.module')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

