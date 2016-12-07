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
from tools import config
import xmlrpclib
import psycopg2
import psycopg2.extras
from tools.translate import _
import pooler

#----------------------------------------------------------
# Migrate
#----------------------------------------------------------
class migrate_migrate(osv.osv):
    _name = "migrate.migrate"
    _description = "Data Base Migrate"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'module_ids': fields.one2many('migrate.migrate.module', 'migrate_id', 'Modules',),
        'script_ids': fields.one2many('migrate.migrate.script', 'migrate_id', 'Script',),
        'state': fields.selection([('draft','Draft'),('modules','Modules Loaded'),('idle','Idle'),('pause','Pause'),('processing','Processing'),('done','Done')], 'Status', readonly=True),
        'server_from': fields.char('Server', size=50),
        'port_from': fields.char('Port', size=5),
        'db_from': fields.char('Data Base', size=50),
        'login_from': fields.char('User Name', size=50),
        'password_from': fields.char('Password', size=54, password=True),
        'server_to': fields.char('Server', size=50),
        'port_to': fields.char('Port', size=5),
        'db_to': fields.char('Data Base', size=50),
        'login_to': fields.char('User Name', size=50),
        'password_to': fields.char('Password', size=54, password=True),
        'instructions': fields.text('Instructions'),
        'python': fields.text('Paython Code'),
        'localdic': fields.char('Localdic', size=384, required=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'server_from': lambda *a: 'localhost',
        'port_from': lambda *a: '8069',
        'server_to': lambda *a: 'localhost',
        'port_to': lambda *a: '8069',
        'localdic': lambda *a: "{'pool':pooler.get_pool(cr.dbname), 'cr':cr, 'uid':uid, 'cr_from':cr_from, 'cr_to':cr_to, 'id':data['id']}",
        'python': lambda *a: '''# result = "python code or constant" ''',
        'instructions': lambda *a: "Instructions for Migrations: \n\n1.- Fill 'Name' field.\n2.- Clic 'Load Modules' button.\n3.- Fill origin and target Server's name or IP address and ports in wizard windows and clic 'Connect' button.\n4.- Select DB origin and target, then fill DB users and paswords respectively, then clic 'Load Modules' button.\n5.- Wait few seconds until finish and 'State' field change to 'Modules Loaded'.\n6.- Check 'Model ORG' and 'Model Dest' and install additional modules if necesary, then cancel and execute process again.\n7.- Select the modules migration order modifying the 'Secuence' Modules field.\n8.- You can migrate modules manualy one by one or automate the process by writing a migration script in 'Script Information'. ",
    }

    def _get_fields(self, cr, uid, data, context):
        res = {}
        res['url_from'] = {'string': 'From url', 'type':'char', 'size': 64}
        res['server_from'] = {'string': 'From Server', 'type':'char', 'size': 64, 'required':True, 'default': lambda *a: 'localhost'}
        res['port_from'] = {'string': 'From Port XML-RPC', 'type':'char', 'size': 5, 'required':True, 'default': lambda *a: '8069'}
        res['login_from'] = {'string': 'From DB User Name', 'type':'char', 'size': 64, 'default': lambda *a: ''}
        res['password_from'] = {'string': 'From DB password', 'type':'char', 'password': True, 'size': 64, 'default': lambda *a: ''}
        res['url_to'] = {'string': 'To url', 'type':'char', 'size': 64}
        res['server_to'] = {'string': 'To Server', 'type':'char', 'size': 64, 'required':True, 'default': lambda *a: 'localhost'}
        res['port_to'] = {'string': 'To Port XML-RPC', 'type':'char', 'size': 5, 'required':True, 'default': lambda *a: '8069'}
        res['login_to'] = {'string': 'To DB User Name', 'type':'char', 'size': 64, 'default': lambda *a: ''}
        res['password_to'] = {'string': 'To DB password', 'type':'char', 'password': True, 'size': 64, 'default': lambda *a: ''}
        res['count'] = {'string': 'Count Control', 'type':'integer', 'default': lambda *a: 1000}
        return res

    def _get_values(self, cr, uid, data, context={}):
        migrate = self.browse(cr, uid, data['id'])
        form = data['form']
        form['server_from'] = migrate.server_from
        form['port_from'] = migrate.port_from
        form['login_from'] = migrate.login_from
        form['password_from'] = migrate.password_from
        form['server_to'] = migrate.server_to
        form['port_to'] = migrate.port_to
        form['login_to'] = migrate.login_to
        form['password_to'] = migrate.password_to
        form['count'] = 2000
        return form

    def list_db(self, cr, uid, data, context={}):
        migrate = self.browse(cr, uid, data['id'])
        form = data['form']
        form['url_from'] = 'http://'+form['server_from']+':'+form['port_from']
        try: 
            sock = xmlrpclib.ServerProxy(form['url_from']+'/xmlrpc/db')
            res = [(x, x) for x in getattr(sock, 'list')(*())]
        except:
            res = []
        return res

    def _list_db(self, cr, uid, data, FIELDS={}, context={}):
        migrate = self.browse(cr, uid, data['id'])
        form = data['form']
        form['url_from'] = 'http://'+form['server_from']+':'+form['port_from']
        form['url_to'] = 'http://'+form['server_to']+':'+form['port_to']
        if 'db_from' not in FIELDS:
            try: 
                sock = xmlrpclib.ServerProxy(form['url_from']+'/xmlrpc/db')
                selection = [(x, x) for x in getattr(sock, 'list')(*())]
            except:
                selection = []
