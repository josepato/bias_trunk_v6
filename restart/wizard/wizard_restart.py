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


ask_form ='''<?xml version="1.0"?>
<form string="Restart">
    <label string="Are you sure you whant to restart the OpenERP Server?" colspan="4"/>

</form>
'''


class restart(wizard.interface):
    def create_record(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        restart_brw = pool.get('restart.restart').create(cr, uid, {'user_id':uid, 'date':time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
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
                    ('restart', 'Restart Server', 'gtk-ok', True)
                ]
            }
        },
        'restart': {
                 'actions': [],
                 'result': {'type': 'action', 'action': _restart, 'state':'end'}
                 },

        }
restart('restart.restart')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
