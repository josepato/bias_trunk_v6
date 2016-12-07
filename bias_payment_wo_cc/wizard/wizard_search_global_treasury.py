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
import wizard
import pooler
import osv
import xmlrpclib

FORM = '''<?xml version="1.0"?>
<form string="Search Global Bank Accounts">
    <separator colspan="4"/>
    <field name="server" />
    <newline/>
    <field name="port" />
</form>'''

CONNECT_FORM = '''<?xml version="1.0"?>
<form string="Search Global Bank Accounts">
    <separator colspan="4"/>
    <field name="url" readonly="1"/>
    <newline/>
    <field name="db" />
    <newline/>
    <field name="login" required="1"/>
    <newline/>
    <field name="password" required="1"/>
</form>'''

SELECT_FORM = '''<?xml version="1.0"?>
<form string="Select Global Bank Accounts">
    <field name="treasury" />
</form>'''

SELECT_FIELDS = {
    'selection': {'string': 'Selection', 'type': 'char', 'size': 256},
}

FIELDS = {}

class wizard_search_global_treasury(wizard.interface):

    def _get_fields(self, cr, uid, data, context):
        while FIELDS:
            FIELDS.popitem()
        FIELDS['url'] = {'string': 'url', 'type':'char', 'size': 64}
        FIELDS['server'] = {'string': 'Server', 'type':'char', 'size': 64, 'required':True, 'default': lambda *a: 'localhost'}
        FIELDS['port'] = {'string': 'Port', 'type':'char', 'size': 5, 'required':True, 'default': lambda *a: '8069'}
        FIELDS['login'] = {'string': 'User Name', 'type':'char', 'size': 64, 'default': lambda *a: ''}
        FIELDS['password'] = {'string': 'password', 'type':'char', 'password': True, 'size': 64, 'default': lambda *a: ''}
        return data['form']

    def _list_db(self, cr, uid, data, context={}):
        form = data['form']
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
                pass
        return form

    def _select(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        form = data['form']
        dbname = form['db']
        user = form['login']
        pwd = form['password']
        try:
            rpc = xmlrpclib.ServerProxy(form['url']+'/xmlrpc/common')
            uid = rpc.login(dbname, user, pwd)
            rpc = xmlrpclib.ServerProxy(form['url']+'/xmlrpc/object')
            ids = rpc.execute(dbname, uid, pwd, 'account.treasury', 'search', [])
            selection = []
            for treasury in rpc.execute(dbname, uid, pwd, 'account.treasury', 'read', ids, ['name']):
                selection += [(treasury['id'], treasury['name'])]
            form['selection'] = str(dict(selection))
        except:
            selection = []
        SELECT_FIELDS['treasury'] = {'string': 'Company Treasury', 
                              'type': 'selection',
                              'selection': selection,
                              'required': False}
        return form

    def _create(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        form = data['form']
        selection = eval(form['selection'])
        pool.get('account.global.line').create(cr, uid, {
            'name': selection[form['treasury']],
            'global_id': data['id'],
            'reg_id': form['treasury'],
            'url': form['url'], 
            'server': form['server'],
            'port': form['port'],
            'db': form['db'],
            'login': form['login'],
            'password' : form['password'],
        }) 
        pool.get('account.global.treasury').write(cr, uid, data['id'], {'state': 'done'})
        return data['form']

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
				'state': [('end', 'Close','gtk-cancel'),('select','Select Global Treasury','gtk-go-forward')]
			}
		},
        'select': {
            'actions': [_select],
			'result': {
				'type': 'form',
				'arch': SELECT_FORM,
				'fields': SELECT_FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('create','Create Line','gtk-go-forward')]
			}
		},
        'create': {
            'actions': [],
            'result': {'type': 'action', 'action':_create, 'state':'init'}
        }
	}

wizard_search_global_treasury('search.global.treasury')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
