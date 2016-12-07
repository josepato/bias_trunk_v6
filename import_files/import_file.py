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
import base64
import tools
from tempfile import TemporaryFile
import csv
import re


class field_selection(osv.osv):
    _name = 'field.selection'
    _description = "Field Selection"
    _columns = {
        'name': fields.char('Name', size=64, required=True, ),
        'code': fields.char('Code', size=64, required=True, ),
        'type':fields.char('Type', size=64,  ),
        'relation':fields.char('Relation', size=64, ),
        'model': fields.many2one('ir.model','Model Name', required=True, ),
    }



field_selection()

#----------------------------------------------------------
# Catalog Import
#----------------------------------------------------------

class import_file(osv.osv):
    _name = 'import.file'
    _description = "Import Fiels"
    _columns = {
        'name': fields.char('Name', size=64, required=True, ),
        'active': fields.boolean('Active'),
        'record_per_line': fields.boolean('Record per Line'),        
        'configured': fields.boolean('Confiugred'),
        'update': fields.boolean('Update'),
        'user_id': fields.many2one('res.users', 'User', ),
        'path':fields.binary('File Path', ),
        'model': fields.many2one('ir.model','Model Name', required=True, ),
        'field_ids': fields.one2many('import.file.columns', 'file_id', 'Fields to Import'),
        'state': fields.selection([('draft','Draft'),('partial','Partial'),('done','Done')], 'Status', required=True, readonly=True),
    }




    _defaults = {
        'active': lambda *a: 1,
        'state': lambda *a:'draft',
    }



    def button_populete_field_type(self, cr, uid, ids, context={}):
        for line in self.browse(cr, uid, ids, context):
            self.populate_field_type(cr, uid, line.model, context)
        return True

    def button_get_columns(self, cr, uid, ids, context={}):
        for line in self.browse(cr, uid, ids, context):
            self.populate_field_type(cr, uid, line.model, context)
            self._define_fields(cr, uid, line, context)
        return True

    def get_alternative_value(self, cr, uid, column_brw, col_value = ''):
        if column_brw.field_id:
            if column_brw.altre_value_type == 'id':
                if type(column_brw.alter_value).__name__ != 'int':
                    return int(column_brw.alter_value)
                else:
                    return column_brw.alter_value
            if column_brw.value == 'of_column':
                value_to_search = col_value
            elif column_brw.value == 'this':
                value_to_search =  column_brw.alter_value
            else:
                value_to_search =  column_brw.alter_value

            query = "SELECT id FROM %s where %s ilike '%s'"%(re.sub('\.','_',column_brw.field_id.relation), column_brw.altre_value_type, value_to_search)
            cr.execute(query)
            value_id = cr.fetchall()
            if value_id:
                if len(value_id) > 1:
                    raise osv.except_osv(('Warning !'),('More than one value for %s!'%(value_to_search)))
                return value_id[0][0]
        return ''
        
        



        
    def get_column_value(self, cr, uid, line_brw, column_brw, row):
        file_description_obj  = self.pool.get('file.description')
        if column_brw.value == 'of_column':
            query = "Select name from file_description where row_number = %s and column_name = '%s' and file_id = %s"%(row[0], column_brw.name, line_brw.id)
            cr.execute(query)
            col_name = cr.fetchone()
            if col_name:
                if column_brw.field_id.ttype in ('many2one','many2many'):
                    if column_brw.altre_value_type in ('name', 'code', 'default_code'):
                        return self.get_alternative_value(cr, uid, column_brw, col_name[0])
                        value_id = self.pool.get(column_brw.field_id.relation).search(cr, uid, [(column_brw.altre_value_type, '=', col_name[0])])
                        if value_id:
                            return value_id[0]
                        return ''
                if column_brw.field_id.ttype == 'float' and col_name[0]:
                    return float(col_name[0])
                return col_name[0]
            else:
                return ''
        if column_brw.value == 'this':
            return column_brw.alter_value

        if column_brw.value == 'alternative':
            value = self.get_alternative_value(cr, uid, column_brw)
            return value
        else:
            return ''


    #def create_row_directory(self, cr, uid, brw_record):
    def get_update_id(self, cr, uid, line_brw, column_brw, row):
        query = "Select name from file_description where row_number = %s and column_name = '%s' and file_id = %s"%(row[0], column_brw.name, line_brw.id)
        cr.execute(query)
        col_name = cr.fetchone()
        if col_name:
            res_id = self.pool.get(line_brw.model.model).search(cr, uid, [(column_brw.field_id.name,'=',col_name[0])])
            if res_id:
                return res_id
            else:
                return False
        else:
            return False

    def get_update_values(self, res, update_dir):
        new_res = {}
        for field in update_dir:
            new_res[field.values()[0]] = res[field.values()[0]]
        return  new_res

    
    def button_get_file_data(self, cr, uid, ids, context={}):
        for line in self.browse(cr, uid, ids, context):
            query = 'select distinct(row_number) from file_description where file_id = %s order by row_number'%(line.id)
            cr.execute(query)
            filds_rows = cr.fetchall()
            res = {}
            all_res = ()
            start = False
            if line.update:
                query = "select distinct(f.name) from import_file_columns i left join ir_model_fields f on (i.field_id = f.id)  where i.file_id =%s and i.update_value='t'"%(line.id)
                cr.execute(query)
                update_dir = cr.dictfetchall()
            for row in filds_rows:
                one2many_fields = {}
                required = True
                update_id = False
                for column in line.field_ids:
                    lines_dir = {}
                    new_line = False
                    if column.field_id.id:
                        has_value_on_file = self.get_column_value(cr, uid, line, column, row)
                        if has_value_on_file:
                            if column.field_id.ttype in ('char', 'binary', 'boolean','date','datetime', 'float','integer','reference','text','selection', 'many2one'):
                                result = self.get_column_value(cr, uid, line, column, row)
                                if column.required and not result:
                                    required = False
                                if result:
                                    if column.field_id.ttype  == 'boolean':
                                        try:
                                            result = re.sub('False','0',result)
                                            result = re.sub('FALSE','0',result)
                                            result = re.sub('True','1',result)
                                            result = re.sub('TRUE','1',result)
                                            result = int(result)
                                        except ValueError:
                                            raise osv.except_osv(('Warning !'),('Boolean type data has to be in form of 1 and 0 or True and False!'))
                                    res[column.field_id.name] = result
                                    new_line = True
                            elif column.field_id.ttype =='many2many':
                                #res[column.field_id.name] = [(6,0,(1,))]
                                col_value = ()
                                if column.field_ids:
                                    for related_column in column.field_ids:
                                        col_value += (int(self.get_column_value(cr, uid, line, related_column, row)),)
                                else:
                                    col_value += (int(self.get_column_value(cr, uid, line, column, row)),)
                                res[column.field_id.name] = [(6,0,col_value)]
                            else:
                                for related_column in column.field_ids:
                                    col_value = self.get_column_value(cr, uid, line, related_column, row)
                                    if col_value:
                                        lines_dir[related_column.field_id.name] = col_value
                                    if related_column.required and not col_value:
                                        required = False
                                try:
                                    if not res[column.field_id.name]:
                                        res[column.field_id.name] = [(0, 0,lines_dir)]
                                    else:
                                        res[column.field_id.name].append((0, 0,lines_dir))
                                except KeyError:
                                    res[column.field_id.name] = [(0, 0,lines_dir)]


                        elif (not has_value_on_file) and (column.required):
                            required = False
                        else:
                            if column.field_id.ttype == 'one2many':
                                try:
                                    if not res[column.field_id.name]:
                                        res[column.field_id.name] = False
                                except KeyError:
                                    res[column.field_id.name] = False
                            else:
                                res[column.field_id.name] = False
