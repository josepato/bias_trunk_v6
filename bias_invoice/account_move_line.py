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
import netsvc
from osv import fields, osv
from tools.translate import _

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

import tools

class account_move_line(osv.osv):
    _inherit = "account.move.line"


    _columns = {
    }

    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False, context={}):
        id_set = ','.join(map(str, ids))
        
        lines = self.browse(cr, uid, ids, context=context)
        unrec_lines = filter(lambda x: not x['reconcile_id'], lines)
        credit = debit = 0.0
        currency = 0.0
        account_id = False
        partner_id = False
        for line in unrec_lines:
            if line.state <> 'valid':
                raise osv.except_osv(_('Error'),
                        _('Entry "%s" is not valid !') % line.name)
            credit += line['credit']
            debit += line['debit']
            currency += line['amount_currency'] or 0.0
            account_id = line['account_id']['id']
            partner_id = (line['partner_id'] and line['partner_id']['id']) or False
        writeoff = debit - credit
        # Ifdate_p in context => take this date
        if context.has_key('date_p') and context['date_p']:
            date=context['date_p']
        else:
            date = time.strftime('%Y-%m-%d')

        cr.execute('SELECT account_id, reconcile_id \
                FROM account_move_line \
                WHERE id IN ('+id_set+') \
                GROUP BY account_id,reconcile_id')
        r = cr.fetchall()
#TODO: move this check to a constraint in the account_move_reconcile object
        if (len(r) != 1) and not context.get('fy_closing', False):
            raise osv.except_osv(_('Error'), _('Entries are not of the same account or already reconciled ! '))
        if not unrec_lines:
            raise osv.except_osv(_('Error'), _('Entry is already reconciled'))
        account = self.pool.get('account.account').browse(cr, uid, account_id, context=context)
        if not context.get('fy_closing', False) and not account.reconcile:
            raise osv.except_osv(_('Error'), _('The account is not defined to be reconciled !'))
        if r[0][1] != None:
            raise osv.except_osv(_('Error'), _('Some entries are already reconciled !'))

        if (not self.pool.get('res.currency').is_zero(cr, uid, account.company_id.currency_id, writeoff)) or \
           (account.currency_id and (not self.pool.get('res.currency').is_zero(cr, uid, account.currency_id, currency))):
            if not writeoff_acc_id:
                raise osv.except_osv(_('Warning'), _('You have to provide an account for the write off entry !'))
            if writeoff > 0:
                debit = writeoff
                credit = 0.0
                self_credit = writeoff
                self_debit = 0.0
            else:
                debit = 0.0
                credit = -writeoff
                self_credit = 0.0
                self_debit = -writeoff

            # If comment exist in context, take it
            if 'comment' in context and context['comment']:
                label=context['comment']
            else:
                label='Write-Off'

            writeoff_lines = [
                (0, 0, {
                    'name':label,
                    'ref':label,
                    'debit':self_debit,
                    'credit':self_credit,
                    'account_id':account_id,
                    'date':date,
                    'partner_id':partner_id,
                    'currency_id': account.currency_id.id or False,
                    'amount_currency': account.currency_id.id and -currency or 0.0
                }),
                (0, 0, {
                    'name':label,
                    'ref':label,
                    'debit':debit,
                    'credit':credit,
                    'account_id':writeoff_acc_id,
                    'date':date,
                    'partner_id':partner_id
                })
            ]

            writeoff_move_id = self.pool.get('account.move').create(cr, uid, {
                'period_id': writeoff_period_id,
                'journal_id': writeoff_journal_id,

                'state': 'draft',
                'line_id': writeoff_lines
            })

            writeoff_line_ids = self.search(cr, uid, [('move_id', '=', writeoff_move_id), ('account_id', '=', account_id)])
            ids += writeoff_line_ids

        r_id = self.pool.get('account.move.reconcile').create(cr, uid, {
            #'name': date,
            'type': type,
            'line_id': map(lambda x: (4,x,False), ids),
            'line_partial_ids': map(lambda x: (3,x,False), ids)
        })
        wf_service = netsvc.LocalService("workflow")
        # the id of the move.reconcile is written in the move.line (self) by the create method above
        # because of the way the line_id are defined: (4, x, False)
        for id in ids:
            wf_service.trg_trigger(uid, 'account.move.line', id, cr)
        return r_id

account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

