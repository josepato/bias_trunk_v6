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
import netsvc
import pooler
import time
from tools.translate import _
from decimal import *

#    <group attrs="{'invisible':[('currency_id','=',1)]}">
#        <field name="rate"/>
#    </group>
pay_form = '''<?xml version="1.0"?>
<form string="Payment Tool">
    <separator string="Actual Order Information" colspan="4"/>
    <field name="payment_id"/>
    <field name="lines"/>
    <field name="lines_ok"/>
    <field name="lines_error"/>
    <separator string="Payment Lines with not entry, not reconciled or partial reconcile" colspan="4"/>
    <field name="line_id" colspan="4" nolabel="1" width="700" height="400"/>
</form>'''

pay_fields = {
    'payment_id': {'string': 'Payment Order', 'type': 'many2one', 'relation':'payment.order', 'readonly':True},
    'lines': {'string': 'Order Lines', 'type':'integer', 'readonly':True},
    'lines_ok': {'string': 'Lines OK', 'type':'integer', 'readonly':True},
    'lines_error': {'string': 'Lines Partial', 'type':'integer', 'readonly':True},
    'line_id': {'string': 'Payment With Reconcile Partial', 'type': 'one2many', 'relation':'payment.line', 'readonly':False},
}

def _cancel(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    move_obj,pay_obj,line_obj = pool.get('account.move'),pool.get('payment.order'),pool.get('payment.line')
    payment = pay_obj.browse(cr, uid, data['id'], context)
    user_id = payment.mode.journal.user_id.id
    if user_id != uid:
        return {}
    move, rec_ids, part_rec_ids = [], [], []
    for pay_line in payment.line_ids:
        if pay_line.move_line_id.reconcile_partial_id:
            part_rec_ids.append(pay_line.move_line_id.reconcile_partial_id.id)
        if pay_line.move_id:
            lines = [x.id for x in pay_line.move_id.line_id]
            recs = pool.get('account.move.line').read(cr, uid, lines, ['reconcile_id',])
            recs = filter(lambda x: x['reconcile_id'], recs)
            rec_ids = rec_ids + [rec['reconcile_id'][0] for rec in recs]
            move.append(pay_line.move_id.id)    
    if rec_ids:
        rec_ids.append(0)
        sql = """select l.id as line, m.id as move from account_move_line as l, account_move as m 
	    where l.reconcile_id in %s and l.move_id = m.id"""%(tuple(rec_ids),)
        cr.execute(sql)
        result = cr.dictfetchall()
        line_ids =  map(lambda x: x['line'], result)
        move_ids =  map(lambda x: x['move'], result)
        move_ids = [x for x in set(move_ids)]
        self._trans_unrec(cr, uid, line_ids, context)
    if part_rec_ids:
        part_rec_ids.append(0)
        sql = """select l.id as line, m.id as move from account_move_line as l, account_move as m 
	    where l.reconcile_partial_id in %s and l.move_id = m.id"""%(tuple(part_rec_ids),)
        cr.execute(sql)
        result = cr.dictfetchall()
        partial_ids =  map(lambda x: x['line'], result)
        self._trans_unrec(cr, uid, partial_ids, context)
    move = [x for x in set(move)]
    for m in move_obj.browse(cr, uid, move):
        if m.state == 'posted':
            move_obj.button_cancel(cr, uid, [m.id], context)
    move_obj.unlink(cr, uid, move, context)
    pay_obj.write(cr, uid, data['id'], {'state': 'cancel'})
    pay_obj.set_to_draft(cr, uid, [data['id']], context)
    return {}



def _get_default(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    payment = pool.get('payment.order').browse(cr, uid, data['id'], context)
    if payment.state not in  ['done','open']:
        raise wizard.except_wizard(_('Error !'), _('Can use Payment Tool only in orders in state done or confirm.'))
    reg_ok, reg_error = 0, 0
    line_id = []
    for pay_line in payment.line_ids:
        if pay_line.move_line_id.reconcile_partial_id:
            reg_error += 1
            line_id.append(pay_line.id)
        elif pay_line.move_id:
            lines = [x.id for x in pay_line.move_id.line_id]
            recs1 = pool.get('account.move.line').read(cr, uid, lines, ['reconcile_id',])
            recs2 = pool.get('account.move.line').read(cr, uid, lines, ['reconcile_partial_id',])
            recs1 = filter(lambda x: x['reconcile_id'], recs1)
            recs2 = filter(lambda x: x['reconcile_partial_id'], recs2)
            rec_ids1 = [rec['reconcile_id'][0] for rec in recs1]
            rec_ids2 = [rec['reconcile_partial_id'][0] for rec in recs2]
            if rec_ids1:
                reg_ok +=1
            else:
                reg_error += 1
                line_id.append(pay_line.id)
        else:
            reg_error += 1
            line_id.append(pay_line.id)
    return {
        'payment_id': payment.id,
        'lines': len(payment.line_ids),
        'lines_ok': reg_ok,
        'lines_error': reg_error,
        'line_id': line_id,
    }

class wizard_payment_tool(wizard.interface):
    def _trans_unrec(self, cr, uid, ids, context):
        pool = pooler.get_pool(cr.dbname)
        recs1 = pool.get('account.move.line').read(cr, uid, ids, ['reconcile_id',])
        recs2 = pool.get('account.move.line').read(cr, uid, ids, ['reconcile_partial_id',])
        recs1 = filter(lambda x: x['reconcile_id'], recs1)
        recs2 = filter(lambda x: x['reconcile_partial_id'], recs2)
        rec_ids1 = [x for x in set([rec['reconcile_id'][0] for rec in recs1])]
        rec_ids2 = [x for x in set([rec['reconcile_partial_id'][0] for rec in recs2])]
        if len(rec_ids1):
            pooler.get_pool(cr.dbname).get('account.move.reconcile').unlink(cr, uid, rec_ids1)
        if len(rec_ids2):
            pooler.get_pool(cr.dbname).get('account.move.reconcile').unlink(cr, uid, rec_ids2)
        return {}

    states = {
        'init': {
            'actions': [_get_default],
            'result': {'type':'form', 'arch':pay_form, 'fields':pay_fields, 'state':[('end','Cancel'),('cancel','Cancel Order')]}
        },
        'cancel': {
            'actions': [_cancel],
            'result': {'type':'state', 'state':'end'}
        },
    }
wizard_payment_tool('account.payment.tool')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