#                raise osv.except_osv(_('Connection Error'), _('Unable to connect to "Origin Database" !'))
            FIELDS['db_from'] = {'string': 'Database', 
                              'type': 'selection',
                              'selection': selection,
                              'required': True}
        if 'db_to' not in FIELDS:
            try: 
                sock = xmlrpclib.ServerProxy(form['url_to']+'/xmlrpc/db')
                selection = [(x, x) for x in getattr(sock, 'list')(*())]
            except:
                selection = []
#                raise osv.except_osv(_('Connection Error'), _('Unable to connect to the "Target Database" !'))
            FIELDS['db_to'] = {'string': 'Database', 
                              'type': 'selection',
                              'selection': selection,
                              'required': True}
        if migrate.db_from:
            form['db_from'] = migrate.db_from
        if migrate.db_to:
            form['db_to'] = migrate.db_to
        return {'form':form, 'FIELDS':FIELDS}

    def _get_cursor(self, cr, uid, data, context={}):
        form = data['form']
        dbname_from, user_from, pwd_from = form['db_from'], form['login_from'], form['password_from']
        dbname_to, user_to, pwd_to = form['db_to'], form['login_to'], form['password_to']
        try:
            conn_from = psycopg2.connect("dbname="+dbname_from+" user="+user_from+" host="+form['server_from']+" password="+pwd_from+" ");
        except:
            raise osv.except_osv(_('Connection Error'), _('Unable to connect to "Origin Database" !'))
        try:
            conn_to = psycopg2.connect("dbname="+dbname_to+" user="+user_to+" host="+form['server_to']+" password="+pwd_to+" ");
        except:
                raise osv.except_osv(_('Connection Error'), _('Unable to connect to the "Target Database" !'))
        cr_from = conn_from.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cr_to = conn_to.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return {'cr_from':cr_from, 'cr_to':cr_to}

    def cancel(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'draft'})

    def include(self,cr, uid, ids, context={}):
        for migrate in self.browse(cr, uid, ids, context):
            self.pool.get('migrate.migrate.module').write(cr, uid, [x.id for x in migrate.module_ids], {'include':True})
            if migrate.state == 'modules':
                pass
            else:
                self.write(cr, uid, ids, {'state': 'idle'})
        return True

    def exclude(self,cr, uid, ids, context={}):
        for migrate in self.browse(cr, uid, ids, context):
            self.pool.get('migrate.migrate.module').write(cr, uid, [x.id for x in migrate.module_ids], {'include':False})
            if migrate.state == 'modules':
                pass
            else:
                self.write(cr, uid, ids, {'state': 'pause'})
        return True

    def _get_actual_one(self,cr, uid, ids, context={}):
        script_obj = self.pool.get('migrate.migrate.script')
        actual_one_script_ids = script_obj.search(cr, uid, [('migrate_id','=',ids[0]),('actual_one','=',True)])
        return actual_one_script_ids and actual_one_script_ids[0] or False

    def _get_next_one(self,cr, uid, ids, context={}):
        script_obj = self.pool.get('migrate.migrate.script')
        all_script_ids = script_obj.search(cr, uid, [('migrate_id','=',ids[0])])
        actual_one = self._get_actual_one(cr, uid, ids, context=context)
        if not actual_one:
            actual_one = all_script_ids[0]
        actual_script = script_obj.browse(cr, uid, actual_one)
        next_script = []
        if all_script_ids.index(actual_one) + 1 != len(all_script_ids):
            next_script = script_obj.search(cr, uid, [('seq','=',actual_script.next)])
        return next_script and next_script[0]

