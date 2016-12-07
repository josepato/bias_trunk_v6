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

COUNT = {'i':0,'res':0,'init':0,'table_id':0,'end':0}

FORM = '''<?xml version="1.0"?>
<form string="Migrate">
    <separator colspan="4"/>
    <field name="url" readonly="1"/>
    <newline/>
    <field name="db" />
    <newline/>
    <field name="login" required="1"/>
    <newline/>
    <field name="password" required="1"/>
    <newline/>
    <field name="count"/>
    <newline/>
    <field name="initial_id"/>
    <separator string="Modules" colspan="4"/>
        <field name="module_ids" width="450" height="150" colspan="2" nolabel="1" readonly="1"/>
</form>'''

FIELDS = {
    'url': {'string': 'url', 'type':'char', 'size': 64},
    'server': {'string': 'Server', 'type':'char', 'size': 64, 'required':True, 'default': lambda *a: 'localhost'},
    'port': {'string': 'Port', 'type':'char', 'size': 5, 'required':True, 'default': lambda *a: '8069'},
    'login': {'string': 'User Name', 'type':'char', 'size': 64, 'default': lambda *a: ''},
    'password': {'string': 'password', 'type':'char', 'password': True, 'size': 64, 'default': lambda *a: ''},
	'module_ids': {'string': 'Modules', 'type': 'one2many', 'relation': 'migrate.migrate.module'},
    'count': {'string': 'Count Control', 'type':'integer', 'default': lambda *a: 1000},
    'initial_id': {'string': 'Initial ID', 'type':'integer'},
}

class migrate_set_sequences(wizard.interface):

    def _get_connection_data(self, cr, uid, data, context):
        migrate = pooler.get_pool(cr.dbname).get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        form['server'] = migrate.server
        form['port'] = migrate.port
        form['login'] = migrate.login
        form['password'] = migrate.password
        form['url'] = 'http://'+form['server']+':'+form['port']
        if 'db' not in FIELDS:
            try: 
                sock = xmlrpclib.ServerProxy(form['url']+'/xmlrpc/db')
                selection = [(x, x) for x in getattr(sock, 'list')(*())]
                FIELDS['db'] = {'string': 'Database', 
                              'type': 'selection',
                              'selection': selection,
                              'required': True}
            except:
                raise wizard.except_wizard(_('Connection Error'), _('I am unable to connect to the database !'))
        if migrate.db:
            form['db'] = migrate.db
        module_ids = []
        for module in migrate.module_ids:
            if module.state in ['done','pending']:
                module_ids.append(module.id)
        form['module_ids'] = module_ids
        return form

    def _load_seq(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('migrate.migrate.module')
        for m in data['form']['module_ids']:
            module = mod_obj.browse(cr, uid, m[1])
            if 'id' in [x.name for x in module.field_ids]:
                cr.execute("SELECT max(id) from "+module.name)
                res = cr.fetchone()
                cr.execute("SELECT setval('public."+module.name+"_id_seq', "+str(res[0]+1)+", true)")
            mod_obj.write(cr, uid, m[1], {'id_seq': res[0]})
        return data['form']

    states = {
		'init': {
			'actions': [_get_connection_data],
			'result': {
				'type': 'form',
				'arch': FORM,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('reload','Reload Sequence','gtk-go-forward')]
			}
		},
        'reload': {
            'actions': [],
            'result': {'type': 'action', 'action':_load_seq, 'state':'end'}
        },

    }

migrate_set_sequences('migrate.set.sequences')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

