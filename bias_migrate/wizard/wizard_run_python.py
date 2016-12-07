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
    <separator string="Modules" colspan="4"/>
        <field name="module_ids" width="450" height="150" colspan="4" nolabel="1" readonly="1"/>
</form>'''

RESULT_FORM = '''<?xml version="1.0"?> 
<form string="Python Result"> 
    <field name = "result" width="600" height="300" colspan="4" nolabel="1"/>
</form>'''

RESULT_FIELDS = {
	'result': {'string': 'Result', 'type': 'text', 'relation': False, 'required': False},
}

class run_python(wizard.interface):

    def _run_python(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        migrate = pool.get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._get_cursor(cr, uid, data, context=context)
        cr_from, cr_to = res['cr_from'], res['cr_to']
        if migrate.python and migrate.localdic:
            localdic = eval(migrate.localdic)
            exec migrate.python in localdic
        return {'result':str(localdic.get('result', False))}

    def _get_connection_data(self, cr, uid, data, context):
        migrate = pooler.get_pool(cr.dbname).get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        while FIELDS:
            FIELDS.popitem()
        FIELDS.update(pooler.get_pool(cr.dbname).get('migrate.migrate')._get_fields(cr, uid, data, context))
        form = pooler.get_pool(cr.dbname).get('migrate.migrate')._get_values(cr, uid, data, context)
        res = pooler.get_pool(cr.dbname).get('migrate.migrate')._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        module_ids = []
        for module in migrate.module_ids:
            if module.include:
                module_ids.append(module.id)
        if not module_ids:
            raise wizard.except_wizard(_('Module Error'), _('No module selected !'))
        form['module_ids'] = module_ids
        return res['form']

    states = {
		'init': {
			'actions': [_get_connection_data],
			'result': {
				'type': 'form',
				'arch': FORM,
				'fields': FIELDS,
				'state': [('end', 'Close','gtk-cancel'),('open','Run Python','gtk-go-forward')]
			}
		},
        'open': {
            'actions': [_run_python],
            'result': {
            'type':'form',
            'arch': RESULT_FORM,
            'fields': RESULT_FIELDS,
            'state':[('end','Ok')]
            }
        },
    }

run_python('migrate.run.python')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