##                            try:
##                                if not res[column.field_id.name]:
##                                    res[column.field_id.name] = False
##                            except KeyError:
##                                res[column.field_id.name] = False
                    if lines_dir and required:
                        if column.field_id.name in one2many_fields.keys():
                            one2many_fields[column.field_id.name].append((0, 0, lines_dir))
                        else:
                            one2many_fields[column.field_id.name] = [(0, 0, lines_dir), ]
                    if column.update:
                        update_id = self.get_update_id(cr, uid, line, column, row)
                for related_field in one2many_fields.keys():
                    if new_line or line.record_per_line:
                        if start:
                            all_res += (res,)
                        start = True
                        res[related_field] = one2many_fields[related_field]
##                    else:
##                        if not res[related_field]:
##                            print 'inicializaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
##                            res[related_field] = []
##                        try:
##                            print 'try append(one2many_fields[related_field]',res
##                            print 'res[related_field]',res[related_field]
##                            res[related_field].append(one2many_fields[related_field])
##                        except KeyError:
                            
##                            print 'except ', one2many_fields[related_field]
##                            res[related_field] = one2many_fields[related_field]
                        #res[related_field].append(one2many_fields[related_field])
                        #try:
                        #print 'append(one2many_fields[related_field]',res
                        #res[related_field].append(one2many_fields[related_field][0])
                        #except AttributeError:
                        #res[related_field] = one2many_fields[related_field]

                if required and line.record_per_line:
                    if required:
                        if update_id:
                            update_res = self.get_update_values(res, update_dir)
                            move_id = self.pool.get(line.model.model).write(cr, uid, update_id,  update_res)
                        else:
                            move_id = self.pool.get(line.model.model).create(cr, uid, res)
                        query = 'DELETE FROM  file_descriptions where row_number = %s and  file_id = %s'%(row[0], line.id )
                        cr.execute('DELETE FROM  file_description where row_number = %s and  file_id = %s'%(row[0], line.id ))
                        cr.commit()
                if required and not line.record_per_line:
                    query = 'DELETE FROM  file_descriptions where row_number = %s and  file_id = %s'%(row[0], line.id )
                    cr.execute('DELETE FROM  file_description where row_number = %s and  file_id = %s'%(row[0], line.id ))
            if not line.record_per_line:
                move_id = self.pool.get(line.model.model).create(cr, uid, res)
                cr.commit()



                    

        return True

    
    def button_importe_data(self, cr, uid, ids, context={}):
        for line in self.browse(cr, uid, ids, context):
            self.populate_describe_file(cr, uid, line, context)
            #self._define_fields(cr, uid, line, context)
        return True


    def populate_field_type(self, cr, uid, model, context):
        fields_dir = self.pool.get(model.model).fields_get(cr, uid, context=context)
        #self.pool.get('field.selection').unlink(cr, uid, self.pool.get('field.selection').search(cr, uid, []))
        for field in fields_dir.keys():
            if fields_dir[field].has_key('relation'):
                self.pool.get('field.selection').create(cr, uid, {'name':fields_dir[field]['string'], 'code':field, 'type':fields_dir[field]['type'], 'relation':fields_dir[field]['relation'], 'model':model.id})
            else:
                self.pool.get('field.selection').create(cr, uid, {'name':fields_dir[field]['string'], 'code':field, 'type':fields_dir[field]['type'], 'model':model.id})
        return True

    def _define_fields(self, cr, uid, file_brw, context ):
        fileobj = TemporaryFile('w+')
        fileobj.write( base64.decodestring(file_brw.path) )
        fileobj.seek(0)
        # now we determine the file format
        first_line = fileobj.readline().strip().replace('"', '')
        count = 0
        self.pool.get('import.file.columns').unlink(cr, uid, self.pool.get('import.file.columns').search(cr, uid, [('file_id','=',file_brw.id)]))
        for column in first_line.split(','):
            self.pool.get('import.file.columns').create(cr, uid, {'name':column, 'file_id':file_brw.id, 'model':file_brw.model.id, 'column_numbre':count, 'code':'code'})
            count += 1
        return True

    def populate_describe_file(self, cr, uid, file_brw, context):
        fileobj = TemporaryFile('w+')
        file_id = file_brw.id
        fileobj.write( base64.decodestring(file_brw.path) )
        fileobj.seek(0)
        lines = 'True'
        count = 0
        readFid = csv.reader(fileobj, delimiter=',', quotechar='"')
        #lines = readFid.next()
        for line in readFid:
            if count == 0:
                columns = line
            else:
                column_count = 0
                for row in line:
                    #row = row.strip('"')
                    directorio =  {'name':row, 'column_name':columns[column_count].strip('"'), 'row_number':count, 'file_id':file_id}
                    self.pool.get('file.description').create(cr, uid, {'name':row, 'column_name':columns[column_count].strip('"'), 'row_number':count, 'file_id':file_id})
                    column_count +=1
                    
            count += 1
            #lines = fileobj.readline()
        return True
        


        

