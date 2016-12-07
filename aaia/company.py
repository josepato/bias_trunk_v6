# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenBIAS S. de R.L. de C.V. (http://bias.com.mx)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields

import tempfile, os
from subprocess import Popen, PIPE


class res_company(osv.osv):

    def attachACESFile(self, cr, uid, myid, fname):
        import base64
        datafname = self.downloadACESFile(cr, uid, myid, fname)
        data = base64.encodestring(open(datafname).read())
        res = self.read(cr, uid, myid, ['name'])
        mydict = {'name': fname,
                  'datas_fname': fname,
                  'res_name': res['name'],
                  'datas': data,
                  'res_model': 'res.company',
                  'type': 'binary',
                  'res_id': myid}
        attach_id = self.pool.get('ir.attachment').create(cr, uid, mydict)
        return attach_id
    
    def downloadACESFile(self, cr, uid, myid, fname):
        res = self.read(cr, uid, myid, ['aces_username', 'aces_password', 'aces_hostname', 'aces_portnum', 'aces_postgres_folder'])
        username = res['aces_username']
        passwd = res['aces_password']
        hostname = res['aces_hostname']
        portnum = res['aces_portnum']
        folder = res['aces_postgres_folder']
        uri = "ftps://%s:%i" %(hostname, portnum)
        outfname = tempfile.mktemp() + ".gz"
        cmdfname = tempfile.mktemp()
        fid = open(cmdfname, "w")
        fid.write("open %s\n" %(uri, ))
        fid.write("login %s %s\n" %(username, passwd))
        fid.write("cd %s\n" %(folder, ))
        fid.write("nlist\n")  ###### DO NOT ERASE, WILL NOT WORK WITHOUT IT!!!!!
        fid.write('get "%s" -o %s\n' %(fname, outfname, ))
        fid.close()
        cmdstr = "/usr/bin/lftp -f %s" %(cmdfname, )
        pp = Popen(cmdstr.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        (outdata, errdata) = pp.communicate()
        if pp.returncode:
            raise osv.except_osv(('Error !'), ('Error en la conexion al serivdor de ACES\n' + errdata))
        os.remove(cmdfname)
        return outfname

    def getFileList(self, cr, uid, myid):
        res = self.read(cr, uid, myid, ['aces_username', 'aces_password', 'aces_hostname', 'aces_portnum', 'aces_postgres_folder'])
        username = res['aces_username']
        passwd = res['aces_password']
        hostname = res['aces_hostname']
        portnum = res['aces_portnum']
        folder = res['aces_postgres_folder']
        uri = "ftps://%s:%i" %(hostname, portnum)
        cmdfname = tempfile.mktemp()
        fid = open(cmdfname, "w")
        fid.write("open %s\n" %(uri, ))
        fid.write("login %s %s\n" %(username, passwd))
        fid.write("cd %s\n" %(folder, ))
        fid.write("nlist\n")
        fid.close()
        cmdstr = "/usr/bin/lftp -f %s" %(cmdfname, )
        pp = Popen(cmdstr.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        (outdata, errdata) = pp.communicate()
        if pp.returncode:
            raise osv.except_osv(('Error !'), ('Error en la conexion al serivdor de ACES\n' + errdata))
        os.remove(cmdfname)
        return outdata.split("\n")[:-1]


    _inherit = "res.company"
    _columns = {'aces_username': fields.char('ACES username', size=40),
                'aces_password': fields.char('ACES password', size=40),
                'aces_hostname': fields.char('ACES hostname', size=80),
                'aces_portnum': fields.integer('ACES port number'),
                'aces_postgres_folder': fields.char('Postgres folder', size=80)
                }

res_company()
