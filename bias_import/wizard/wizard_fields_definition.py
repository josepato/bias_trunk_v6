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



view_form="""<?xml version="1.0"?>
<form string="Field Selection">

  
        <separator string="Select the Field of the module for each column" colspan="4"/>
        <field name="column" width="200"/>
        <field name="fild"/>

</form>"""

fields_form={
    'name':{'string':'Column', 'type':'char', 'size':64, 'required':True},
    'code':{'string':'Data Base Field', 'type':'char', 'size':64, 'required':True},

}

class wizard_fields_definition(wizard.interface):

    def _import_lang(self, cr, uid, data, context):
        form=data['form']
        print 'data', data
        print '________________________________\n from', form
##        fileobj = TemporaryFile('w+')
##        fileobj.write( base64.decodestring(form['data']) )

##        # now we determine the file format
##        fileobj.seek(0)
##        first_line = fileobj.readline().strip().replace('"', '').replace(' ', '')
##        fileformat = first_line.endswith("type,name,res_id,src,value") and 'csv' or 'po'
##        fileobj.seek(0)

##        tools.trans_load_data(cr.dbname, fileobj, fileformat, form['code'], lang_name=form['name'])
##        fileobj.close()
        return {}

    states={
        'init':{
            'actions': [],
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state':[
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('finish', 'Ok', 'gtk-ok', True)
                           ]
                       }
            },
        'finish':{
            'actions':[],
            'result':{'type':'action', 'action':_import_lang, 'state':'end'}
            },
        }

    print 'states', states
wizard_fields_definition('catalog.fields.definition')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:




