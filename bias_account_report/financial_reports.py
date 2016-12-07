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


from osv import osv
from osv import fields
import netsvc
import time
import decimal
from decimal import Decimal
import datetime

#----------------------------------------------------------
# Financial Reports
#----------------------------------------------------------
class financial_reports(osv.osv):
    _name = 'financial.reports'
    _description = 'Financial Reports'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'customer_account_id': fields.many2one('account.account', 'Customer Account'),
        'supplier_account_id': fields.many2one('account.account', 'Supplier Account'),
        'creditor_account_id': fields.many2one('account.account', 'Creditor Account'),
        'mn_customer_account_id': fields.many2one('account.account', 'Customer Account MN'),
        'usd_customer_account_id': fields.many2one('account.account', 'Customer Account USD'),
        'mn_supplier_account_id': fields.many2one('account.account', 'Supplier Account MN'),
        'usd_supplier_account_id': fields.many2one('account.account', 'Supplier Account USD'),
        'statement_balance_id': fields.many2one('fiscal.statements', 'General Balance'),
        'statement_income_id': fields.many2one('fiscal.statements', 'Income Statement'),
    }
    _sql_constraints = [
        ('report_company_uniq', 'unique (company_id)', 'The Report Configuration must be unique per company !')
    ]

    ###############################################################
    #   Method of Financial Reports
    ###############################################################
    def _get_company(self, cr, uid, form):
        return self.pool.get('res.users').browse(cr, uid, uid).company_id.name

    def _get_title(self, cr, uid, form):
        plus = ''
        if form['currency'] == 'USD':
            plus = '  [USD]'
        elif form['currency'] == 'MN':
            plus = '  [M.N.]'
        res = form['name'] + plus
        return res

    def _get_date(self, cr, uid, form):
        start = time.strftime('%d-%b-%Y', time.strptime(form['date1'],'%Y-%m-%d'))
        stop = time.strftime('%d-%b-%Y', time.strptime(form['date2'],'%Y-%m-%d'))
        res = str(start) + ' / ' + str(stop)
        return res

    def _get_type(self, cr, uid, form):
        result = ''
        result = 'Cuenta: '+ self.pool.get('account.account').browse(cr, uid, form['account_id']).code
        if 'partner_type' in form and form['partner_type'] == 'customer':
            result = result + ', Filtro: Clientes'
        elif 'partner_type' in form and form['partner_type'] == 'supplier':
            result = result + ', Filtro: Proveedores'
        return result

    def _date_sp(self, cr, uid, date):
		return str(time.strftime('%d-%m-%Y', time.strptime(date,'%Y-%m-%d')))

    def get_function(self, cr, uid, data, context={}):
