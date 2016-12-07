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
import osv
import pooler
import os
import tools

#import zipfile

#import base64
#from tools.translate import _


ask_form ='''<?xml version="1.0"?>
<form string="Time Machine">
    <separator string="Recover Databases" colspan="4"/>
    <label string="Please click View Databases to see the available files to recover." colspan="4"/>

</form>
'''

search_form ='''<?xml version="1.0"?>
<form string="Time Machine">
    <label string="Select the Date of the Data Base you what to recover!" colspan="4"/>
     <field name="data_bases" colspan="4" height="300" width="200" nolabel="1"/>
    <label string="If you select more than one, only the first database will be generated!" colspan="4"/>

</form>
'''

search_fields = {
    'data_bases': {'string': 'Data Bases', 'type': 'one2many', 'relation': 'time.machine.date', 'help': 'Cheques of this payment', 'readonly':False},
}

search_hour_form ='''<?xml version="1.0"?>
<form string="Time Machine">
    <label string="Select the Hour of the day of the Data Base you what to recover!" colspan="4"/>
     <field name="data_hour" colspan="4" height="300" width="200" nolabel="1"/>
    <label string="If you select more than one, only the first database will be generated!" colspan="4"/>
</form>
'''

search_hour_fields = {
    'data_hour': {'string': 'Data Bases', 'type': 'one2many', 'relation': 'time.machine.hour', 'help': 'Cheques of this payment', 'readonly':False},
}

restore_day_form ='''<?xml version="1.0"?>
<form string="Time Machine">
    <label string="Restoration Done!" colspan="4"/>
</form>'''

restore_day_fields = {
    'name': {'string': 'Entry Name', 'type':'char', 'size': 64, 'required':False},
    }



