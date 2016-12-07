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
import os
import pooler
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
    <label string="Save the data on wanted file" colspan="4"/>
    <field name="object_information" width="400"/>
</form>
'''

export_fiels={
    'object_information':{'string':'Object Information', 'type': 'binary'}
    

}


import_form ='''<?xml version="1.0"?>
<form string="Import Data">
    <label string="Select the data File and click on Import" colspan="4"/>
    <field name="object_information" width="400"/>
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


class wizard_query_import_export(wizard.interface):



    def _start(self, cr, uid, data, context):
        import_file_obj = pooler.get_pool(cr.dbname).get(data['model'])
        import_file_brw = import_file_obj.browse(cr, uid, data['ids'])
        for file_brw in import_file_brw:
            object_information = import_file_obj.copy_data(cr, uid, file_brw.id)
            if type(object_information).__name__ in  (' tuple' 'list'):
                object_information = object_information[0]
            object_information['name'] = object_information['name']
	buf = StringIO.StringIO()
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
        restart_brw  = pool.get(data['model']).create(cr, uid, eval(data_dir))
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
                    ('end', 'Export', 'gtk-execute'),
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
                    ('start_import', 'Import Object', 'gtk-execute', True),                
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
        }

wizard_query_import_export('wizard.query.import.export')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
