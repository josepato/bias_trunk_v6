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
        <field name="detail"/>
        <separator string="Date Filter" colspan="4"/>
        <field name="date2"/>
</form>'''

report_fields = {
    'name':{'string':"Name",'type':'char', 'default': lambda *a: 'Antigüedad de Saldos Acreedores'},
    'date1': {'string':'Start date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-01')},
    'date2': {'string':'To date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'account_id': {'string': 'Account', 'type': 'many2one', 'relation': 'account.account', 'help': 'This account and childs', 'required':True},
    'balance':{'string':"Only balances",'type':'boolean', 'default': lambda *a: False},
    'currency':{
        'string':"Currency",
        'type':'selection',
        'selection':[('none',' '),('MN','PESOS'),('USD','DOLARES')], 'default': lambda *a: 'none'
    },
    'result_selection':{
        'string':"Select",
        'type':'selection',
        'selection':[('account','Account'),('aged','Aged Trial Balance')], 'default': lambda *a: 'aged'
    },
    'detail':{
        'string':"Detail",
        'type':'selection',
        'selection':[('detail','Detail'),('balance','Balance')], 'default': lambda *a: 'detail'
    },
    'period_length': {'string': 'Period length (days)', 'type': 'integer', 'required': False, 'default': lambda *a:30},
    'group_by':{
        'string':"Group By",
        'type':'selection',
        'selection':[('partner','Partner'),('account','Account')], 'default': lambda *a: 'partner'
    },
    'partner_type':{
        'string':"Partner Type",
        'type':'selection',
        'selection':[('none','None'),('customer','Customer'),('supplier','Supplier'),('creditor','Creditor')], 'default': lambda *a: 'creditor',
    },
    'report_zero':{
        'string':"Report Zeros",
        'type':'selection',
        'selection':[('zero','Yes'),('no_zero','Not')], 'default': lambda *a: 'no_zero',
    },
}

export_form = '''<?xml version="1.0"?>
<form string="Export Report">
        <separator string="File" colspan="4"/>
    	<field name="file"/>
</form>'''

export_fields = {
	'file': {'string': 'File', 'type': 'binary', 'help': 'File created for this report', 'readonly':True},

}

class wizard_financial_reports_aged_creditor(wizard.interface):

    def _calc_dates(self, cr, uid, data, context):
        data['form']['date1'] = data['form']['date2']
        if data['form']['detail'] == 'balance':
            data['form']['balance'] = True
        res = {}
        period_length = data['form']['period_length']
        if period_length<=0:
            raise wizard.except_wizard(_('UserError'), _('You must enter a period length that cannot be 0 or below !'))
        start = datetime.date.fromtimestamp(time.mktime(time.strptime(data['form']['date1'],"%Y-%m-%d")))
        start = DateTime(int(start.year),int(start.month),int(start.day))
        for i in range(3)[::-1]:
            stop = start - RelativeDateTime(days=period_length)
            res[str(i)] = {
                    'name' : str((3-(i+1))*period_length) + '-' + str((3-i)*period_length),
                    'name_stop' : str((3-i)*period_length),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start' : stop.strftime('%Y-%m-%d'),
                    }
            start = stop - RelativeDateTime(days=1)
        data['form'].update(res)
        return data['form']

    def _ouput_csv(self, cr, uid, data, context):
        self._calc_dates(cr, uid, data, context)
        import csv
        import types
        result = pooler.get_pool(cr.dbname).get('financial.reports').get_result(cr, uid, data, context)
        buf = StringIO.StringIO()#		pool = pooler.get_pool(cr.dbname)

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

    def _get_defaults(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        report_obj = pool.get('financial.reports')
        company_id = pool.get('res.users').browse(cr, uid, uid).company_id.id
        config_id = report_obj.search(cr, uid, [('company_id','=',company_id)])
        account_id = config_id and  report_obj.browse(cr, uid, config_id[0]).creditor_account_id.id
        return {'account_id': account_id}

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':report_form, 'fields':report_fields, 'state':[('end','Cancel','gtk-cancel'),('csv','Excel','gtk-convert'),('print','Print','gtk-print')]}
        },
        'csv': {
            'actions': [_ouput_csv],
            'result': {'type':'form','arch':export_form,'fields':export_fields,'state':[('end','Ok')]},
        },
        'print': {
            'actions': [_calc_dates],
            'result': {'type':'print', 'report':'financial.reports_aged', 'state':'end'}
        },
    }
wizard_financial_reports_aged_creditor('financial.reports.aged.creditor')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
