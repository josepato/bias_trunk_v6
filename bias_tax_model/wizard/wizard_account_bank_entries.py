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

form = '''<?xml version="1.0"?>
<form string="Bank Entries">
        <separator string="Select Date Period" colspan="4"/>
    	<field name="date_start"/>
    	<field name="date_stop"/>
</form>'''

fields = {
    'date_start': {'string':'Start date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-07-01')},
    'date_stop': {'string':'End date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
}

class wizard_account_bank_entries(wizard.interface):

    def _check_user(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        for group in pool.get('res.users').browse(cr, uid, uid).groups_id:
            if group.name == 'Finance / Manager':
                return 'select'
        return 'select'

    def _action_open_window(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        move_obj = pool.get('account.move')
        bank_obj = pool.get('account.bank.entries')
        query = """SELECT DISTINCT(m.id) FROM account_move m LEFT JOIN account_move_line l ON (l.move_id = m.id) 
                 LEFT JOIN account_account a ON (l.account_id = a.id) 
                 LEFT JOIN account_account_type t ON (a.user_type = t.id) 
                 WHERE l.date BETWEEN '%s' AND '%s' AND t.code = 'cash' """%(data['form']['date_start'],data['form']['date_stop'])
        cr.execute(query)
        moves_id = [x[0] for x in cr.fetchall()]

        query = """SELECT bank_move_id FROM account_bank_entries
                 WHERE date IS NULL OR date BETWEEN '%s' AND '%s' """%(data['form']['date_start'],data['form']['date_stop'])
        cr.execute(query)
        writed = [x[0] for x in cr.fetchall()]
        for m in moves_id:
            move = move_obj.browse(cr, uid, m)
            if m in writed:
                value = {
                    'name': move.name,
                    'date': move.date,
                }
                bank_obj.write(cr, uid, bank_obj.search(cr, uid, [('bank_move_id','=',m)]), value)
            else:
                value = {
                    'name': move.name,
                    'date': move.date,
                    'bank_move_id': m
                }
                bank_obj.create(cr, uid, value)
                print 'create=', value

        bank_moves_id = bank_obj.search(cr, uid, [])
        domain = str(('id','in',bank_moves_id))
        return {
        'domain': "["+domain+"]",
		'name': 'Bank Entries',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'view_id': False,              
		'res_model': 'account.bank.entries',
		'type': 'ir.actions.act_window',
#		'limit': len(bank_moves_id)
    	}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_user}
        },
        'select': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel','gtk-cancel'),('open','Open','gtk-go-forward')]}
        },
        'open': {
            'actions': [],
			'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
        },
	}

wizard_account_bank_entries('wizard.account.bank.entries')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
