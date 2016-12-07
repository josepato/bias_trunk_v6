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
# Catalog Import
#----------------------------------------------------------

class catalog_import_file(osv.osv):
    _name = 'catalog.import.file'
    _description = "Import Catalogs Fiels"
    _columns = {
        'name': fields.char('Name', size=64, required=True, ),
        'active': fields.boolean('Active'),
        'user_id': fields.many2one('res.users', 'User', ),
        'path':fields.binary('File Path', ),
        'model': fields.char('Model Name', size=64, required=True, ),
    }




    _defaults = {
        'active': lambda *a: 1,
    }
    


catalog_import_file()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
