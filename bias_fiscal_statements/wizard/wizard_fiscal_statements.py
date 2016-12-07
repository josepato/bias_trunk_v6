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
import wizard
import pooler
from tools.translate import _
import StringIO
import base64
import re

fiscal_form = '''<?xml version="1.0"?>
<form string="Estados Financieros">
        <field name="company_id" colspan="4"/>
        <newline/>
        <field name="fiscalyear"/>
        <field domain="[('fiscalyear_id','=',fiscalyear)]" name="period_id"/>
        <field name="fiscal_statements_id" colspan="4"/>
        <field name="level"/>
        <field name="message"/>
        <field name="name_1"/>
        <field name="title_1"/>
        <field name="name_2"/>
        <field name="title_2"/>
        <field name="message_text" nolabel="1" colspan="4"/>
</form>'''

fiscal_fields = {
    'company_id': {'string': 'Organizacion', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'period_id': {'string': 'Periodo', 'type': 'many2one', 'relation':'account.period', 'required': True},
    'fiscal_statements_id': {'string': 'Reporte', 'type': 'many2one', 'relation': 'fiscal.statements', 'required': True},
    'fiscalyear': {
        'string':'Ejercicio', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True,
        'help': 'Keep empty for all open fiscal year',
        'default': lambda *a:False},
    'level': {'string': 'Nivel', 'type': 'integer', 'default': lambda *a:1},
    'name_1': {'string': 'Nombre 1', 'type': 'char', 'size': 64, 'default': lambda *a: 'C.P. HORTENCIA MEDINA HERNANDEZ'},
    'title_1': {'string': 'Titulo 1', 'type': 'char', 'size': 64, 'default': lambda *a: 'No CED PROF   699403'},
    'name_2': {'string': 'Nombre 2', 'type': 'char', 'size': 64, 'default': lambda *a: 'LIC. JUAN  PABLO SALAZAR DUDREV'},
    'title_2': {'string': 'Titulo 2', 'type': 'char', 'size': 64, 'default': lambda *a: 'REPRESENTANTE LEGAL'},
    'message': {'string': 'Con Mensaje', 'type': 'boolean'},
    'message_text': {'string': 'Mensaje', 'type': 'text', 'default': lambda *a:
'"BAJO PROTESTA DE DECIR VERDAD MANIFIESTO QUE LAS CIFRAS CONTENIDAS EN ESTE ESTADO FINANCIERO \n \
SON VERACES Y CONTIENEN TODA LA INFORMACION REFERENTE A LA SITUACION FINANCIERA Y/O LOS \n \
ESTADOS DE LA EMPRESA, Y AFIRMO QUE SOY LEGALMENTE RESPONSABLE DE LA AUTENTICIDAD Y VERACIDAD \n \
DE LAS MISMAS ASUMIENDO ASIMISMO TODO TIPO DE RESPONSABILIDAD DERIVADA DE CUALQUIER DECLACION \n \
EN FALSO SOBRE LA MISMA" '
},
}

export_form = '''<?xml version="1.0"?>
<form string="Guardar Archivo .csv">
        <separator string="File" colspan="4"/>
    	<field name="file"/>
</form>'''

export_fields = {
	'file': {'string': 'Archivo', 'type': 'binary', 'help': 'File created for this report', 'readonly':True},

}



def _get_period(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    fiscalyear_obj = pool.get('account.fiscalyear')
    stm_obj = pool.get('fiscal.statements')
    print 'id=',data
    if data['model'] == 'fiscal.statements':
        statement = stm_obj.browse(cr, uid, data['id'])
    else: 
        statement = stm_obj.browse(cr, uid, stm_obj.search(cr, uid, [])[0])
    ids = pool.get('account.period').find(cr, uid, context=context)
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
    if user.company_id:
        company_id = user.company_id.id
    else:
        company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
    period_id = False
    if len(ids):
        period_id = ids[0]
    return {
        'fiscalyear': fiscalyear_obj.find(cr, uid),
        'company_id': company_id,
        'period_id': period_id,
        'name_1': statement.name_1,
        'title_1': statement.title_1,
        'name_2': statement.name_2,
        'title_2': statement.title_2,
        'message_text': statement.message_text,
        'fiscal_statements_id': data['id'],
    }


class wizard_fiscal_statements(wizard.interface):

    def _check_ouput_csv(self, cr, uid, data, context):
        import csv
        import types
        result = pooler.get_pool(cr.dbname).get('fiscal.statements').get_result(cr, uid, data, context)
        buf = StringIO.StringIO()
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
        buf.close()
        res = {}
        res['file'] = out
        return res

    def _check(self, cr, uid, data, context):
        format = pooler.get_pool(cr.dbname).get('fiscal.statements').browse(cr, uid, data['form']['fiscal_statements_id'], context).format
        if format == 'balance':
            return 'report_balance'           
        elif format == 'balance_1' and data['form']['message']:
            return 'report_balance_1_message'           
        elif format == 'balance_1':
            return 'report_balance_1'           
        elif data['form']['message']:
            return 'report_income_message'
        else:
            return 'report_income'

    states = {
        'init': {
            'actions': [_get_period],
            'result': {'type':'form', 'arch':fiscal_form, 'fields':fiscal_fields,
            'state':[('end','Cancel','gtk-cancel'),('report_csv','Excel','gtk-convert'),('checkreport','Print','gtk-print')]}
        },
        'report_csv': {
            'actions': [_check_ouput_csv],
            'result': {'type':'form','arch':export_form,'fields':export_fields,'state':[('end','Ok')]},
        },
        'checkreport': {
            'actions': [],
            'result': {'type':'choice','next_state':_check}
        },
        'report_balance': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_balance', 'state':'end'}
        },
        'report_balance_1': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_balance_1', 'state':'end'}
        },
        'report_balance_1_message': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_balance_1_message', 'state':'end'}
        },
        'report_income': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_income', 'state':'end'}
        },
        'report_income_message': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_income_message', 'state':'end'}
        },
    }
wizard_fiscal_statements('fiscal.statements')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

