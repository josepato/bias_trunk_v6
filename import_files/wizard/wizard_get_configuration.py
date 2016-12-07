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
import os
import pooler
import time
import StringIO
import base64
from tempfile import TemporaryFile


ask_form ='''<?xml version="1.0"?>
<form string="Restart">
    <label string="Do you Want to Import or Export information?" colspan="4"/>
</form>
'''


export_form ='''<?xml version="1.0"?>
<form string="Export">
    <label string="Save Data on wanted file" colspan="4"/>
    <field name="object_information" width="200"/>
</form>
'''

export_fiels={
    'object_information':{'string':'Object Information', 'type': 'binary'}
    

}


import_form ='''<?xml version="1.0"?>
<form string="Import Data">
    <label string="Select Data File and click on Import" colspan="4"/>
    <field name="object_information" width="200"/>
</form>
'''

import_fiels={
    'object_information':{'string':'Object Information', 'type': 'binary'}
    

}



import_done_form ='''<?xml version="1.0"?>
<form string="Import Data Done!">
    <label string="Succesful Importation!!!!" colspan="4"/>

</form>
'''


class get_configuration(wizard.interface):



    def _start(self, cr, uid, data, context):
        print 'data', data
        import_file_obj = pooler.get_pool(cr.dbname).get('import.file')
        import_file_brw = import_file_obj.browse(cr, uid, data['ids'])
        for file_brw in import_file_brw:
            object_information = import_file_obj.copy_data(cr, uid, file_brw.id)
            try:
                object_information[0]['name'] = object_information[0]['name']
            except KeyError:
                object_information['name'] = object_information['name']
            #import_file_obj.create(cr, uid, object_information[0])
        buf = StringIO.StringIO()
        try:
            writer = buf.write(object_information[0])
        except KeyError:
            writer = buf.write(object_information)
	out = base64.encodestring(buf.getvalue())
	buf.close()
        return {'object_information':out}

    
    def import_record(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        object_info = data['form']['object_information']
        fileobj = TemporaryFile('w+')
        fileobj.write( base64.decodestring(object_info) )
        fileobj.seek(0)
        data_dir = fileobj.read()
        # now we determine the file format
        restart_brw = pool.get('import.file').create(cr, uid, eval(data_dir))
        print 'restart_brw',restart_brw
        return {}
    
    def _restart(self, cr, uid, data, context):
        self.create_record(cr, uid, data, context)
        fid = os.popen('python /usr/local/bin/restart_open.py&')
        fid.close()
        return {}
            


    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': ask_form,
                'fields': {},
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('import', 'Import Object', 'gtk-ok', True),                
                    ('export', 'Export Object', 'gtk-ok', True)
                ]
            }
        },
        'export': {
            'actions': [_start],
            'result': {
                'type': 'form',
                'arch': export_form,
                'fields': export_fiels,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                ]
            }
        },
        'import': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': import_form,
                'fields':import_fiels,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start_import', 'Import Object', 'gtk-ok', True),                
                ]
            }
        },


        'start_import': {
            'actions': [import_record],
            'result': {
                'type': 'form',
                'arch': import_done_form,
                'fields':{},
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                ]
            }
        },
        'restart': {
                 'actions': [],
                 'result': {'type': 'action', 'action': _restart, 'state':'end'}
                 },

        }
get_configuration('get.configuration')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
