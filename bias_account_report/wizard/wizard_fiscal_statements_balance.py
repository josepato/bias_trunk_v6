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
<form string="Fiscal Statements">
        <field name="company_id" colspan="4"/>
        <newline/>
        <field name="fiscalyear"/>
        <field domain="[('fiscalyear_id','=',fiscalyear)]" name="period_id"/>
        <field name="level"/>
        <field name="cost_center_id"/>
</form>'''

fiscal_fields = {
    'company_id': {'string': 'Company', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period', 'required': True},
    'fiscal_statements_id': {'string': 'Fiscal Statement', 'type': 'many2one', 'relation': 'fiscal.statements', 'readonly': True},
    'fiscalyear': {
        'string':'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True,
        'help': 'Keep empty for all open fiscal year',
        'default': lambda *a:False},
    'level': {'string': 'Level', 'type': 'integer', 'default': lambda *a:1},
    'cost_center_id': {'string': 'Cost Center', 'type': 'many2one', 'relation': 'account.cost.center', 'help': 'Keep empty for all cost centers'},
	'journal_ids': {'string': 'Journal', 'type': 'many2many', 'relation': 'account.journal', 'help': 'Keep empty for all journals'},
}

export_form = '''<?xml version="1.0"?>
<form string="Export Report">
        <separator string="File" colspan="4"/>
    	<field name="file"/>
</form>'''

export_fields = {
	'file': {'string': 'File', 'type': 'binary', 'help': 'File created for this report', 'readonly':True},

}



def _get_period(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    fiscalyear_obj = pool.get('account.fiscalyear')
    ids = pool.get('account.period').find(cr, uid, context=context)
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
    if user.company_id:
        company_id = user.company_id.id
    else:
        company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
    report_id = pool.get('financial.reports').search(cr, uid, [('company_id','=',company_id)])[0]
    statement = pool.get('financial.reports').browse(cr, uid, report_id).statement_balance_id.id
    period_id = False
    if len(ids):
        period_id = ids[0]
    return {
        'fiscalyear': fiscalyear_obj.find(cr, uid),
        'company_id': company_id,
        'period_id': period_id,
        'fiscal_statements_id': statement
    }


class wizard_fiscal_statements_balance(wizard.interface):

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
        'report_income': {
            'actions': [],
            'result': {'type':'print', 'report':'fiscal_statements_income', 'state':'end'}
        },
    }
wizard_fiscal_statements_balance('fiscal.statements.balance')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

