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

def _get_selection(self,cr, uid, ctx):
        res = []
        report_obj = pooler.get_pool(cr.dbname).get('account.custom.report')
        report_ids = report_obj.search(cr, uid, [])
        for report in report_obj.browse(cr, uid, report_ids):
            if not report.user_ids or uid in eval(report.user_ids):
                res.append((report.id,report.name))
        return res
#<field name="null" nolabel="1" readonly="1" colspan="2"/> || ('result_selection','in',('cash','aged')),
#        <group  colspan="4" attrs="{ 'invisible':[('state','=','none')] }">
#        <group  colspan="4" attrs="{ 'invisible':[('result_selection','!=','aged')] }">

report_form = '''<?xml version="1.0"?>
<form string="Custom Report">
    <group colspan="4" col="4" >
        <separator string="Select Custom Report" colspan="4"/>
    	<field name="report_id" on_change="onchange_report(report_id)" colspan="2"/>
        <group colspan="2" attrs="{ 'invisible':[('result_selection','=','aged')] }">
        <group  colspan="4" attrs="{ 'invisible':[('state','=','none')] }">
            <field name="group_by" />
        </group>
        </group>
    </group>
    <group attrs="{'invisible':[('state','=','none')]}" colspan="4">
        <field name="account_id"/>
            <field name="cost_center_id" />
        <field name="report_zero"/>
        <group  colspan="4" attrs="{ 'invisible':[('result_selection','!=','aged')] }">
            <field name="currency"/>
            <field name="partner_type"/>
        </group>
        <separator string="Partners" colspan="4"/>
            <separator string="Partner Selection" colspan="2"/>
            <separator string="Partner Category Selection" colspan="2"/>
	        <field name="partner_ids" height="150" colspan="2" nolabel="1" />
	        <field name="category_ids" height="150" colspan="2" nolabel="1" />
        <newline/>
    </group>
    <group attrs="{'invisible':[('state','!=','none')]}" colspan="4">
        <field name="text1" width="350" height="500" colspan="2" nolabel="1"/>
        <field name="text2" width="350" height="500" colspan="2" nolabel="1"/>
    </group>
    <group attrs="{'invisible':[('state','=','none')]}" colspan="4">
        <group attrs="{'invisible':[('state','=','none')]}" colspan="4"  height="250">
            <group attrs="{'invisible':[('state','=','byperiod')]}" colspan="4">
                <separator string="Date Filter" colspan="4"/>
                    <group attrs="{ 'invisible':[('result_selection','=','aged')] }">
                        <field name="date1"/>
                    </group>
                    <field name="date2"/>
                    <group attrs="{ 'invisible':[('result_selection','=','aged')] }" colspan="4">
                        <field name="fiscalyear"/>
                        <label string="(Keep empty for all open fiscal years)" align="0.0"/>
                    </group>
            </group>
        </group>
    </group>
</form>'''