#            if not actual_one:
#                script_obj.write(cr, uid, all_script_ids, {'next_one': False, 'actual_one':False})
#                return True

    def _set_next_one(self,cr, uid, ids, context={}):
        script_obj = self.pool.get('migrate.migrate.script')
        all_script_ids = script_obj.search(cr, uid, [('migrate_id','=',ids[0])])
        script_obj = self.pool.get('migrate.migrate.script')
        actual_one = self._get_actual_one(cr, uid, ids, context=context)
        next_one = self._get_next_one(cr, uid, ids, context)
        if not actual_one:
            actual_one = all_script_ids[0]
            script_obj.write(cr, uid, [actual_one], {'actual_one': True})
        else:
            script_obj.write(cr, uid, [actual_one], {'actual_one': False})
            script_obj.write(cr, uid, [next_one], {'next_one': False, 'actual_one': True})
        next_one = self._get_next_one(cr, uid, ids, context)
        if next_one:
            script_obj.write(cr, uid, [next_one], {'next_one': True})
            return True
        else:
            script_obj.write(cr, uid, all_script_ids, {'next_one': False,'actual_one': False})
            return False

    def run(self,cr, uid, ids, context={}):
        script_obj = self.pool.get('migrate.migrate.script')
        data = {'id':ids[0], 'form':{}}
        FIELDS = {}
        FIELDS.update(self._get_fields(cr, uid, data, context))
        data['form'] = self._get_values(cr, uid, data, context)
        res = self._list_db(cr, uid, data, FIELDS, context={})
        FIELDS.update(res['FIELDS'])
        res = self._get_cursor(cr, uid, data, context=context)
        cr_from, cr_to = res['cr_from'], res['cr_to']
        all_script_ids = script_obj.search(cr, uid, [('migrate_id','=',ids[0])])
        actual_one = self._get_actual_one(cr, uid, ids, context=context)
        if not actual_one:
            to_execute = all_script_ids[0]
        else:
            to_execute = self._get_next_one(cr, uid, ids, context)
            if not to_execute:
                return self._set_next_one(cr, uid, ids, context=context)
        to_execute_script = script_obj.browse(cr, uid, to_execute)
#        process = True
        if to_execute_script.python:
            localdic = {'pool':pooler.get_pool(cr.dbname), 'cr':cr, 'uid':uid, 'cr_from':cr_from, 'cr_to':cr_to, 'id':data['id']}
            exec to_execute_script.python in localdic
        return self._set_next_one(cr, uid, ids, context=context)

    def active_script(self,cr, uid, ids, context={}):
        script_ids = self.pool.get('migrate.migrate.script').search(cr, uid, [('migrate_id','=',ids[0]),('active','=',False)])
        return self.pool.get('migrate.migrate.script').write(cr, uid, script_ids, {'active': True})

migrate_migrate()

class migrate_migrate_script(osv.osv):
    _name = "migrate.migrate.script"
    _description = "Data Base Migrate Script"
    _order = "seq"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'migrate_id': fields.many2one('migrate.migrate', 'Migrate', required=True, select=True, ondelete='cascade'),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the script line without removing it."),
        'next': fields.integer('Next'),
        'actual_one': fields.boolean('Actual One'),
        'next_one': fields.boolean('Next One'),
        'seq': fields.integer('Sequence', required=True),
        'python': fields.text('Paython Code'),
        'object_id': fields.many2one('migrate.migrate.module', 'Object', select=True),
        'note': fields.text('Note'),
    }

    _defaults = {
        'active': 1,
        'next': 0,
    }

