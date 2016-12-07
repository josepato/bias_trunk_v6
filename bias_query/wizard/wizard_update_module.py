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

import wizard
import pooler
import tools
import os


query_form = '''<?xml version="1.0"?>
<form string="Update Module Querys">
 <field name="module" />
</form>'''

query_fields = {
    'module': {'string': 'Module', 'type': 'many2one', 'relation':'ir.module.module', 'help': 'Update the sql files of the selected Module. You need to crear a folder with the name sql on the root of the module. Inside of that folder place all the fiel.sql files', 'required':True},
    }





succes_form = '''<?xml version="1.0"?>
<form string="Liquidation">
    <label string="Liquidation Stored Succesfully!" colspan="4"/>
</form>'''

succes_fields = {}


class wizard_update_module(wizard.interface):


    def _check_user(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        for group in pool.get('res.users').browse(cr, uid, uid).groups_id:
            if group.name == 'Query / Manager':
                return 'update'
        return 'end'

    def _action_load_label(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        module_name = pool.get('ir.module.module').browse(cr, uid, data['form']['module']).name
        path = tools.config['root_path']
        path += '/addons/' + module_name + '/sql'
	print 'path',path
        files = self._get_ls_files(cr, path, '*.sql')
	print 'files', files
        for sql in files.keys():	    
            cr.execute(files[sql])
        return {}



    def _get_ls_files(self, cr, path, search=''):
        fid_files = os.popen('ls -m %s/%s'%(path,search))
        files = fid_files.read()
        fid_files.close()
        files = files.strip('')     
        files = files.strip('\n')
        files = files.split(',')
        res = {}
        for ff in files:
            ff = ff.strip('')
            ff = ff.strip('\n')
            fid =  os.popen('less %s'%(ff))
            ff = ff.split('/')[-1:]
            sql = fid.read()
            fid.close()
            res[ff[0]] = sql
        return res

    


    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_user}
            },
        'update': {
            'actions': [],
            'result': {
                'type': 'form',	'arch': query_form,	'fields': query_fields,
                'state': [('end', 'Cancel'), ('update_action', 'Update', 'gtk-execute')]
                }
            },
        'update_action': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_load_label, 'state':'succes'}
            },
        'succes': {
            'actions': [],
            'result': {
                'type': 'form',	'arch': succes_form,	'fields': succes_fields,
                'state': [('end', 'Thanks'),]
                }
            },
	}

wizard_update_module('wizard.update.module')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
