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

report_form = '''<?xml version="1.0"?>
<form string="Parameters">
        <field name="account_id"/>
        <separator string="Date Filter" colspan="4"/>
        <field name="date1"/>
        <field name="date2"/>
</form>'''

report_fields = {
    'name':{'string':"Name",'type':'char', 'default': lambda *a: 'Balanza de Comprobación por Empresa'},
    'date1': {'string':'Start date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-01')},
    'date2': {'string':'End date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'account_id': {'string': 'Account', 'type': 'many2one', 'relation': 'account.account', 'help': 'This account and childs', 'required':True},
    'balance':{'string':"Only balances",'type':'boolean', 'default': lambda *a: True},
    'currency':{
        'string':"Currency",
        'type':'selection',
        'selection':[('none',' '),('mn','PESOS'),('usd','DOLARES')], 'default': lambda *a: 'none'
    },
    'result_selection':{
        'string':"Select",
        'type':'selection',
        'selection':[('account','Account'),('aged','Aged Trial Balance')], 'default': lambda *a: 'account'
    },
    'group_by':{
        'string':"Group By",
        'type':'selection',
        'selection':[('partner','Partner'),('account','Account')], 'default': lambda *a: 'partner'
    },
}

export_form = '''<?xml version="1.0"?>
<form string="Export Report">
        <separator string="File" colspan="4"/>
    	<field name="file.csv"/>
</form>'''

export_fields = {
	'file.csv': {'string': 'File (.csv Format)', 'type': 'binary', 'help': 'File created for this query, save it with .csv extension', 'readonly':True},

}

class wizard_financial_reports_balance_partner(wizard.interface):

    def _ouput_csv(self, cr, uid, data, context):
        import csv
        import types
        result = pooler.get_pool(cr.dbname).get('financial.reports').get_result(cr, uid, data, context)
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
        res['file.csv'] = out
        return res

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':report_form, 'fields':report_fields, 'state':[('end','Cancel','gtk-cancel'),('csv','Excel','gtk-convert'),('print','Print','gtk-print')]}
        },
        'csv': {
            'actions': [_ouput_csv],
            'result': {'type':'form','arch':export_form,'fields':export_fields,'state':[('end','Ok')]},
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'financial.reports_balance', 'state':'end'}
        },
    }
wizard_financial_reports_balance_partner('financial.reports.balance.partner')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