import_file()


class import_file_columns(osv.osv):
    _name = 'import.file.columns'
    _description = "Import Fiels Colums"




    def _col_get(self, cr, user, context={}):
        result = []
        cols_ids = self.pool.get('field.selection').search(cr, user, [])
        for col in self.pool.get('field.selection').browse(cr, user, cols_ids):
            result.append( (col.code, col.name) )
        result.sort()
        return result


    
    _columns = {
        'name': fields.char('Column Name', size=64, required=True, ),
        'code': fields.char('Code', size=64, required=True, ),
        'active': fields.boolean('Active'),
        'required': fields.boolean('Required'),
        'update': fields.boolean('Update', help='If selected, it is used to search this value on the object, if so, it will update de record, if not find it will create a new record'),
        'update_value': fields.boolean('Update Value', help='If selected it will update this value, if not olny selected values'),
        'file_id': fields.many2one('import.file', 'File to Import', required=False, on_delete='cascade'),
        #'field_id': fields.many2one('field.selection', 'Field Name' ),
        'field_id': fields.many2one('ir.model.fields', 'Field Name' ),
        'value': fields.selection([('this', 'This'),
                                   ('of_column', 'Of Column'),
                                   ('alternative', 'Alternative'),
                                   ('null', 'Null'),
                                   ], 'Value', required=True),
        'alter_value': fields.char('Alternative Value', size=64,  ),
        'altre_value_type': fields.selection(
                                  [('', ''),
                                   ('id', 'ID'),
                                   ('name', 'Name'),
                                   ('code', 'Code'),
                                   ('default_code', 'Default Code'),
                                   ], 'Value Type'),
        'model': fields.many2one('ir.model','Model Name', required=True, ),
        'column_numbre':fields.integer('Column Numbre', ),
        'myself_id': fields.many2one('import.file.columns', 'From Field to Import', required=False, on_delete='cascade'),
        'field_ids': fields.one2many('import.file.columns', 'myself_id', 'Fields to Import'),

                
        }




    _defaults = {
        'active': lambda *a: 1,
        'required': lambda *a: 0,
        'value': lambda * a:'this',
        'code' : lambda * a:'code',

    }


        
    def button_confiugre_column(self, cr, uid, ids, context={}):
        line = self.browse(cr, uid, ids, context)[0]
        relation = line.field_id.relation
        related_obj = self.pool.get(relation)
        model_obj = self.pool.get('ir.model')
        model_id = model_obj.search(cr, uid, [('model','=', relation)])[0]
        fields = related_obj.fields_get(cr, uid)
        for column in fields.keys():
            if fields[column].has_key('required'):
                if fields[column]['required']:
                    model_fields_obj = self.pool.get('ir.model.fields')
                    model_fields_id = model_fields_obj.search(cr, uid, [('model_id','=', model_id ), ('name','=',column)])[0]
                    record = self.create(cr, uid, {'name':'/', 'myself_id':line.id,  'field_id': model_fields_id, 'model':model_id, 'column_numbre':1, 'code':'code'})

        #for line in self.browse(cr, uid, ids, context):
            #print 'line', line

            #self._define_fields(cr, uid, line, context)
        return True


import_file_columns()








class file_description(osv.osv):
    _name = 'file.description'
    _description = "File Description"
    _columns = {
        'name': fields.char('Name', size=64, required=False ),
        'column_name': fields.char('Column Name', size=64, required=True, ),
        'row_number':fields.integer('Row Number', required=True,),         
        'file_id': fields.many2one('import.file', 'File to Import', required=True, on_delete='cascade'),
    }



file_description()





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

