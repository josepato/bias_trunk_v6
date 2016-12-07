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

class load_utilities(osv.osv_memory):
    _name = "migrate.load.utilities"
    _description = "Load Utilities"

    def _get_object(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        script = self.pool.get('migrate.migrate.script').browse(cr, uid, context.get('active_id', False))
        for rec_id in ids:
            result[rec_id] = (script.object_id.id, script.object_id.name)
        return result

    def _get_utility_selection(self,cr, uid, context=None):
        res = []
        utility_obj = self.pool.get('migrate.utilities')
        utility_ids = utility_obj.search(cr, uid, [])
        for utility in utility_obj.browse(cr, uid, utility_ids):
            res.append((utility.id,utility.name))
        return res

    _columns = {
        'script_id': fields.many2one('migrate.migrate.script', 'Script'),
#        'script_id': fields.function(_get_script, method=True, string='Script', type='many2one', relation='migrate.migrate.script'),
        'object_id': fields.function(_get_object, method=True, string='Object', type='many2one', relation='migrate.migrate.module'),
        'related_id': fields.many2one('migrate.migrate.module', 'Related Object'),
        'related_field_id': fields.many2one('migrate.migrate.field', 'Related Field'),
        'utility': fields.selection(_get_utility_selection, 'Utilities', method=True, required=True, size=32),
        'field': fields.many2one('migrate.migrate.field', 'Field'),
    }
    def _get_script(self, cr, uid, context=None):
        print 'context=',context
        result = {}
        script = self.pool.get('migrate.migrate.script').browse(cr, uid, context.get('active_id', False))
        for rec_id in browse(cr, uid, ids):
            print 'rec=',rec
            result[rec.id] = (script.id, script.name)
        return result

    _defaults = {
        'script_id': _get_script,
    }

    def _get_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids)[0]
        return data

    def load_utility(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        script_obj = self.pool.get('migrate.migrate.script')
        module_obj = self.pool.get('migrate.migrate.module')
        field_obj = self.pool.get('migrate.migrate.field')
        script = script_obj.browse(cr, uid, data['id'])
        field = field_obj.browse(cr, uid, data['form']['field'])
        utility = self.pool.get('migrate.utilities').browse(cr, uid, data['form']['utility'])
        ##############################################################################################################################
        # Parameters key words definition
        object_name = script.object_id and script.object_id.name
        related_object = data['form']['related_id'] and module_obj.browse(cr, uid, data['form']['related_id']).name or ''
        related_field = data['form']['related_field_id'] and field_obj.browse(cr, uid, data['form']['related_field_id']).name or ''
        field_name = field and field.name 
        ##############################################################################################################################
        if script.python:
            if 'if object_id:' in script.python:
                code = utility.field_utility
                parameters = utility.field_parameters
                script_obj.write(cr, uid, [data['id']], {'python':script.python +'\n'+code%eval(parameters)})
        else:
            sep = {'d':'','n':'\n', 'nt':'\n\t', 't':'\t', 's':' '}
            newline1 = sep.get(utility.separator_1, '')
            newline2 = sep.get(utility.separator_2, '')
            newline3 = sep.get(utility.separator_3, '')
            comma1 = utility.free_parameters and utility.object_parameters and ',' or ''
            comma2 = utility.object_parameters and utility.field_parameters and ',' or ''
            comma3 = utility.field_parameters and utility.related_parameters and ',' or ''
            parameters1 = utility.free_parameters or ''
            parameters2 = comma1 + (utility.object_parameters or '')
            parameters3 = comma2 + (utility.field_parameters or '')
            parameters4 = comma3 + (utility.related_parameters or '')
            parameters = parameters1 + parameters2 + parameters3 + parameters4
            code = utility.free_utility or ''
            code += newline1 + (utility.object_utility or '')
            code += newline2 + (utility.field_utility or  '')
            if not parameters4:
                code = code%eval(parameters)
                code +=  newline3 + (utility.related_utility or  '')
            else:
                code += newline3 + (utility.related_utility or  '')
                code = code%eval(parameters)
            script_obj.write(cr, uid, [data['id']], {'python':code})
        return {}

    def _get_connection_data(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        migrate = self.pool.get('migrate.migrate').browse(cr, uid, data['id'])
        form = data['form']
        FIELDS.update(self.pool.get('migrate.migrate')._get_fields(cr, uid, data, context))
        form = self.pool.get('migrate.migrate')._get_values(cr, uid, data, context)
        res = self.pool.get('migrate.migrate')._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        return res['form']

    def _load_defaults(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        while FIELDS:
            FIELDS.popitem()
        script = self.pool.get('migrate.migrate.script').browse(cr, uid, data['id'])
        if script.object_id:
            migrate_id = script.migrate_id.id
            migrate_data = {'model': 'migrate.migrate', 'form': {}, 'id': migrate_id, 'report_type': 'pdf', 'ids': [migrate_id]}
            migrate_data['form'] = self._get_connection_data(cr, uid, migrate_data, context)
            res = self.pool.get('migrate.migrate')._get_cursor(cr, uid, migrate_data, context=context)
            cr_from, cr_to = res['cr_from'], res['cr_to']
            cr_from.execute("""SELECT constraint_name FROM information_schema.table_constraints 
                            WHERE table_name = '%s' and constraint_type = 'FOREIGN KEY'"""%script.object_id.name)
            for constraint in cr_from.fetchall():
                cr_from.execute("""SELECT kcu.column_name,
                        ccu.table_name AS references_table,
                        ccu.column_name AS references_field
                        FROM information_schema.table_constraints tc
                        LEFT JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_catalog = kcu.constraint_catalog
                        AND tc.constraint_schema = kcu.constraint_schema
                        AND tc.constraint_name = kcu.constraint_name
                        LEFT JOIN information_schema.referential_constraints rc
                        ON tc.constraint_catalog = rc.constraint_catalog
                        AND tc.constraint_schema = rc.constraint_schema
                        AND tc.constraint_name = rc.constraint_name
                        LEFT JOIN information_schema.constraint_column_usage ccu
                        ON rc.unique_constraint_catalog = ccu.constraint_catalog
                        AND rc.unique_constraint_schema = ccu.constraint_schema
                        AND rc.unique_constraint_name = ccu.constraint_name
                        WHERE tc.table_name = '%s'
                        AND tc.constraint_name = '%s'"""%(script.object_id.name,constraint[0]))
                res = cr_from.fetchone()[0]
                print 'res=',res

        return form

load_utilities()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