migrate_migrate_script()

#----------------------------------------------------------
# Migrate Utilities
#----------------------------------------------------------
SEPARATOR = [('d',''),('n','New Line'),('nt','New Line + Tab'), ('t','Tab'), ('s','Space')]

class migrate_migrate_utilities(osv.osv):
    _name = "migrate.migrate.utilities"
    _description = "Data Base Migrate Utilities"
    _order = "name"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'free_utility': fields.text('Free Utility'),
        'object_utility': fields.text('Object Utility'),
        'field_utility': fields.text('Field Utility'),
        'related_utility': fields.text('Related Utility'),
        'free_parameters': fields.char('Free Parameters', size=64),
        'object_parameters': fields.char('Object Parameters', size=64, help='object_name, field_name, related_object, related_field'),
        'field_parameters': fields.char('Field Parameters', size=64, help='object_name, field_name, related_object, related_field'),
        'related_parameters': fields.char('Related Parameters', size=64),
        'separator_1': fields.selection(SEPARATOR, 'Separator'),
        'separator_2': fields.selection(SEPARATOR, 'Separator'),
        'separator_3': fields.selection(SEPARATOR, 'Separator'),
        'note': fields.text('Note'),
    }
    _defaults = {
        'free_utility': lambda *a: ''' ''',
        'object_utility': lambda *a: '''mig_obj = pool.get('migrate.migrate')\nmod_obj = pool.get('migrate.migrate.module')\nfield_obj = pool.get('migrate.migrate.field')\nobject_id = mod_obj.search(cr, uid, [('migrate_id','=',id),('name','=','%s')])\nif object_id:\n''',
        'field_utility': lambda *a: '''#Field\n    fid = field_obj.search(cr, uid, [('module_id','=',object_id[0]),('name','=','%s')])\n    field_obj.write(cr, uid, fid, {'include':True})''',
        'free_parameters': lambda *a: '',
        'object_parameters': lambda *a: 'object_name',
        'field_parameters': lambda *a: 'field_name',
    }

migrate_migrate_utilities()

class migrate_utilities(osv.osv):
    _name = "migrate.utilities"
    _description = "Data Base Migrate Utilities"
    _order = "name"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'free_utility': fields.text('Free Utility'),
        'object_utility': fields.text('Object Utility'),
        'field_utility': fields.text('Field Utility'),
        'related_utility': fields.text('Related Utility'),
        'free_parameters': fields.char('Free Parameters', size=64),
        'object_parameters': fields.char('Object Parameters', size=64, help='object_name, field_name, related_object, related_field'),
        'field_parameters': fields.char('Field Parameters', size=64, help='object_name, field_name, related_object, related_field'),
        'related_parameters': fields.char('Related Parameters', size=64),
        'separator_1': fields.selection(SEPARATOR, 'Separator'),
        'separator_2': fields.selection(SEPARATOR, 'Separator'),
        'separator_3': fields.selection(SEPARATOR, 'Separator'),
        'note': fields.text('Note'),
    }
    _defaults = {
        'free_utility': lambda *a: ''' ''',
        'object_utility': lambda *a: '''mig_obj = pool.get('migrate.migrate')\nmod_obj = pool.get('migrate.migrate.module')\nfield_obj = pool.get('migrate.migrate.field')\nobject_id = mod_obj.search(cr, uid, [('migrate_id','=',id),('name','=','%s')])\nif object_id:\n''',
        'field_utility': lambda *a: '''#Field\n    fid = field_obj.search(cr, uid, [('module_id','=',object_id[0]),('name','=','%s')])\n    field_obj.write(cr, uid, fid, {'include':True})''',
        'free_parameters': lambda *a: '',
        'object_parameters': lambda *a: 'object_name',
        'field_parameters': lambda *a: 'field_name',
    }

