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
from datetime import datetime
from mx.DateTime import *
import wizard
import StringIO
import base64
import re

from osv import osv, fields
from tools.translate import _
from dateutil.relativedelta import relativedelta

def trunc(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    slen = len('%.*f' % (n, f))
    return str(f)[:slen]

class wizard_exchange_fluctuation(osv.osv_memory):
    _name = "wizard.exchange.fluctuation"
    _description = "Exchange Fluctuation"

    _columns = {
        'name': fields.char('Name', size=64,),
        'ref': fields.char('Reference', size=64,),
        'period_id': fields.many2one('account.period', 'Period', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'fluctuation_id': fields.many2one('exchange.fluctuation.account', 'Fluctuation'),
        'move_id': fields.many2one('account.move', 'Entry'),
        'bank_move_id': fields.many2one('account.move', 'Bank Entry'),
        'reverse_move_id': fields.many2one('account.move', 'Reverse Entry'),
        'rate': fields.float('Rate', digits=(16,4)),
        'date': fields.date('Date', readonly=False),
        'state': fields.selection( ( ('choose','choose'),   # choose parameters
                                     ('get','get'),         # get the file
                                     ('replace','replace'), # replace entry
                                 ) ),
        'file.csv': fields.binary('File (.csv Format)', readonly=True),
        'totals': fields.text('Totals'),
        'detailed_totals': fields.text('Detailed Totals'),
        'bank_totals': fields.text('Bank Totals'),
        'detailed': fields.boolean('Detailed'),
    }

    def _default_period(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['period_id']

    def _default_journal(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['journal_id']

    def _default_currency(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['currency_id']

    def _default_company(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['company_id']

    def _default_fluctuation(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['fluctuation_id']

    def _default_move(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['move_id']

    def _default_bank(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['bank_move_id']

    def _default_reverse(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['reverse_move_id']

    def _default_date(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['date']

    def _default_rate(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['rate']

    def _default_ref(self, cr, uid, context=None):
        return self._process_default(cr, uid, False)['ref']

    _defaults = {
        'name': 'FLUCTUACION CAMBIARIA',
        'ref': _default_ref,
        'period_id': _default_period,
        'journal_id': _default_journal,
        'currency_id': _default_currency,
        'company_id': _default_company,
        'fluctuation_id': _default_fluctuation,
        'move_id': _default_move,
        'bank_move_id': _default_bank,
        'reverse_move_id': _default_reverse,
        'date': _default_date,
        'rate': _default_rate,
        'state': 'choose',
    }

    def onchange_period(self, cr, uid, ids, period_id, currency_id, context={}):
        context.update({'currency_id':currency_id})
        if not period_id:
            return {'value':{'date':False, 'rate':False, 'ref':False}}
        form = self._process_default(cr, uid, period_id)
        return {'value':form}

    def _process_default(self, cr, uid, period_id, context={}):
        fluc_obj = self.pool.get('exchange.fluctuation.account')
        line_obj = self.pool.get('exchange.fluctuation.account.line')
        if not period_id:
            period_ids = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = period_ids and period_ids[0]
        company_id = fluc_obj._default_company(cr, uid, context=context)
        fluctuation_ids = fluc_obj.search(cr, uid, [('company_id','=',company_id)])
        if not fluctuation_ids:
            raise osv.except_osv(_('Error !'), _('No Exchange Fluctuation set for this company !'))
        fluctuation = fluc_obj.browse(cr, uid, fluctuation_ids[0])
        journal_id = fluctuation.journal_id.id
        currency_id = context.get('currency_id',False)
        if not currency_id:
            currency_id = fluctuation.currency_id
        company_currency = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id
        date = self.pool.get('account.period').browse(cr, uid, period_id).date_stop
        cr.execute("SELECT currency_id, rate FROM res_currency_rate WHERE currency_id = %s AND name <= %s ORDER BY name desc LIMIT 1" \
                    ,(company_currency.id, date))
        rate = 0
        if cr.rowcount:
            id, rate = cr.fetchall()[0]
        ref = 'FLUCTUACION CAMBIARIA '+self.pool.get('account.period').browse(cr, uid, period_id).code
        line_ids = line_obj.search(cr, uid, [('fluctuation_id','=',fluctuation.id), ('period_id','=',period_id)])
        move_id = reverse_move_id = line = False
        if line_ids:
            line = line_obj.browse(cr, uid, line_ids[0])
        return {'date':date, 'rate':rate, 'period_id':period_id, 'ref':ref, 'journal_id':journal_id, 'currency_id':currency_id.id, 'company_id':company_id,
                'fluctuation_id':fluctuation.id, 'move_id':line and line.move_id and line.move_id.id or False, 
                'bank_move_id':line and line.bank_move_id and line.bank_move_id.id or False, 
                'reverse_move_id':line and line.reverse_move_id and line.reverse_move_id.id or False}

    def _create_fluctuation_moves(self, cr, uid, data, context=None):
        form = data['form']
        date = (datetime.strptime(form['date'], "%Y-%m-%d") + relativedelta(days=1)).strftime('%Y-%m-%d')
        period_ids = self.pool.get('account.period').find(cr, uid, dt=date, context=context)
        period_id = period_ids and period_ids[0]
        move = {'ref': form['ref'], 'journal_id': form['journal_id'], 'period_id': form['period_id'], 'date': form['date'], 'narration': ''}
        move_id = self.pool.get('account.move').create(cr, uid, move)
        move = {'ref': 'REVERSA '+ form['ref'], 'journal_id': form['journal_id'], 'period_id': period_id, 'date': date, 'narration': ''}
        reverse_move_id = self.pool.get('account.move').create(cr, uid, move)
        move = {'ref': form['ref']+' DE BANCOS', 'journal_id':form['journal_id'], 'period_id':form['period_id'], 'date':form['date'], 'narration': ''}
        bank_move_id = self.pool.get('account.move').create(cr, uid, move)
        return move_id, reverse_move_id, bank_move_id

    def replace_entry(self, cr, uid, ids, context=None):
        form = self._get_data(cr, uid, ids, context=context)['form']
        line_obj = self.pool.get('exchange.fluctuation.account.line')
        line_ids = line_obj.search(cr, uid, [('fluctuation_id','=',form['fluctuation_id']), ('period_id','=',form['period_id'])])
        line = line_obj.read(cr, uid, line_ids, context=context)[0]
        move_ids = (line['move_id'] and [line['move_id'][0]] or []) + \
                   (line['reverse_move_id'] and [line['reverse_move_id'][0]] or []) + \
                   (line['bank_move_id'] and [line['bank_move_id'][0]] or [])
        cr.execute("SELECT id FROM account_move_line WHERE reconcile_id IS NOT NULL AND move_id IN "+str(tuple(move_ids))+" ")
        res = cr.fetchall()
        if res:
            res = map(lambda x: x[0], res)
            self.pool.get('account.move.line')._remove_move_reconcile(cr, uid, res, context=context)
            cr.execute("commit")
        self.pool.get('account.move').unlink(cr, uid, move_ids)
        self.pool.get('exchange.fluctuation.account.line').unlink(cr, uid, line_ids)
        return self.create_entry(cr, uid, ids, context=context)

    def create_entry(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        data = self._get_data(cr, uid, ids, context=context)
        form = data['form']
        date = (datetime.strptime(form['date'], "%Y-%m-%d") + relativedelta(days=1)).strftime('%Y-%m-%d')
        period_ids = self.pool.get('account.period').find(cr, uid, dt=date, context=context)
        period_id = period_ids and period_ids[0]
        totals, detailed_totals, bank_totals, to_reconcile_lines = eval(form['totals']), eval(form['detailed_totals']), eval(form['bank_totals']), []
        diff, line_reverse = False, []
        for reg in totals: diff = diff or reg['acc_diff'] and True
        if not totals or not diff: raise osv.except_osv(_('Notification !'),_('No Exchange Fluctuation for this period.'))
        debit = credit = t = 0
        move_id, reverse_move_id, bank_move_id = self._create_fluctuation_moves(cr, uid, data, context=context)
        for acc in bank_totals:
            amount = acc['acc_diff']
            if amount == 0: 
                continue
            account_id = acc['account_id']
            line = move_line_obj.create(cr, uid, {'debit': amount>0 and amount or 0.0, 'credit': amount<0 and -amount or 0.0, 'account_id': account_id,
                                                  'ref': form['ref'], 'date': form['date'], 'journal_id': form['journal_id'], 
                                                  'period_id': form['period_id'], 'name': form['ref'], 'move_id':bank_move_id, 'amount_currency':0})
        totals = form['detailed'] and detailed_totals or totals
        for acc in totals:
            amount = acc['acc_diff']
            if totals.index(acc)+1 != len(totals): 
                t += amount
            else: 
                amount = -t
            if amount == 0: 
                continue
            account_id = acc['account_id']
            line1 = move_line_obj.create(cr, uid, {'debit': amount>0 and amount or 0.0, 'credit': amount<0 and -amount or 0.0, 'account_id': account_id,
                    'ref': acc['name'] and acc['name'] or form['ref'], 'date': form['date'], 'journal_id': form['journal_id'], 
                    'period_id': form['period_id'], 'name': acc['name'] and acc['name'] or form['ref'],
                    'move_id':move_id, 'amount_currency':0, 'partner_id':acc['partner_id']})
            line2 = move_line_obj.create(cr, uid, {'debit': amount<0 and -amount or 0.0, 'credit': amount>0 and amount or 0.0, 'account_id': account_id,
                    'ref': 'REVERSA ' + (acc['name'] and acc['name'] or form['ref']), 'date': date, 'journal_id': form['journal_id'], 
                    'period_id': period_id, 'name': 'REVERSA ' + (acc['name'] and acc['name'] or form['ref']), 'move_id':reverse_move_id,
                    'amount_currency':0, 'partner_id':acc['partner_id']})
            line_reverse.append(line2)
            if self.pool.get('account.account').browse(cr, uid, account_id).reconcile:
                to_reconcile_lines.append([line1,line2])
        for rec in to_reconcile_lines:
            self.pool.get('account.move.line').reconcile(cr, uid, rec, context=context)
        move_line_obj.write(cr, uid, line_reverse, {'date':date}, context=context, update_check=False)
        self.write(cr, uid, ids, {'move_id':move_id, 'reverse_move_id':reverse_move_id, 'bank_move_id':bank_move_id}, context=context)
        self.pool.get('exchange.fluctuation.account.line').create(cr, uid, {'fluctuation_id':form['fluctuation_id'], 'move_id':move_id,
                      'reverse_move_id':reverse_move_id, 'bank_move_id':bank_move_id, 'period_id':form['period_id'], 'company_id':form['company_id'],
        }, context=context)
        return self.action_open_window(cr, uid, ids, context=context)

    def action_open_window(self, cr, uid, ids, context=None):
        form = self._get_data(cr, uid, ids, context=context)['form']
        move_ids = [form['move_id'], form['reverse_move_id'], form['bank_move_id']]
        return {
            'domain': "[('id','in',%s)]" % (move_ids,),
            'name': _('Fluctuation Entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window'
        }

    def _get_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, context=context)[0]
        return data

    def ouput_csv(self, cr, uid, ids, context=None):
        import csv
        import types
        data = self._get_data(cr, uid, ids, context=context)
        result = self.pool.get('exchange.fluctuation').get_result(cr, uid, data, context)
        buf = StringIO.StringIO()
        this = self.browse(cr, uid, ids)[0]
        for val in result['result']:
            row = []
            csvval = ''
            for d in val:
                if type(d).__name__ == 'unicode':
                    d = d.encode('utf-8')
                if type(d)==types.StringType:
                    csvval += (csvval and ',' or '') + '"' + str(d.replace('\n',' ').replace('\t',' ')) + '"'
                else:
                    csvval += (csvval and ',' or '') + str(d)
            buf.write(csvval+'\n')
        out=base64.encodestring(buf.getvalue())
        buf.close()
        self.write(cr, uid, ids, {
                'state':data['form']['move_id'] and 'replace' or 'get', 
                'file.csv':out, 
                'name':this.name, 
                'totals':str(result['totals']),
                'detailed_totals':str(result['detailed_totals']),
                'bank_totals':str(result['bank_totals'])}, context=context)
        return True

    def check_report(self, cr, uid, ids, context=None):
        data = self._get_data(cr, uid, ids, context=context)
        return self._print_report(cr, uid, ids, data, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.exchange.fluctuation',
            'datas': data
        }

wizard_exchange_fluctuation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