#       160 2010-06-01 2010-06-30   0 False False True False False 30 0 none True
        form = data['form']
        category = ''
        partners = ''
        if form.get('partner_ids',False):
            partners = form['partner_ids'][0][2] and '(' + ','.join(map(str, form['partner_ids'][0][2])) + ')' or ''
        cc = 0
        balance = False
        if form['balance'] == (1 or True): balance = True # True: Auxiliar, False: Balance
        group_by = form.get('group_by',False) == 'partner' # True: by partner, False: by account
        zero = False
        if form.get('report_zero',False): #
            if form['report_zero'] == 'zero':
                zero = True
            else:
                zero = False
        else:
            zero = True
        if form['result_selection'] == 'aged': #
            reconcile = aged = True
        else:
            reconcile = aged = False
        period = form.get('period_length', False) or 30
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('code','=',form['currency'])])
        currency = currency_ids and currency_ids[0] or 0
        partner_type = form.get('partner_type','none') or 'none'
        fyear = True
        journal = form.has_key('journal_ids') and form['journal_ids'][0][2] and '(' + ','.join(map(str, form['journal_ids'][0][2])) + ')' or ''

        print form['account_id'], form['date1'], form['date2'], category, partners, cc, balance, group_by, zero, reconcile, aged, period, currency, partner_type, fyear, journal
        cr.execute("SELECT * FROM getLedger(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(form['account_id'], form['date1'], form['date2'], category, partners, cc, balance, group_by, zero, reconcile, aged, period, currency, partner_type, fyear, journal))
        res = cr.dictfetchall()
        return res

    def get_result(self, cr, uid, data, context={}):
        form = data['form']
        c = form['currency'] == 'USD'
        res = self.get_function(cr, uid, data, context=context)
        result = []
        result += [(self._get_company(cr, uid, form),)]
        result += [(self._get_title(cr, uid, form),)]
        result += [ ('Rango de Fechas', self._get_date(cr, uid, form)) ]
        result += [ ('Tipo de Reporte', self._get_type(cr, uid, form)) ]
        if form['result_selection'] == 'aged':
            if form['balance']:
                print 'aged balance'
                result += [('EMPRESA', 'POR VENCER', form['2']['name'], form['1']['name'],
                        form['0']['name'], '+ de '+form['0']['name_stop'], 'SALDO')]
                for l in res:
                    result += [(
                        l['line_ref'], 
                        c and l['uto_mature'] or l['to_mature'] or '', c and l['urange_0'] or l['range_0'] or '', 
                        c and l['urange_1'] or l['range_1'] or '', c and l['urange_2'] or l['range_2'] or '', 
                        c and l['uout_range'] or l['out_range'] or '', 
                        (c and l['title']=='t' and l['ubalance'] ) or (not c and l['balance']) or '' 
                        )]
            else:
                print 'aged ledger'
                result += [('REFERENCIA/EMPRESA', 'FECHA', 'CODIGO', 'CUENTA','DIAS DE CREDITO', 'DIAS VENCIDOS', 'POR VENCER', form['2']['name'], 
                            form['1']['name'], form['0']['name'], '+ de '+form['0']['name_stop'], 'SALDO', 'POLIZA', 'CONCILIACION', 'PARCIAL', 
                            'FECHA DE PAGO', 'Titulo')]
                for l in res:
                    result += [(
                        l['line_ref'], 
                        l['line_date'], 
                        l['account_code'], 
                        l['account_name'], 
                        l['credit_days'], 
                        l['mature'] , 
                        c and l['uto_mature'] or l['to_mature'] or '', 
                        c and l['urange_0'] or l['range_0'] or '', 
                        c and l['urange_1'] or l['range_1'] or '', 
                        c and l['urange_2'] or l['range_2'] or '', 
                        c and l['uout_range'] or not c and l['out_range'] or '', 
                        (c and l['title']=='t' and l['ubalance'] ) or (not c and l['balance']) or '', 
                        l['line_move'], 
                        l['reconcile'], 
                        l['reconcile_partial'], 
                        l['payment_date'], 
                        l['title'] or ''
                        )]
        else:
            if form['balance']:
                print 'balanza'
                result += [('','','Inicial','Débito','Crédito','Saldo',)]
                for l in res:
                    result += [( l['account_code'], l['account_name'], l['initial'] or 0, l['line_debit'] or 0, l['line_credit'] or 0, 
                                l['balance'] or 0 )]
            else:
                print 'auxiliar'
                result += [('Codigo','Nombre Cuenta','Centro de Costos','Fecha','Libro','PID','Poliza', 'LID','Empresa','Ref.','Nombre', 'Inicial', \
                            'Débito', 'Crédito', 'Saldo', 'Debito Moneda', 'Credito Moneda', 'Paridad', 'Moneda', 'Conciliacion', 'Parcial', 
                            'Fecha de Pago')]
                for l in res:
                    amount_currency = ((l['line_credit'] and l['amount_currency'] > 1) and -1 or 1) * (l['amount_currency'] or '')
                    result += [(l['account_code'], l['account_name'], l['cost_center_code'], l['line_date'], l['line_journal'], l['line_move_id'], \
                                l['line_move'], l['line_id'], l['partner_name'] or '', l['line_ref'], l['line_name'], l['initial'] or '', \
                                l['line_debit'] or '', l['line_credit'] or '', l['balance'] or '', \
                                amount_currency > 0 and amount_currency or '', amount_currency < 0 and -amount_currency or '', \
                                amount_currency and abs((l['line_debit'] - l['line_credit'])/amount_currency) ,\
                                l['currency'] or '', l['reconcile'], l['reconcile_partial'], l['payment_date'] )]
        return result

financial_reports()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

