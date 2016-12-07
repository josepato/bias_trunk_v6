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
#
#
from osv import osv
from osv import fields
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

def trunc(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    slen = len('%.*f' % (n, f))
    return str(f)[:slen]

#----------------------------------------------------------
# Exchange Fluctuation
#----------------------------------------------------------

class exchange_fluctuation(osv.osv):
    _name = "exchange.fluctuation"
    _description = "Exchange Fluctuation"

    ###############################################################
    #   Methods for Wizard Exchange Fluctuation
    ###############################################################
    def _get_company(self, cr, uid, form):
        return self.pool.get('res.users').browse(cr, uid, uid).company_id.name

    def _get_title(self, cr, uid, form):
        res = form['name'] + ' [' + self.pool.get('res.currency').browse(cr, uid, form['currency_id']).name + ']'
        return res

    def _get_date(self, cr, uid, form):
        stop = time.strftime('%d-%b-%Y', time.strptime(form['date'],'%Y-%m-%d'))
        res = 'Al ' + str(stop), 'TASA: ' + str('%.4f' % form['rate']) 
        return res

    def _date_sp(self, cr, uid, date):
		return str(time.strftime('%d-%m-%Y', time.strptime(date,'%Y-%m-%d')))

    def _get_amount(self, cr, uid, acc, date, bank_move_id):
        query = "SELECT SUM(amount_currency) AS amount_currency, SUM(debit-credit) AS balance FROM account_move_line " \
                "WHERE account_id = %s  AND state='valid' AND move_id != %s AND date <= '%s'"%(acc, bank_move_id or 0, date)
        cr.execute(query)
        res = cr.dictfetchone()
        return res or []

    def _get_bank_account_ids(self, cr, uid, currency_id, date, context={}):
        query = "SELECT a.id, a.code, a.type FROM account_move m LEFT JOIN account_move_line l ON (m.id = l.move_id) " \
                "LEFT JOIN account_account a ON (l.account_id = a.id)  " \
                "WHERE a.currency_id = %s AND l.state='valid' AND l.date <= '%s'  " \
                "AND a.type IN ('liquidity') AND a.active = True GROUP BY a.id, a.code, a.type ORDER BY a.code "%(currency_id, date)
        cr.execute(query)
        return cr.dictfetchall()

    def _get_account_ids(self, cr, uid, currency_id, date, context={}):
        query = "SELECT a.id, a.code, a.type FROM account_move m LEFT JOIN account_move_line l ON (m.id = l.move_id) " \
                "LEFT JOIN account_account a ON (l.account_id = a.id) LEFT JOIN account_journal j ON (l.journal_id = j.id) " \
                "WHERE a.currency_id = %s AND l.state='valid' AND l.date <= '%s'  " \
                "AND j.type IN ('sale','sale_refund','purchase','purchase_refund','situation') AND a.active = True " \
                "GROUP BY a.id, a.code, a.type ORDER BY a.code "%(currency_id, date)
        cr.execute(query)
        return cr.dictfetchall()

    def _get_lines_ids(self, cr, uid, data, acc, move_id, reverse_move_id, context={}):
        form = data['form']
        invoice = "(SELECT id FROM account_invoice WHERE move_id=m.id)"
        line_name = "('**[ID'||l.id::varchar||','||CASE WHEN l.ref IS NOT NULL THEN l.ref ELSE '**' END||'] '||l.name)"
        reconcile = "(l.reconcile_id IS NULL OR (SELECT r.create_date FROM account_move_reconcile r WHERE id = l.reconcile_id) < '"+form['date']+"' )"
        invoice_name = "(SELECT CASE WHEN type = 'out_invoice' THEN 'FACC'||' '||number " \
                    	    "WHEN type = 'out_refund' THEN 'NCRE'||' '||number " \
                    	    "WHEN type = 'in_invoice' THEN 'FACP'||' '||reference " \
                    	    "ELSE 'NCAR'||' '||reference END " \
                    	    "FROM account_invoice WHERE id="+invoice+") "

        query = "SELECT l.date,	" \
                    "CASE WHEN "+invoice+" IS NULL THEN "+line_name+" ELSE "+invoice_name+" END AS name, " \
                    "((l.debit-l.credit) / l.amount_currency)::NUMERIC(14,4) AS rate, " \
                    "l.amount_currency, " \
                    "l.id, " \
                    "l.partner_id " \
                	"FROM account_move m LEFT JOIN account_move_line l ON (l.move_id = m.id) " \
                	"LEFT JOIN account_journal j ON (l.journal_id = j.id) " \
	                "WHERE "+reconcile+" AND l.account_id = %s AND l.date <= '%s' AND l.state = 'valid' " \
                    "AND j.type IN ('sale','sale_refund','purchase','purchase_refund','situation') AND l.move_id NOT IN (%s, %s) " \
	                "AND (l.amount_currency IS NOT NULL AND l.amount_currency != 0) ORDER BY l.date "%(acc['id'], form['date'], move_id or 0, \
                    reverse_move_id or 0)
        cr.execute(query)
        return cr.dictfetchall()

    def get_function(self, cr, uid, data, context={}):
        cur_obj = self.pool.get('res.currency')
        form = data['form']
        fluctuation = self.pool.get('exchange.fluctuation.account').browse(cr, uid, form['fluctuation_id'])
        company_currency = fluctuation.company_id.currency_id
        currency = cur_obj.browse(cr, uid, form['currency_id'])
        res, temp, totals, detailed_totals, bank_totals = [], [], [], [], []
        total_history , total_current, total_diff, bank_total_diff = 0, 0, 0, 0
        bank_account_ids = self._get_bank_account_ids(cr, uid, currency.id, form['date'], context=context)
        account_ids = self._get_account_ids(cr, uid, currency.id, form['date'], context=context)
        if not account_ids and not bank_account_ids:
            return {'result':res, 'totals':totals, 'bank_totals':bank_totals}
        date = (datetime.strptime(form['date'], "%Y-%m-%d") - relativedelta(months=+1)).strftime('%Y-%m-%d')
        rate = cur_obj.browse(cr, uid, company_currency.id, context={'date':date}).rate
        for acc in bank_account_ids: # acc= {'code': u'1-1-02-102', 'type': u'liquidity', 'id': 139}
            result = self._get_amount(cr, uid, acc['id'], form['date'], form['bank_move_id'])
            if not result['amount_currency']:
                continue
            amount_mn = cur_obj.compute(cr, uid, currency.id, company_currency.id, result['amount_currency'], context={'date':form['date']})
            acc_diff = float(trunc(amount_mn - result['balance'],2))
            bank_totals.append({'account_id': acc['id'], 'acc_diff':acc_diff})
            bank_total_diff += acc_diff
            temp.append({'date':'', 'acc':'CUENTA: '+acc['code'], 'amount_currency':result['amount_currency'], 'history':result['balance'], 
                         'current':amount_mn, 'rate':'', 'residual':'', 'diff':acc_diff, 'partner_id':''})
        account_id = bank_total_diff > 0 and fluctuation.gain_fluc_acc.id or fluctuation.loss_fluc_acc.id
        bank_totals.append({'account_id': account_id, 'acc_diff':-bank_total_diff})
        if temp:
            res.append({'date':'BANCOS', 'acc':'', 'amount_currency':'', 'history':'', 'current':'', 'rate':'', 'residual':'', 'diff':'',
                        'partner_id':''})
            res.append({'date':'', 'acc':'', 'amount_currency':'MONEDA EXT', 'history':'CONTABLE', 'current':'ACTUAL', 'rate':'',
                        'residual':'', 'diff':'DIFERENCIA', 'partner_id':''})
            res = res + temp       
        temp = []     
        for acc in account_ids: # acc= {'code': u'1-1-10-002', 'type': u'purchase', 'id': 26}
            acc_total_history = acc_total_current = acc_diff = 0
            acc_temp = []
            lines_ids = self._get_lines_ids(cr, uid, data, acc, form['move_id'], form['reverse_move_id'], context=context)
            for l in lines_ids:
                residual = self.pool.get('account.move.line').browse(cr, uid, l['id']).amount_residual_currency
                if not residual: continue
                current = residual * form['rate']
                history = residual * l['rate']
                diff = float(trunc(acc['type'] == 'receivable' and (current-history) or (history-current),2))
                partner_code = self.pool.get('res.partner').read(cr, uid, [l['partner_id']], ['name'])
                partner_code = partner_code  and partner_code[0].get('name','')
                acc_temp.append({'date':l['date'], 'acc':l['name'], 'amount_currency':abs(l['amount_currency']), 'history':history, 
                            'current':current, 'rate':l['rate'], 'residual':residual, 'diff':diff, 'partner_id':partner_code})
                acc_total_history += history
                acc_total_current += current
                acc_diff += diff
                detailed_totals.append({'partner_id':l['partner_id'], 'name':l['name'], 'account_id': acc['id'], 'acc_diff':diff})
            if acc_temp:
                temp.append({'date':'','acc':'CUENTA: '+acc['code'], 'amount_currency':'', 'history':'', 'current':'', 'rate':'', 'residual':'', \
                             'diff':'', 'partner_id':''})
                temp.append({'date':'FECHA', 'acc':'REFERENCIA', 'amount_currency':'DOCUMENTO', 'history':'HISTORICO', 
                            'current':'ACTUAL', 'rate':'TAZA', 'residual':'PENDIENTE', 'diff':'DIFERENCIA', 'partner_id':'EMPRESA'})
                temp = temp + acc_temp
                temp.append({'date':'', 'acc':'', 'amount_currency':'', 'history':acc_total_history, 'current':acc_total_current, 'rate':'SUBTOTAL',
                            'residual':'', 'diff':acc_diff, 'partner_id':''})
                totals.append({'partner_id':'', 'name':False, 'account_id': acc['id'], 'acc_diff':acc_diff})
                total_history += acc_total_history
                total_current += acc_total_current
                total_diff += acc_diff
        if temp:
            res.append({'date':'','acc':'', 'amount_currency':'', 'history':'', 'current':'', 'rate':'', 'residual':'', 'diff':'', 'partner_id':''})
            res.append({'date':'CLIENTES Y PROVEEDORES','acc':'', 'amount_currency':'', 'history':'', 'current':'', 'rate':'', 'residual':'',
                        'diff':'', 'partner_id':''})
            res = res + temp            

        account_id = total_diff > 0 and fluctuation.gain_fluc_acc.id or fluctuation.loss_fluc_acc.id
#        total_diff = float(trunc(total_diff,2))
        totals.append({'partner_id':'', 'name':False, 'account_id': account_id, 'acc_diff':-total_diff})
        detailed_totals.append({'partner_id':'', 'name':False, 'account_id': account_id, 'acc_diff':-total_diff})
        res.append({'date':'','acc':'', 'amount_currency':'', 'history':'', 'current':'', 'rate':'', 'residual':'', 'diff':'', 'partner_id':''})
        res.append({'date':'', 'acc':'', 'amount_currency':'', 'history':total_history, 'current':total_current, 'rate':'TOTAL', 'residual':'',
                    'diff':total_diff, 'partner_id':''})
        return {'result':res, 'totals':totals, 'detailed_totals':detailed_totals, 'bank_totals':bank_totals}

    def get_result(self, cr, uid, data, context={}):
        form = data['form']
        result = []
        result += [(self._get_company(cr, uid, form),)]
        result += [(self._get_title(cr, uid, form),)]
        result += [self._get_date(cr, uid, form)]
        values = self.get_function(cr, uid, data, context=context)
        for l in values['result']:
            result += [(l['date'], l['acc'], l['partner_id'], l['amount_currency'], l['residual'], l['rate'], l['history'], l['current'], l['diff'])]
        return {'result':result, 'totals':values['totals'], 'detailed_totals':values['detailed_totals'], 'bank_totals':values['bank_totals']}
    

exchange_fluctuation()
#                    "(SELECT amount_total FROM account_invoice WHERE id="+invoice+")::numeric(16,2) AS invoice, " \
#                    "(l.amount_currency * "+str(form['rate'])+") AS current, " \
#                    "AND j.type IN ('sale','sale_refund','purchase','purchase_refund') " \
#                    "l.debit-l.credit AS history " \

#----------------------------------------------------------
#    Account Gain and Loss definition
#----------------------------------------------------------

class exchange_fluctuation_account(osv.osv):
    _name = "exchange.fluctuation.account"
    _description = "Exchange Fluctuation Accounts"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.company_id.name + ' ' + record.currency_id.name
            res.append((record['id'],name ))
        return res

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'gain_fluc_acc': fields.many2one('account.account', 'Gain Account', required=True),
        'loss_fluc_acc': fields.many2one('account.account', 'Loss Account', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'line_ids': fields.one2many('exchange.fluctuation.account.line', 'fluctuation_id', 'Enries'),
   }

    _sql_constraints = [
        ('account_fluctuation_uniq', 'unique (company_id)', 'The fluctuation account definition must be unique per company !')
    ]

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]

    _defaults = {
        'company_id': _default_company,
        'currency_id': 2,
    }


exchange_fluctuation_account()

class exchange_fluctuation_account_line(osv.osv):
    _name = "exchange.fluctuation.account.line"
    _description = "Exchange Fluctuation Accounts Lines"
    _order = "period_id"

    _columns = {
        'fluctuation_id': fields.many2one('exchange.fluctuation.account', 'Fluctuation', required=True, ondelete="cascade"),
        'move_id': fields.many2one('account.move', 'Entry', ondelete="cascade"),
        'bank_move_id': fields.many2one('account.move', 'Reverse Entry', ondelete="cascade"),
        'reverse_move_id': fields.many2one('account.move', 'Reverse Entry', ondelete="cascade"),
        'period_id': fields.many2one('account.period', 'Period'),
        'company_id': fields.many2one('res.company', 'Company'),
   }

    _sql_constraints = [
        ('fluctuation_move_uniq', 'unique (company_id,period_id)', 'The fluctuation entry must be unique per company !')
    ]

exchange_fluctuation_account_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