class data_base_recover_wizard(wizard.interface):

    def _get_ls_files(self, path, search=''):
        fid_files = os.popen('ls -m %s/%s'%(path,search))
        files = fid_files.read()
        files = files.strip('')     
        files = files.strip('\n')
        files = files.split(',')
        res = []
        for ff in files:
            ff = ff.strip('')
            ff = ff.strip('\n')
            ff = ff.strip(path)

            #ff = ff.strip(search)
            res.append(ff)
        return res

    
    def import_info(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        data_path = pool.get('time.machine.configuration').search(cr, uid, [])[0]

        data_path = pool.get('time.machine.configuration').browse(cr, uid, data_path).local_path
        tar_files = self._get_ls_files(data_path,'*.dump*')
        ids , data_base_name= pool.get('time.machine.date').populate_dates(cr, uid, tar_files)
        data['data_base_name'] = data_base_name
        return {'data_bases':ids}

    def import_hour(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        data_path = pool.get('time.machine.configuration').search(cr, uid, [])[0]
        data_path = pool.get('time.machine.configuration').browse(cr, uid, data_path).local_path
        records = data['form']['data_bases']
        for rec in records:
            selected = rec[2]['selected']
            if selected:
                date = rec[2]['date'][:10]
                break
        md5_files = self._get_ls_files(data_path,'%s-%s*.md5'%(data['data_base_name'],date))
        diff_files = self._get_ls_files(data_path,'%s-%s*-diff'%(data['data_base_name'],date))
        #tar_files = self._get_ls_files(data_path,'*.dump*')
        ids, data_base_file = pool.get('time.machine.hour').populate_hour(cr, uid, md5_files, diff_files)
        data['data_base_file'] = data_base_file
        return {'data_hour':ids}

    def _restore_hour(self, cr, uid, data, context):
        data_base_file = data['data_base_file']
        records = data['form']['data_hour']
        for rec in records:
            selected = rec[2]['selected']
            if selected:
                datetime = rec[2]['date']
                break
        daba_base_hour_files = data_base_file[datetime[-8:]]
        md5_name = daba_base_hour_files['md5_name']
        diff_name = daba_base_hour_files['diff_name']
        diff_name = diff_name.rstrip('-diff')
        fid_files = os.popen('/usr/local/bin/dbdifrecover2 %s'%(diff_name))
        #restore_db_name = fid_files.read()
        fid_files.close()
        restore_db_name = md5_name.rstrip('.md5')
        restore_db_name = restore_db_name + '.dump'
        self.restore_daba_base(cr, uid, restore_db_name)
        return {}


    def _restore_day(self, cr, uid, data, context):
        db_name = data['data_base_name']
        records = data['form']['data_bases']
        date = self.get_date_selected(cr, uid, records)
        date, hr = date.split()
        hr = hr.replace(':','')
        #data_base_name = db_name + '-' + date + '-040701.dump.gz'
        data_base_name = db_name + '-' + date + '-' + hr + '.dump'
        res = self.restore_daba_base(cr, uid, data_base_name)
        return {}

    def get_date_selected(self, cr, uid, records):
        for rec in records:
            selected = rec[2]['selected']
            if selected:
                date = rec[2]['date']
                break
        return date

    def get_data_base(self, cr, uid, data, data_base_name):
        pool = pooler.get_pool(cr.dbname)
        config_id = pool.get('time.machine.configuration').search(cr, uid, [])[0]
        data_path = pool.get('time.machine.configuration').browse(cr, uid, config_id).local_path
        fid = os.popen('less %s/%s'%(data_path,data_base_name))
        data_base = fid.read()
        fid.close()
        data_base = self._make_file(cr, uid, data_base)
        return data_base
    

    def restore_daba_base(self, cr, uid, daba_base_name):
        daba_base_name_plain = daba_base_name.split('.')[0]
        pool = pooler.get_pool(cr.dbname)
        config_id = pool.get('time.machine.configuration').search(cr, uid, [])[0]
        data_path = pool.get('time.machine.configuration').browse(cr, uid, config_id).local_path
        database_user = pool.get('time.machine.configuration').browse(cr, uid, config_id).database_user
        crate_db = os.popen('createdb %s --encoding=UNICODE --username %s'%(daba_base_name_plain, database_user))
        crate_db.close()
        daba_base_location = data_path + '/' +  daba_base_name
        restore_db =  os.popen('psql -U %s -d %s -f %s'%(database_user, daba_base_name_plain ,daba_base_location))
        result = restore_db.read()
        reboot =  os.popen('psql -U %s -d %s -f %s'%(database_user, daba_base_name_plain ,daba_base_location))
        restore_db.close()
        return {}


    def _action_module_open(self, cr, uid, data, context):
        return {
            'domain': str([('name', '=', data['form']['module_name'])]),
            'name': 'Module List',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.module.module',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }


    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': ask_form,
                'fields': {},
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('import', 'View Databases', 'gtk-ok', True)
                ]
            }
        },
        'import': {
            'actions': [import_info],
            'result': {
                'type':'form',
                'arch':search_form,
                'fields':search_fields,
                'state':[('import_hour','Choose Hour'),('restore_day','Restore Day')]
            }
        },
        'import_hour': {
            'actions': [import_hour],
            'result': {
                'type':'form',
                'arch':search_hour_form,
                'fields':search_hour_fields,
                'state':[('restore_hour','Restore Day'),('end','Cancel')]
            }
        },
        'open_window': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_module_open, 'state':'end'}
        },
        'restore_day': {
            'actions': [_restore_day],
            'result': {
                       'type': 'form',
                       'arch':restore_day_form,
                       'fields':restore_day_fields,
                       'state':[('end','Done'),]
                       }
        },
        'restore_hour': {
            'actions': [_restore_hour],
            'result': {
                       'type': 'form',
                       'arch':restore_day_form,
                       'fields':restore_day_fields,
                       'state':[('end','Done'),]
                       }
        },


    }
data_base_recover_wizard('data.base.recover')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
