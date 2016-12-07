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

def _library_get(self, cr, uid, context={}):
	obj = self.pool.get('migrate.python.utilities')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['id','name'], context)
	return [('',' ')] + [(r['id'], r['name']) for r in res]

class convert_python(osv.osv_memory):
    _name = "migrate.convert.python"
    _description = "Python Code"

    _columns = {
        'python_code': fields.text('Python Code'),
		'python_library': fields.selection(_library_get, 'Python Library', size=32),
        'type': fields.selection([('python','Only Python'), ('field','Only Fields')], 'Type', help='Select Only Python to define only paython code, select Only Field to define action on fields.' ),
    }

    def onchange_python_library(self, cr, uid, ids, python_library, context=None):
        lib_obj = self.pool.get('migrate.python.utilities')
        if python_library:
            lib = lib_obj.browse(cr, uid, python_library)
            return {'value': {'python_code':lib.python, 'type':lib.type}}
        return {'value': {'python_code':'', 'type':''}}

    def _get_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['id'] = context.get('active_id', False)
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids)[0]
        return data

    def convert_python(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        form = data['form']
        util_obj = self.pool.get(context['active_model'])
        if context is None:
            context = {}
        reg = util_obj.browse(cr, uid, context['active_id'])
        if form['type'] == 'python':
            text = '''#\n    fid = field_obj.search(cr, uid, [('module_id','=',object_id[0]),('name','=','%s')])\n    field_obj.write(cr, uid, fid, {'include':True, 'python': "'''
            text += re.sub('\n', '\\\\n', data['form']['python_code'] or 'result = False')
            text += '''"})'''
        elif form['type'] == 'field':
            text = data['form']['python_code'] or ''
        else:
            text = ''
        util_obj.write(cr, uid, reg.id, {'field_utility':text})
        return {'type': 'ir.actions.act_window_close'}

convert_python()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