report_fields = {
    'stage':{'string':"Stage",'type':'boolean'},
    'report_id': {'string':'Report Name', 'type':'selection', 'selection': _get_selection}, 
    'null': {'string': 'Null', 'type': 'char'},
    'date1': {'string':'Start date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
    'date2': {'string':'End date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'periods_ids': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period', 'help': 'All periods if empty','states':{'none':[('readonly',True)],'bydate':[('readonly',True)]}},
    'state':{
        'string':"Date/Period Filter",
        'type':'selection',
        'selection':[('bydate','By Date'),('none','No Filter')],
        'default': lambda *a:'none'
    },
    'fiscalyear': {'string':"Fiscal year",'type':'boolean'},
    'group_by':{
        'string':"Group By",
        'type':'selection',
        'selection':[('partner','Partner'),('account','Account')],
        'required':False
    },
    'result_selection':{
        'string':"Select",
        'type':'selection',
        'selection':[
                ('account','Account'),
                ('aged','Aged Trial Balance'),
                ('customer','Receivable Accounts'),
                ('supplier','Payable Accounts'),
                ('all','Receivable and Payable Accounts'),
                ('cash','Bank')],
        'required':True
    },
    'report_zero':{
        'string':"Report Zeros",
        'type':'selection',
        'selection':[('zero','Yes'),('no_zero','Not')],
        'required': False,
        'default': lambda *a: 'zero',
    },
    'currency':{
        'string':"Currency",
        'type':'selection',
        'selection':[('mn','PESOS'),('usd','DOLARES')],
        'required': False,
        'default': lambda *a: 'mn',
    },
    'partner_type':{
        'string':"Partner Type",
        'type':'selection',
        'selection':[('customer','Customer'),('supplier','Supplier'),('none','None')],
        'required': False,
        'default': lambda *a: 'none',
    },
    'text1': {'string': 'Nota', 'type': 'text', 'readonly':True},
    'text2': {'string': 'Nota', 'type': 'text', 'readonly':True},
	'partner_ids': {'string': 'Partners', 'type': 'many2many', 'relation': 'res.partner', 'required': False, 'help': 'Keep empty for all partners'},
    'account_id': {'string': 'Account', 'type': 'many2one', 'relation': 'account.account', 'help': 'This account and childs'},
    'cost_center_id': {'string': 'Cost Center', 'type': 'many2one', 'relation': 'cost.center', 'help': 'Keep empty for all cost centers'},
    'category_ids': {'string': 'Categoria', 'type': 'many2many', 'relation': 'res.partner.category'},
    'balance':{'string':"Only balances",'type':'boolean'},
}
#    'fiscalyear': {
#        'string':'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
#        'help': 'Keep empty for all open fiscal year',
#    },

new_form = '''<?xml version="1.0"?>
<form string="Select Parameters">
        <field name="name" colspan="4"/>
        <newline/>  
        <field name="result_selection"/>
        <field name="company_id"/>
    <newline/>  
    <group colspan="4" col="4" >
        <group attrs="{ 'invisible':[('result_selection','!=','aged')] }">
            <field name="period_length"/>
        </group>
        <group attrs="{ 'invisible':[('result_selection','!=','aged')] }">
            <field name="direction_selection"/>
        </group>
    </group>

    <group colspan="4" attrs="{ 'invisible':[('result_selection','in',('customer','supplier','all','cash'))] }">
    <field domain="[('type','in',((result_selection == 'aged' and ('payable','receivable','view')) or ('payable','receivable','view','consolidation','other','closed')))]" name="account_id" attrs="{'readonly':[('result_selection','not in',('account','aged'))], 'required':[('result_selection','in',('account','aged'))]}"/>
    <label colspan="2" string="(This account and childs)" align="0.0"/>/>
    </group>
    <field name="reconcil"/>
    <field name="payment"/>
    <newline/>
    <field name="page_split"/>
    <field name="balance"/>
    <newline/>
    <field name="journal_type"/>
    <field name="state" required="True"/>
    <separator string="Select Report Users" colspan="4"/>
    <field name="user_ids" height="150" colspan="4" nolabel="1"/>
    <group attrs="{'invisible':[('state','!=','none')]}" colspan="4">
        <field name="text" width="500" height="100" colspan="4" nolabel="1"/>
    </group>

</form>'''
#    <group attrs="{ 'invisible':[('result_selection','!=','aged')] }">
#        <field name="date" />
#    </group>
new_fields = {
    'company_id': {'string': 'Company', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'account_id': {'string': 'Account', 'type': 'many2one', 'relation': 'account.account', 'required': False},
    'user_ids': {'string': 'Users', 'type': 'many2many', 'relation': 'res.users', 'required': False},
    'result_selection':{
        'string':"Select",
        'type':'selection',
        'selection':[
                ('account','Account'),
                ('aged','Aged Trial Balance'),
                ('customer','Receivable Accounts'),
                ('supplier','Payable Accounts'),
                ('all','Receivable and Payable Accounts'),
                ('cash','Bank')],
        'required':True
    },
    'reconcil':{
        'string':"Entries to Include",
        'type':'selection',
        'selection':[
                ('all','All Entries'),
                ('unreconcile_today','Up Today Unreconciled'),
                ('unreconcile_inrange','In Range Unreconciled'),
                ('reconcile_inrange','In Range Reconciled')],
        'required':True,
        'default': lambda *a: 'all',
    },
    'payment':{
        'string':"Payment Order",
        'type':'selection',
        'selection':[
                ('all','All Entries'),
                ('exclude','Exclude Payment Order Entries'),
                ('only','Only Payment Order Entries'),
                ],
        'required':True,
        'default': lambda *a: 'all',
    },
    'journal_type':{
        'string':"Select Journal Type",
        'type':'selection',
        'selection':[
                ('all','All Journals'),
                ('sale','Sale Journals'),
                ('purchase','Purchase Journals'),
                ('cash','Only Cash Journals'),
                ('no_cash','Witout Cash Journals')],
        'required':True
    },
    'direction_selection':{
        'string':"Analysis Direction",
        'type':'selection',
        'selection':[('past','Past'),('future','Future')],
        'required':False,
        'default': lambda *a: 'past',
    },
    'state':{
        'string':"Date/Period Filter",
        'type':'selection',
        'selection':[('bydate','By Date'),('none','No Filter')],
        'default': lambda *a:'bydate'
    },
    'balance':{'string':"Only balances",'type':'boolean'},
    'page_split':{'string':"One Partner Per Page",'type':'boolean'},
    'period_length': {'string': 'Period length (days)', 'type': 'integer', 'required': False, 'default': lambda *a:30},
    'text': {'string': 'Nota', 'type': 'text', 'readonly':True},
    'name': {'string': 'Report Name', 'type': 'char', 'size': 128},
}
#    'date':{'string':"Date", 'type':'date', 'default': lambda *a: time.strftime('%Y-%m-%d')},

account_form = '''<?xml version="1.0"?>
<form string="Select Action">
        <separator string="Selected Account" colspan="4"/>
        <field name="acc_count"/>
        <field name="account_ids" height="250" colspan="4" nolabel="1"/>
</form>'''

account_fields = {
    'account_ids': {'string': 'Accounts', 'type': 'many2many', 'relation': 'account.account', 'required': True},
    'acc_count':{'string':"Number of Accounts",'type':'integer'},
}

export_form = '''<?xml version="1.0"?>
<form string="Export Report">
        <separator string="File" colspan="4"/>
    	<field name="file.csv"/>
</form>'''

export_fields = {
	'file.csv': {'string': 'File.csv', 'type': 'binary', 'help': 'File created for this report', 'readonly':True},

}
#                ('reconcile_today','Up Today Reconciled'),

class wizard_account_custom_report(wizard.interface):

    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        periods_obj=pooler.get_pool(cr.dbname).get('account.period')
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        else:
            company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
#        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        data['form']['result_selection'] = 'all'
        data['form']['result_selection'] = 'account'
        data['form']['journal_type'] = 'all'
        data['form']['group_by'] = 'account'
        data['form']['reconcil'] = 'all'
        return data['form']

    def _get_report_data(self, cr, uid, data, context):
        if data['form']['stage'] == False:
            data['form']['stage'] = True
        else:
            return data['form']
        if data['form']['report_id']:
            report = pooler.get_pool(cr.dbname).get('account.custom.report').browse(cr, uid, data['form']['report_id'])
            user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
            if user.company_id:
                company_id = user.company_id.id
            else:
                company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
            data['form']['company_id'] = company_id
            data['form']['result_selection'] = report.result_selection
            data['form']['page_split'] = report.page_split
            data['form']['balance'] = report.balance
            data['form']['journal_type'] = report.journal_type
            data['form']['group_by'] = report.group_by
            data['form']['state'] = 'bydate'#report.state
            data['form']['account_ids'] = eval(report.account_ids)
            data['form']['category_ids'] = report.category_ids and eval(report.category_ids)
            data['form']['user_ids'] = report.user_ids and eval(report.user_ids)
            data['form']['account_id'] = data['form']['account_id']#report.account_id
            data['form']['period_length'] = report.period_length
            data['form']['reconcil'] = report.reconcil
            data['form']['payment'] = report.payment
            data['form']['direction_selection'] = report.direction_selection
            data['form']['name'] = report.name
            data['form']['cost_center_id'] = report.cost_center_id
            data['form']['currency'] = report.currency,
            data['form']['partner_type'] = report.partner_type,
        else:
            data['form']['user_ids'] = [uid]
        return data['form']

    def _save(self, cr, uid, data, context):
        report_obj = pooler.get_pool(cr.dbname).get('account.custom.report')
        if data['form']['category_ids'] and type(data['form']['category_ids'][0]).__name__ == 'tuple':
            data['form']['category_ids'] = data['form']['category_ids'][0][2]
        values = {
        'result_selection': data['form']['result_selection'],
        'page_split': data['form']['page_split'],
        'balance': data['form']['balance'],
        'result_selection': data['form']['result_selection'],
        'journal_type': data['form']['journal_type'],
        'group_by': data['form']['group_by'],
        'state': 'bydate',#data['form']['state'],
        'account_ids': str(data['form']['account_ids'][0][2]),
        'user_ids': str(data['form']['user_ids'][0][2]),
        'category_ids': str(data['form']['category_ids']),
        'account_id': data['form']['account_id'],
        'period_length': data['form']['period_length'],
        'reconcil': data['form']['reconcil'],
        'payment': data['form']['payment'],
        'direction_selection': data['form']['direction_selection'],
        'partner_ids': data['form']['partner_ids'][0][2],
        'periods_ids': data['form']['periods_ids'][0][2],
        'date1': data['form']['date1'],
        'date2': data['form']['date2'],
        'state': data['form']['state'],
        'report_zero': data['form']['report_zero'],
        'fiscalyear': data['form']['fiscalyear'],
        'name': data['form']['name'],
        'currency': data['form']['currency'],
        'partner_type': data['form']['partner_type'],
        }
        if data['form']['report_id']:
            report_obj.write(cr, uid, data['form']['report_id'], values)
        else:
            report_obj.create(cr, uid, values)
        return 'account'

    def _save_periods(self, cr, uid, data, context):
        if data['form']['report_id']:
            report_obj = pooler.get_pool(cr.dbname).get('account.custom.report')
            values = {
            'partner_ids': data['form']['partner_ids'][0][2],
            'periods_ids': data['form']['periods_ids'][0][2],
            'category_ids': data['form']['category_ids'] and data['form']['category_ids'][0][2],
            'date1': data['form']['date1'],
            'date2': data['form']['date2'],
#            'state': data['form']['state'],
            'fiscalyear': data['form']['fiscalyear'],
            'account_id': data['form']['account_id'],
            'cost_center_id': data['form']['cost_center_id'],
            'group_by': data['form']['group_by'],
            'report_zero': data['form']['report_zero'],
            'currency': data['form']['currency'],
            'partner_type': data['form']['partner_type'],
            }
            report_obj.write(cr, uid, data['form']['report_id'], values)
        return 'account'

    def _delete(self, cr, uid, data, context):
        report_obj = pooler.get_pool(cr.dbname).get('account.custom.report')
        if data['form']['report_id']:
            report_obj.unlink(cr, uid, [data['form']['report_id']])
        return 'account'

    def _calc_dates(self, cr, uid, data, context):
        res = {}
        period_length = data['form']['period_length']
        if period_length<=0:
            raise wizard.except_wizard(_('UserError'), _('You must enter a period length that cannot be 0 or below !'))
        start = datetime.date.fromtimestamp(time.mktime(time.strptime(data['form']['date1'],"%Y-%m-%d")))
        start = DateTime(int(start.year),int(start.month),int(start.day))
        if data['form']['direction_selection'] == 'past':
            for i in range(3)[::-1]:
                stop = start - RelativeDateTime(days=period_length)
                res[str(i)] = {
                    'name' : str((3-(i+1))*period_length) + '-' + str((3-i)*period_length),
                    'name_stop' : str((3-i)*period_length),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start' : stop.strftime('%Y-%m-%d'),
                    }
                start = stop - RelativeDateTime(days=1)
        else:
            for i in range(3):
                stop = start + RelativeDateTime(days=period_length)
                res[str(3-(i+1))] = {
                    'name' : str((i)*period_length)+'-'+str((i+1)*period_length),
                    'name_stop' : str((i+1)*period_length),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop' : stop.strftime('%Y-%m-%d'),
                    }
                start = stop + RelativeDateTime(days=1)
        return res

    def _get_accounts(self, cr, uid, data, context):
        acc_obj = pooler.get_pool(cr.dbname).get('account.account')
        company_id = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid).company_id.id
        if data['form']['result_selection'] == 'aged':
            res = self._calc_dates(cr, uid, data, context)
            data['form'].update(res)
        elif data['form']['result_selection'] == 'cash':
            query = ("Select a.id, a.code from account_account a, account_account_type t " \
                	"where a.user_type = t.id and t.code ='cash' and a.reconcile = True order by code")
            cr.execute(query)
            account = [x[0] for x in cr.fetchall()]
        if data['form']['account_id']:
            account = acc_obj._get_children_and_consol(cr, uid, [data['form']['account_id']])
        elif data['form']['result_selection'] == 'supplier':
    	    account = acc_obj.search(cr, uid, [('type','=','payable'),('active','=',True),('company_id','=',company_id)]) 
        elif data['form']['result_selection'] == 'customer':
    		account = acc_obj.search(cr, uid, [('type','=','receivable'),('active','=',True),('company_id','=',company_id)]) 
        elif data['form']['result_selection'] == 'all':
    		account = acc_obj.search(cr, uid, [('type','in',('payable','receivable')),('active','=',True),('company_id','=',company_id)]) 
        data['form']['account_ids'] = account
        data['form']['acc_count'] = len(account)
        return data['form']

    def _action_open_window(self, cr, uid, data, context):
        result = pooler.get_pool(cr.dbname).get('account.custom.report').get_id_to_open(cr, uid, data, context)

        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')
        res = mod_obj._get_id(cr, uid, 'account', 'action_move_line_select')
        id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
        res = act_obj.read(cr, uid, [id])[0]
        res['domain'] = str([('id','in',eval(result))])
        return res
        
        return {
        'domain': "[('id','in',"+result+")]",
        'name': _('Account Lines'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'view_id': False,
        'res_model': 'account.move.line',
        'type': 'ir.actions.act_window'}

    def _ouput_csv(self, cr, uid, data, context):
        import csv
        import types
        result = pooler.get_pool(cr.dbname).get('account.custom.report').get_result(cr, uid, data, context)
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

    def _correct_data_form(self, cr, uid, data, context):
        if data['form']['report_id']:
            self._save_periods(cr, uid, data, context)
            data['form'] = self._get_report_data(cr, uid, data, context)
            data['form'] = self._get_accounts(cr, uid, data, context)
        if data['form']['result_selection'] == 'cash':
           data['form']['group_by'] = 'account'
        elif data['form']['result_selection'] == 'aged':
            data['form']['group_by'] = 'partner'
        return data['form']

    def _check(self, cr, uid, data, context):
        data['form'] = self._correct_data_form(cr, uid, data, context)
        if data['form']['stage'] == False:
            return 'new'
        if data['form']['result_selection'] == 'aged':
            return 'report_aged'
        elif data['form']['page_split']:
            return 'report_split'           
        elif data['form']['balance']:
            return 'report_balance'
        else:
            return 'report_other'

    def _check_open(self, cr, uid, data, context):
        data['form'] = self._correct_data_form(cr, uid, data, context)
        if data['form']['stage'] == False:
            return 'new'
        return 'open'

    def _check_csv(self, cr, uid, data, context):
        data['form'] = self._correct_data_form(cr, uid, data, context)
        if data['form']['result_selection'] == 'aged':
            data['form']['date1'] = data['form']['date2']
        if data['form']['stage'] == False:
            return 'new'
        return 'report_csv'

    def _check_state(self, cr, uid, data, context):
        if data['form']['result_selection'] == 'cash':
            data['form']['group_by'] = 'account'
        elif data['form']['result_selection'] == 'aged':
            data['form']['group_by'] = 'partner'
            data['form']['date1'] = data['form']['date2']
        if data['form']['state'] in ('bydate','all'):
           data['form']['fiscalyear'] = False
        else :
#           data['form']['fiscalyear'] = True
           self._check_date(cr, uid, data, context)
#        acc_id = pooler.get_pool(cr.dbname).get('account.invoice').search(cr, uid, [('state','=','open')])
#        if not acc_id:
#            raise wizard.except_wizard(_('No Data Available'), _('No records found for your selection!'))
        return data['form']

    def _check_date(self, cr, uid, data, context):
        sql = """
            SELECT f.id, f.date_start, f.date_stop FROM account_fiscalyear f  Where '%s' between f.date_start and f.date_stop """%(data['form']['date1'])
        cr.execute(sql)
        res = cr.dictfetchall()
        if res:
            if (data['form']['date2'] > res[0]['date_stop'] or data['form']['date2'] < res[0]['date_start']):
                raise  wizard.except_wizard(_('UserError'),_('Date to must be set between %s and %s') % (str(res[0]['date_start']) , str(res[0]['date_stop'])))
            else:
                return 'report'
        else:
            raise wizard.except_wizard(_('UserError'),_('Date not in a defined fiscal year'))

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':report_form, 'fields':report_fields, 'state':[('end','Cancel','gtk-cancel'),('new','New/Edit','gtk-go-forward'),('checkopen','Display'),('checkcsv','Excel','gtk-convert'),('checkreport','Print','gtk-print')]}
        },
        'new': {
            'actions': [_get_report_data],
            'result': {'type':'form', 'arch':new_form, 'fields':new_fields, 'state':[('end','Cancel','gtk-cancel'),('account','Next','gtk-go-forward')]}
        },
        'save': {
            'actions': [],
            'result': {'type': 'action', 'action':_save, 'state':'end'}
        },
        'delete': {
            'actions': [],
            'result': {'type': 'action', 'action':_delete, 'state':'end'}
        },
        'account': {
            'actions': [_get_accounts],
            'result': {'type':'form', 'arch':account_form, 'fields':account_fields, 'state':[('end','Cancel','gtk-cancel'),('delete','Delete'),('save','Save'),('checkopen','Display'),('checkcsv','Excel','gtk-convert'),('checkreport','Print','gtk-print')]}
        },
        'checkopen': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_open}
        },
        'checkcsv': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_csv}
        },
        'checkreport': {
            'actions': [],
            'result': {'type':'choice','next_state':_check}
        },
        'open': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
        },
        'report_csv': {
            'actions': [_ouput_csv],
            'result': {'type':'form','arch':export_form,'fields':export_fields,'state':[('end','Ok')]},
        },
        'report_split': {
            'actions': [_check_state],
            'result': {'type':'print', 'report':'account.custom_report_split', 'state':'end'}
        },
        'report_aged': {
            'actions': [_check_state],
            'result': {'type':'print', 'report':'account.custom_report_aged', 'state':'end'}
        },
        'report_other': {
            'actions': [_check_state],
            'result': {'type':'print', 'report':'account.custom_report_other', 'state':'end'}
        },
        'report_balance': {
            'actions': [_check_state],
            'result': {'type':'print', 'report':'account.custom_report_balance', 'state':'end'}
        }

    }
wizard_account_custom_report('account.custom.report')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
