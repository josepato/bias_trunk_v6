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
import tools
import base64
import pooler
from tempfile import TemporaryFile

ask_form ='''<?xml version="1.0"?>
<form string="Restart">
    <label string="Are you sure you whant to restart the OpenERP Server?" colspan="4"/>
    <field name="name" width="200"/>
    <field name="date"/>

</form>
'''

fields_form={
    'name':{'string':'Language name', 'type':'char', 'size':64, 'required':True},
    'code':{'string':'Code (eg:en__US)', 'type':'char', 'size':5, 'required':True},

}

class wizard_import_file(wizard.interface):



    def _start(self, cr, uid, data, context):
        import_file_obj = pooler.get_pool(cr.dbname).get('import.file')
        import_file_brw = import_file_obj.browse(cr, uid, data['ids'])
        for file_brw in import_file_brw:
            object_information = import_file_obj.copy_data(cr, uid, file_brw.id)
            object_information[0]['name'] = object_information[0]['name'] + 'Copy'
            #import_file_obj.create(cr, uid, object_information[0])
        print 'va al return'
        return {'object_information':object_information[0]}

    def _define_fields(self, cr, uid, data, file_brw, context ):
        fileobj = TemporaryFile('w+')
        fileobj.write( base64.decodestring(file_brw.path) )
        fileobj.seek(0)
        # now we determine the file format
        first_line = fileobj.readline().strip().replace('"', '')
        #for column in first_line.split(','):
            #print 'first_line', first_line
        return True


    

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': ask_form,
                'fields': {},
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('restart', 'Restart Server', 'gtk-ok', True)
                ]
            }
        },
        'restart': {
                 'actions': [],
                 'result': {'type': 'form',
                            'arch':ask_form,
                            'fields':{},
                            'state': [
                                ('end', 'Cancel', 'gtk-cancel'),
                                ]
                            },

            }
        }

wizard_import_file('import.file')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
