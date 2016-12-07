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
import os

#----------------------------------------------------------
# Time Machine
#----------------------------------------------------------

class time_machine(osv.osv):
    _name = 'time.machine'
    _description = "Time Machine"
    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True),

    }




    _defaults = {
        
    }
    


time_machine()

class time_machine_date(osv.osv):
    _name = 'time.machine.date'
    _description = "Time Machine"
    _columns = {
        'date': fields.datetime('Date',required=True),
        'selected': fields.boolean('Select')

    }


    def populate_dates(self, cr, uid, files):
        query = 'DELETE FROM time_machine_date *'
        cr.execute(query)
        dates = []
        ids  =[]
        for data in files:
            data = data.split('-')
            if data:
                if data[2] in dates:
                    continue
                else:
                    date = data[1] + '/' + data[2]  + '/' + data[3] + ' ' + data[4][:2] + ':' + data[4][2:4] + ':' + data[4][4:6]
                    ids.append(self.create(cr, uid, {'date':date}))
                    dates.append(data[1])
        return ids, data[0]
                        
        



    _defaults = {
        
    }
    


time_machine_date()

class time_machine_hour(osv.osv):
    _name = 'time.machine.hour'
    _description = "Time Machine Hour"
    _columns = {
        'date': fields.datetime('Date & Hour'),
        'selected': fields.boolean('Select')
    }

    _defaults = {
        
    }


    def populate_hour(self, cr, uid, md5_file, diff_file):
        query = 'DELETE FROM time_machine_hour *'
        cr.execute(query)
        files = {'hour':[],}
        md5_hour = []
        ids = []
        date = ''
        for md5 in md5_file:
            data = md5.split('-')
            md5_hour.append(data[4][:2] + ':' + data[4][2:4] + ':' + data[4][4:6])
            #files['hour'].append(data[4][:2] + ':' + data[4][2:4] + ':' + data[4][4:6])
            files[data[4][:2] + ':' + data[4][2:4] + ':' + data[4][4:6]] = {'md5_name':md5}
            if not date:
                    date  = data[1] + '/' + data[2] +'/' + data[3]
        for diff in diff_file:
            data = diff.split('-')
            diff_hour = data[-2:][:1][0][:2] + ':' + data[-2:][:1][0][2:-2] + ':' +  data[-2:][:1][0][-2:]
            if diff_hour in md5_hour:
                files['hour'].append(diff_hour)
                files[diff_hour].update({'diff_name':diff})
                if not date:
                    date = data[1] + '/' + data[2] +'/' + data[3]

        for hr in files['hour']:
            datetime = date + ' ' + hr
            ids.append(self.create(cr, uid, {'date':datetime }))
        
        #dates = 
        return ids, files
                        
        



    


time_machine_hour()

class time_machine_configuration(osv.osv):
    _name = 'time.machine.configuration'
    _description = "Time Machine Configuration"
    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True),
        'local_path': fields.char('Local Path', size=256, required=True),
        'server': fields.char('Server', size=128, required=True),
        'database_user': fields.char('DataBase User', size=128, required=True),
    }




    _defaults = {
        'name': lambda *a: 'Time Machine Configuration',
        'local_path': lambda *a: '/var/lib/postgresql',
        'server': lambda *a: 'localhost',
        'database_user': lambda *a: 'openerp',
        
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'There can only be one Time Machine Configuration !'),]

    _order = 'name'


time_machine_configuration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

