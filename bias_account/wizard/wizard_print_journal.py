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

import wizard
import pooler
import time

form = '''<?xml version="1.0"?>
<form string="Print Journal">
    <separator string="Select Journals" colspan="4"/>
    <field name="journal_id" width="300" height="150" colspan="4" nolabel="1"/>
    <newline/>
    <separator string="Filters" colspan="4"/>
    <field name="state" required="True"/>
    <field name="sort_selection"/>
    <newline/>
    <group attrs="{'invisible':[('state','=','none')]}" colspan="4" height="250">
        <group attrs="{'invisible':[('state','=','byperiod')]}" colspan="4">
            <separator string="Date Filter" colspan="4"/>
            <field name="date1"/>
            <field name="date2"/>
        </group>
        <group attrs="{'invisible':[('state','=','bydate')]}" colspan="4">
            <separator string="Filter on Periods" colspan="4"/>
            <field name="period_id" width="300" height="250" colspan="4" nolabel="1"/>
        </group>
    <group attrs="{'invisible':[('state','!=','bydate')]}" colspan="4">
        <field name="text" width="250" height="400" colspan="4" nolabel="1"/>
    </group>
    </group>
</form>'''

fields = {
  'journal_id': {'string': 'Journal', 'type': 'many2many', 'relation': 'account.journal', 'required': True},
  'period_id': {'string': 'Period', 'type': 'many2many', 'relation': 'account.period', 'required': False},
  'sort_selection':{
        'string':"Entries Sorted By",
        'type':'selection',
        'selection':[('date','By date'),('ref','Reference Number')],
        'required':True,
        'default': lambda *a: 'date',
    },
    'state':{
        'string':"Date/Period Filter",
        'type':'selection',
        'selection':[('bydate','By Date'),('byperiod','By Period')],
        'default': lambda *a:'bydate'
    },
    'date1': {'string':'Start date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},#lambda *a: time.strftime('%Y-01-01')},
    'date2': {'string':'End date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'text': {'string': 'Nota', 'type': 'text', 'readonly':True},

}

def _check_data(self, cr, uid, data, *args):
    period_id = data['form']['period_id'][0][2]
    journal_id=data['form']['journal_id'][0][2]
    ids_final = []
    if data['form']['state']=='bydate':
        for journal in journal_id:
            ids_journal_period = pooler.get_pool(cr.dbname).get('account.move.line').search(cr,uid, \
                [('journal_id','=',journal),('date','>=',data['form']['date1']),('date','<=',data['form']['date2'])])
            if ids_journal_period:
                ids_final.append(ids_journal_period)
        if not ids_final:
            raise wizard.except_wizard(_('Sin datos disponibles'), _('No se encontraron registros con este filtro!'))
    elif type(period_id)==type([]):
        for journal in journal_id:
            for period in period_id:
                ids_journal_period = pooler.get_pool(cr.dbname).get('account.journal.period').search(cr,uid, \
                    [('journal_id','=',journal),('period_id','=',period)])

                if ids_journal_period:
                    ids_final.append(ids_journal_period)

            if not ids_final:
                raise wizard.except_wizard(_('Sin datos disponibles'), _('No se encontraron registros con este filtro!'))
    return data['form']

class wizard_print_journal(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', 'Cancel'), ('print', 'Print'))},
        },
        'print': {
            'actions': [_check_data],
            'result': {'type':'print', 'report':'account.journal.period.print.bias', 'state':'end'},
        },
    }
wizard_print_journal('account.print.journal.report.bias')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

