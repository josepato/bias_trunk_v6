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

import time
import datetime
from mx.DateTime import *
import wizard
import pooler
from tools.translate import _
import StringIO
import base64
import re
from tools.misc import UpdateableStr
from string import find,lower, replace


FORM = UpdateableStr()
FIELDS = {}

result_FORM = UpdateableStr()
result_FIELDS = {}

error_form = '''<?xml version="1.0"?>
<form string="Run Query">
         <label string="User has no permitions to run this Query. Check with system Administrator!" colspan="4"/>
</form>'''

query_form = '''<?xml version="1.0"?>
<form string="Run Query">
        <separator string="File" colspan="4"/>
    	<field name="file.csv"/>
</form>'''

query_fields = {
	'file.csv': {'string': 'File (.csv Format)', 'type': 'binary', 'help': 'File created for this query, save it with .csv extension', 'readonly':True},
}

class wizard_run_query(wizard.interface):

    def comma_me(self,amount):
        if  type(amount) is float :
            amount = str('%.2f'%amount)
        else :
            amount = str(amount)
        if (amount == '0'):
            return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>,\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def _get_result_form(self, cr, uid, data, context):
        print '_get_result_form'
        pool = pooler.get_pool(cr.dbname)
        query = pool.get('query.tool').browse(cr, uid, data['id'])
        form = data['form']
        parameters_ids = query.parameters_ids
        result_FORM.string = '''<?xml version="1.0"?> <form string="Select Parameters"> '''
        result_FIELDS['result'] = {'string': 'Result', 'type': 'text', 'relation': False, 'required': False}
        result_FORM.string += '''<field name = "result" width="600" height="300" colspan="4" nolabel="1"/>'''
        result_FORM.string += '''</form>'''
        form['file.csv'], form['result'] = self._run_query(cr, uid, data, context)
        return form

    def _process_data(self, cr, uid, data, context):
        form = data['form']
        form['file.csv'], form['result'] = self._run_query(cr, uid, data, context)
        return form

    def _get_form(self, cr, uid, data, context):
        while FIELDS:
            FIELDS.popitem()
        pool = pooler.get_pool(cr.dbname)
        query = pool.get('query.tool').browse(cr, uid, data['id'])
        form = data['form']
        parameters_ids = query.parameters_ids
        FIELDS['header'] = {'string':"Include Header",'type':'boolean','default': lambda *a: True}
        FORM.string = '''<?xml version="1.0"?> <form string="Select Parameters"> <field name="header"/> <newline/> '''
        if query.no_result:
            FORM.string = '''<?xml version="1.0"?> <form string="Select Parameters"><newline/> '''
        for parameter in query.parameters_ids:
            f_type = parameter.f_type
            selection = parameter.selection and eval(parameter.selection)
            if f_type == 'orderby':
                f_type = 'selection'
                if query.label_ids:
                    selection = []
                    for label in query.label_ids:
                        selection.append((label.name, label.label_new or label.label))
                else:
                    f_type = 'char'
            elif f_type == 'selection':
                FIELDS[parameter.code] = {'string': parameter.name, 
                                    'type': f_type, 
                                    'selection': eval(parameter.selection or '[]'),
                                    'required': parameter.required}
            elif f_type == 'char':
                FIELDS[parameter.code] = {'string': parameter.name, 
                                    'type': f_type, 
                                    'size': 128,
                                    'required': parameter.required}
            elif f_type != 'newline':               
                FIELDS[parameter.code] = {'string': parameter.name, 
                                    'type': f_type, 
                                    'relation': parameter.relation and parameter.relation.model or False,
                                    'required': parameter.required}
            
            if f_type == 'newline':
                FORM.string += '''<newline/>'''
            else:
                FORM.string += '''<field name="'''+parameter.code+'''"/>'''
        FORM.string += '''</form>'''
        for p in query.parameters_ids:
            if p.f_type in ('many2one','integer'):
                default = int(p.default)
            elif p.f_type in ('many2many', 'one2many'):
                default = eval(p.default or '[]')
            elif p.f_type == 'selection':
                default = eval(p.default or '[]')
            else:
                default = p.default
            data['form'][p.code] = default
        return data['form']

    def _get_company(self, cr, uid):
        pool = pooler.get_pool(cr.dbname)
        return pool.get('res.users').browse(cr, uid, uid).company_id.name

    def _get_user_date(self, cr, uid):
        pool = pooler.get_pool(cr.dbname)
        return 'Generado por: ' + pool.get('res.users').browse(cr, uid, uid).name + ', Fecha de Consulta: ' + time.strftime('%d-%b-%Y')

    def _text2fieds(self, cr, uid, res):
        new_res = []
        flag = False
        text_labels = eval(res[0][res[0].keys()[0]])
        for r in res:
            row = {}
            if not flag:
                flag = True
                continue
            else:
                i = 0
                for k in text_labels:
                    
                    row[k] = eval(r[res[0].keys()[0]])[i]
                    i += 1
                new_res.append(row)
        return new_res

    def _run_query(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        query = pool.get('query.tool').browse(cr, uid, data['id'])
        import csv
        import types
        form = data['form']
        buf = StringIO.StringIO()
        if query.python:
            return False, 'Python Code not yet implemented, but it will be soon...'
        elif not query.query:
            raise wizard.except_wizard(_('Warning'), _('Not Query Defined !'))
        else:
            query_text, text = self._get_query_text(cr, uid, form, query)
            cr.execute(query_text)
            try:
                res = cr.dictfetchall()
            except:
                return False, 'OK'
            
        result = []
        if form['header']:
            result += [(self._get_company(cr, uid),)]
            result += [(self._get_user_date(cr, uid),)]
            result.append(['Titulo: ' + query.name])
            result.append([text]) 
            result.append(['']) 
        date_format, float_format = [], []
        if query.text2fields:
            res = self._text2fieds(cr, uid, res)
        if len(res[0].keys()) == len(query.label_ids):
            report_labels, labels = [], []
            for r in res[0].keys():
                new = filter(lambda x: x.label == r, query.label_ids)[0]
                labels.append((new.sequence, new.label_new or r, new.label, new.f_type))
            labels.sort()
            new_labels = [x[1] for x in labels]
            report_labels = [x[2] for x in labels]
            i = 0
            for data in labels:
                if data[3] == 'date':
                    date_format.append(i)
                elif data[3] == 'float':
                    float_format.append(i)
                i += 1
        else:
            new_labels = report_labels = res[0].keys()
        if not query.text2fields:
            result.append(tuple(new_labels))
        for r in res:
            i = 0
            row = []
            for field in report_labels:
#                row.append(i in date_format and time.strftime('%d-%m-%Y', time.strptime(r[field],'%Y-%m-%d')) or \
#                           i in float_format and self.comma_me(r[field]) or r[field])
                if r[field] == None or not r[field]:
                    row.append('')
#                    row.append(i in date_format and '')
                else:
                    row.append(i in date_format and time.strftime('%d-%m-%Y', time.strptime(r[field],'%Y-%m-%d')) or r[field])
                i += 1
            result.append(tuple(row))
        for data in result:
            row = []
            csvData = ''
            for d in data:
                if type(d).__name__ == 'unicode':
                    d = d.encode('utf-8')
                if type(d)==types.StringType:
                    csvData += (csvData and ',' or '') + '"' + str(d.replace('\n',' ').replace('\t',' ')) + '"'
                else:
                    csvData += (csvData and ',' or '') + str(d)
            buf.write(csvData+'\n')
        
        out=base64.encodestring(buf.getvalue())
        text = buf.getvalue()
        buf.close()
        return out, text

    def _create_file(self, cr, uid, data, context):
        res = {}
        res['file.csv'], text = self._run_query(cr, uid, data, context)
        return res

    def _get_query_text(self, cr, uid, form, query):
        pool = pooler.get_pool(cr.dbname)
        par = []
        text = ''
        query_append = ''
        for p in query.parameters_ids:
            if form[p.code]:
                value = form[p.code]
                if p.f_type in ('many2many'):
                     value = tuple(value[0][2])
                if p.f_type in ('one2many'):
                    new_value = []
                    for v in value:
                        new_value.append(v[1])
                    value = tuple(new_value)
                if p.python and p.localdic:
                    localdic = eval(p.localdic)
                    exec p.python in localdic
                    value = localdic['result']
                par.append((p.f_type == 'orderby' and str(value)) or value)
                if p.line_query:
                    query_append += ' ' + p.line_query + ' '
                text += (text and ', ' or '') + p.name + ': ' +  \
                (p.f_type == 'date' and time.strftime('%d-%b-%Y', time.strptime(value,'%Y-%m-%d')) or \
            p.f_type == 'many2one' and pool.get(p.relation.model).browse(cr, uid, value).name or \
            p.f_type == 'selection' and filter(lambda x: x[0] == value, eval(p.selection)) and filter(lambda x: x[0] == value, eval(p.selection))[0][1] or \
            str(value))
        query_text = query.query + query_append
        par = tuple(par) 
        if par:
            try:
                query_text = re.sub('\n', ' ', query_text%par )
            except:
                query_text = re.sub('\n', ' ', query_text )
                query_text = re.sub('\t', ' ', query_text )
                query_text = query_text.format(*par)
        else:
            query_text = re.sub('\n', ' ', query_text )
        return query_text, text

    def _action_load_label(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        query = pool.get('query.tool').browse(cr, uid, data['id'])
        import types
        form = data['form']
        if not query.query:
            raise wizard.except_wizard(_('Warning'), _('Not Query Defined !'))
        text = ''
        pool.get('query.label').unlink(cr, uid, [x.id for x in query.label_ids])
        query_text, text = self._get_query_text(cr, uid, form, query)
        cr.execute(query_text)
        res = cr.dictfetchall()
        if not res:
            raise wizard.except_wizard(_('Warning'), _('Not Result Query !'))
        sequence = 0
        if query.text2fields:
            res = self._text2fieds(cr, uid, res)
        for label in res[0].keys():
            sequence += 10
            value = {
                'sequence': sequence,
                'name': re.compile(r'\W+').sub('_',lower(label)),
                'query_id': data['id'],
                'label': label,
            }
            pool.get('query.label').create(cr, uid, value, context=context)
        return {}

    def _check_user(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        query = pool.get('query.tool').browse(cr, uid, data['id'])
        report_users  = [uid_id.id for uid_id in query.user_ids]
        if uid not in report_users:
            return 'error'
        elif query.no_result:
            return 'no_result'
        for group in pool.get('res.users').browse(cr, uid, uid).groups_id:
            if group.name == 'Query / Manager':
                return 'manager'
        return 'user'

    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_user}
        },
		'no_result': {
			'actions': [_get_form],
			'result': {
				'type': 'form',	'arch': FORM,	'fields': FIELDS,
				'state': [('end', 'Cancel'), ('open', 'Run')]
			}
		},
		'user': {
			'actions': [_get_form],
			'result': {
				'type': 'form',	'arch': FORM,	'fields': FIELDS,
				'state': [('end', 'Cancel'), ('report_csv','CSV File'), ('print', 'Print','gtk-print')]
			}
		},
		'manager': {
			'actions': [_get_form],
			'result': {
				'type': 'form',	'arch': FORM,	'fields': FIELDS,
				'state': [('end', 'Cancel'), ('report_csv','CSV File'), ('print', 'Print','gtk-print'), ('open', 'Display'),('label', 'Load Label')]
			}
		},
        'report_csv': {
            'actions': [_create_file],
            'result': {'type':'form','arch': query_form,'fields': query_fields,'state':[('end','Ok')]},
        },
        'report_csv_2': {
            'actions': [],
            'result': {'type':'form','arch': query_form,'fields': query_fields,'state':[('end','Ok')]},
        },
        'open': {
            'actions': [_get_result_form],
            'result': {'type':'form','arch': result_FORM,'fields': result_FIELDS,'state':[('report_csv_2','CSV File'),('print', 'Print','gtk-print'),('end','Ok')]},
        },
        'print': {
            'actions': [_process_data],
            'result': {'type':'print', 'report': 'query.print.report', 'state':'end'}
        },
        'label': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_load_label, 'state':'end'}
            
        },
        'error': {
            'actions': [],
            'result': {'type':'form', 'arch':error_form, 'fields':{},
                       'state':[('end','Ok')]}
            },
	}

wizard_run_query('wizard.run.query')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