migrate_utilities()

class migrate_python_utilities(osv.osv):
    _name = "migrate.python.utilities"
    _description = "Data Base Migrate Python Utilities"
    _order = "name"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'python': fields.text('Python Code'),
        'note': fields.text('Note'),
        'type': fields.selection([('python','Only Python'), ('field','Only Fields')], 'Type', help='Select Only Python to define only paython code, select Only Field to define action on fields.' ),
    }

    _defaults = {
        'type': lambda *a: 'python',
    }

migrate_python_utilities()

#----------------------------------------------------------
# Migrate Modules
#----------------------------------------------------------
class migrate_migrate_module(osv.osv):
    _name = "migrate.migrate.module"
    _description = "Data Base Migrate Module"

#    def create(self, cr, uid, vals, context=None):
#        seq = 0
#        if 'line_ids' in vals:
#            for line in vals['line_ids']:
#                seq += 1
#                line[2]['sequence'] = seq
#                vals[seq - 1] = line
#        return super(account_bank_statement, self).create(cr, uid, vals, context=context)

    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'migrate_id': fields.many2one('migrate.migrate', 'Migrate', required=True, select=True, ondelete='cascade'),
        'reg': fields.integer('Registers'),
        'seq': fields.integer('Sequence', required=True),
        'id_seq': fields.integer('IDSeq'),
        'model_org': fields.char('Model ORG', size=64),
        'model_dest': fields.char('Model DEST', size=64), #fields.many2one('ir.model', 'Model DEST'),
        'field_ids': fields.one2many('migrate.migrate.field', 'module_id', 'Fields'),
        'state': fields.selection([('draft','Draft'), ('field','Fields Loaded'), ('done','Done')], 'Status', readonly=True),
        'note': fields.text('Note'),
        'code': fields.boolean('Code'),
    }

    _defaults = {
        'state': lambda *a: 'draft',
    }
    _order = 'seq, model_org'
#    _order = 'include desc,seq,model_org'

    def cancel(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'draft'})

    def field(self,cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'field'})

migrate_migrate_module()

#----------------------------------------------------------
# Migrate Field
#----------------------------------------------------------
class migrate_migrate_field(osv.osv):
    _name = "migrate.migrate.field"
    _description = "Data Base Migrate Field"
    _order = "name"

    def __code(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for field in self.browse(cr, uid, ids, context=context):
            code = True
            if field.python == '''# result = "python code or constant" ''' or not field.python:
                code = False
            res[field.id] = code
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'module_id': fields.many2one('migrate.migrate.module', 'Migrate', required=True, select=True, ondelete='cascade'),
#        'seq': fields.integer('Seq', required=True),
        'field_org': fields.char('Field ORG', size=64),
        'field_dest': fields.char('Field DEST', size=64), #fields.many2one('ir.model.fields', 'Field DEST'),
        'field_org_type': fields.char('Field ORG Type', size=64),
        'field_dest_type': fields.char('Field DEST Type', size=64),
        'include': fields.boolean('Include'),
        'order': fields.boolean('Order by'),
        'code': fields.boolean('Code'),
        'code': fields.function(__code, method=True, type='boolean', string='Code'),
        'python': fields.text('Paython Code'),
        'localdic': fields.text('Localdic'),
        'include_reg': fields.text('Include Register'),
        'exclude_reg': fields.text('Exclude Register'),
    }

    _defaults = {
        'include': lambda *a: False,
        'localdic': lambda *a: "{'cr_from': cr_from, 'cr_to': cr_to, 'field': field, 'reg': reg, 'pool': pooler.get_pool(cr.dbname), 'cr': cr, 'uid': uid, 'val':val}",
        'python': lambda *a: '''# result = "python code or constant" ''',
    }

    def onchange_field_id(self, cr, uid, ids, field_dest):
        if not field_dest:
            result = {'value': {'field_dest_type': False}}
        else:
            ttype = self.pool.get('ir.model.fields').browse(cr, uid, field_dest).ttype
            result = {'value': {'field_dest_type': ttype}}
        return result

migrate_migrate_field()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

