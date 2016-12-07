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
# Wizard Account Custom Report
#----------------------------------------------------------
class wizard_account_custom_report(osv.osv):
    _name = 'wizard.account.custom.report'
    _description = 'wizard_account_custom_report'
    
    def onchange_report(self, cr, uid, ids, report_id, context=None):
        if not report_id:
            return {'value':{
            'partner_ids': False,
            'periods_ids': False,
            'date1': False,
            'date2': False,
            'state': 'none'}
        }
        else:
            report = self.pool.get('account.custom.report').browse(cr, uid, report_id)
            return {'value':{
            'partner_ids': eval(report.partner_ids),
            'periods_ids': eval(report.periods_ids),
            'category_ids': report.category_ids and eval(report.category_ids),
            'date1': report.date1,
            'date2': report.date2,
            'fiscalyear': report.fiscalyear,
            'account_id': report.account_id,
            'cost_center_id': report.cost_center_id,
            'group_by': report.group_by,
            'balance': report.balance,
            'result_selection': report.result_selection,
            'state': 'bydate',#report.state,
            'report_zero': report.report_zero,
            'currency': report.currency,
            'partner_type': report.partner_type}
        }
wizard_account_custom_report()

#----------------------------------------------------------
# Account Custom Report
#----------------------------------------------------------
class account_custom_report(osv.osv):
    _name = 'account.custom.report'
    _description = 'Account Custom Report'

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=1 ),
        'result_selection': fields.char('Select', size=64, required=False, readonly=False),
        'page_split': fields.boolean('One Partner Per Page', required=False),
        'balance': fields.boolean('Only balances', required=False),
        'journal_type': fields.char('Select Journal Type', size=64, required=False, readonly=False),
        'group_by': fields.char('Group By', size=64, required=False, readonly=False),
        'state': fields.char('Date/Period Filter', size=64, required=False, readonly=False),
        'account_ids': fields.text('Accounts'),
        'partner_ids': fields.text('Partners'),
        'user_ids': fields.text('Partners'),
        'date1': fields.char('Start date', size=64),
        'date2': fields.char('End date', size=64),
        'periods_ids': fields.char('Periods', size=64),
        'category_ids': fields.char('Category', size=64),
        'state': fields.char('Date/Period Filter', size=64),
        'report_zero': fields.char('Report Zeros', size=64),
        'account_id': fields.integer('Account'),
        'period_length': fields.integer('Period length (days)'),
        'fiscalyear': fields.integer('Fiscalyear'),
        'cost_center_id': fields.integer('Cost Center'),
        'reconcil': fields.char('Entries to Include', size=64, required=False, readonly=False),
        'payment': fields.char('Payment Order', size=64, required=False, readonly=False),
        'direction_selection': fields.char('Analysis Direction', size=64, required=False, readonly=False),
        'currency': fields.char('Currency', size=64),
        'partner_type': fields.char('Partner Type', size=64),
    }

    ###############################################################
    #   Method of Third Party Ledger Report
    ###############################################################
    def _get_title(self, cr, uid, form):
        plus = '  [M.N.]'
        if form['currency'][0] == 'usd':
            plus = '  [USD]'
        res = form['name'] + plus
        print 'res=',res, form['currency']
        return res

    def _get_type(self, cr, uid, form):
        result = ''
        if form['result_selection'] == 'customer':
			result = 'Cuentas por Cobrar'
        elif form['result_selection'] == 'supplier':
			result = 'Cuentas por Pagar'
        elif form['result_selection'] == 'all':
			result = 'Cuentas por Pagar y Cobrar'
        elif form['result_selection'] in ('account','aged'):
			result = 'Cuenta '+ self.pool.get('account.account').browse(cr, uid, form['account_id']).code
        if form['reconcil'] == 'all':
			result = result + ', Todos los Movimientos'
        elif form['reconcil'] == 'unreconcile_today':
			result = result + ', Sin conciliar hasta la fecha'
        elif form['reconcil'] == 'unreconcile_inrange':
			result = result + ', Sin conciliar en el Rango'
        elif form['reconcil'] == 'reconcile_inrange':
			result = result + ', Conciliadas en el Rango'
        if form['journal_type'] == 'all':
			result = result + ', Todos los Diarios '
        elif form['journal_type'] == 'sale':
			result = result + ', Diarios de Venta'
        elif form['journal_type'] == 'purchase':
			result = result + ', Diarios de Compra'
        elif form['journal_type'] == 'cash':
			result = result + ', Diarios de Efectivo'
        elif form['journal_type'] == 'no_cash':
			result = result + ', Sin Diarios de Efectivo'
        if form['group_by'] == 'partner':
            result = result + ', Agrupado por Empresa'
        if form['category_ids']:
            result = result + ', Categoria;' + str(form['category_ids'])
        if form['cost_center_id']:
			result = result + ', CC ['+self.pool.get('account.cost.center').browse(cr, uid, form['cost_center_id']).code+']'
        if form['payment'] == 'exclude':
			result = result + ', Excluir los asientos pagados en Ordenes de Pago'
        if form['payment'] == 'only':
			result = result + ', Solo los asientos pagados en Ordenes de Pago'
        if form['currency'][0] == 'usd':
			result = result + ', Moneda: USD'
        else:
			result = result + ', Moneda: M.N.'
        return result

    def _get_date(self, cr, uid, form):
        start = time.strftime('%d-%b-%Y', time.strptime(self.date_lst[0],'%Y-%m-%d'))
        stop = time.strftime('%d-%b-%Y', time.strptime(self.date_lst[-1],'%Y-%m-%d'))
        if form and (form['result_selection'] == 'aged'):
            res = 'Al ' + str(start)
        else:
            res = str(start) + ' / ' + str(stop)
        return res

    def _get_date_start_stop(self, cr, uid, data):
        return self.date_lst[0], self.date_lst[-1]

    def _generate_totals(self, cr, uid, objects, data):
        for obj in objects:
            self._get_lines(cr, uid, obj, data, add=True)
        return True

    def _get_QUERY_JOURNAL(self, data):
            QUERY_JOURNAL = " "
            if data['form']['journal_type'] == 'all':
                QUERY_JOURNAL = " "
            elif data['form']['journal_type'] == 'sale':
                QUERY_JOURNAL = "AND j.type = 'sale'"
            elif data['form']['journal_type'] == 'purchase':
                QUERY_JOURNAL = "AND j.type = 'purchase'"
            elif data['form']['journal_type'] == 'cash':
                QUERY_JOURNAL = "AND j.type = 'cash'"
            elif data['form']['journal_type'] == 'no_cash':
                QUERY_JOURNAL = "AND j.type != 'cash'"
            return QUERY_JOURNAL

    def _get_QUERY_CC(self, data):
            QUERY_CC = " "
            if data['form']['cost_center_id']:
                QUERY_CC = "AND l.cost_center_id = "+str(data['form']['cost_center_id'])+" "
            return QUERY_CC

    def _get_query_date(self, cr, uid, data):
        QUERY_DATE ="AND l.date IN (" + self.date_lst_string + ") "
        if data['form']['reconcil'] == 'reconcile_inrange':
            QUERY_DATE = "AND l.date <= '" + str(self.date_lst[-1]) + "' "
        elif data['form']['result_selection'] == 'aged':
            QUERY_DATE = ""
        return QUERY_DATE

    def _sum_initial_query(self, cr, uid, data, query):
        result_tmp = 0.0
        if data['form']['reconcil'] == 'reconcile_inrange':
            reconcile = self._get_reconcile(cr, uid, data, "l.date < '" + self.date_lst[0] + "' ")
        else:
            reconcile = self._get_reconcile(cr, uid, data, "l.date >= '" + self.date_lst[0] + "' ")
        if self.date_lst_string:
			cr.execute(
					"SELECT (sum(l.debit) - sum(l.credit)) " \
					"FROM account_move_line l, account_journal j " \
					"WHERE " + query + " " \
					    "AND l.date < %s " \
						" " + reconcile + " " \
        				" " + self.QUERY_CC + " " \
                        "AND l.journal_id = j.id " + self.QUERY_JOURNAL + " " \
						"AND l.state = 'valid' " ,
					(self.date_lst[0],))
        contemp = cr.fetchone()
        if contemp != None:
			result_tmp = contemp[0] or 0.0
        else:
			result_tmp = result_tmp + 0.0
        return result_tmp

    def _sum_initial_obj(self, cr, uid, obj, data):
        if data['form']['group_by'] == 'account':
            child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, [obj.id])
            ids = ','.join(map(str, child_ids))
            where_query = "l.account_id in ("+ids+") "
            if data['form']['partner_ids'][0][2]:
                where_query += self.PARTNER_REQUEST
        else:
            where_query = "l.partner_id = "+ str(obj.id) +" AND l.account_id IN (" + self.account_ids + ") "
        return self._sum_initial_query(cr, uid, data, where_query)

    def _sum(self, cr, uid, data, select_query, where_query=False, obj=False):
        if not where_query:
            if data['form']['group_by'] == 'account':
                child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, [obj.id])
                ids = ','.join(map(str, child_ids))
                where_query = "l.account_id in ("+ids+") "
                if data['form']['partner_ids'][0][2]:
                    where_query += self.PARTNER_REQUEST
            else:
                where_query = "l.partner_id = "+ str(obj.id) +" AND l.account_id IN (" + self.account_ids + ") "
        result_tmp = 0.0
        if self.date_lst_string:
			cr.execute(
					"SELECT " + select_query + " " \
					"FROM account_move_line l, account_journal j " \
					"WHERE "+ where_query + " " \
						" " + self.RECONCILE_TAG + " " \
    					"AND l.date IN (" + self.date_lst_string + ")" \
        				" " + self.QUERY_CC + " " \
                        "AND l.journal_id = j.id " + self.QUERY_JOURNAL + " " \
						"AND l.state = 'valid' "
					)
			contemp = cr.fetchone()
			if contemp != None:
				result_tmp = contemp[0] or 0.0
			else:
				result_tmp = result_tmp + 0.0
        return result_tmp

    def _sum_initial(self, cr, uid, data):
        query = " "+ self.PARTNER +" l.account_id IN (" + self.account_ids + ") "
        return self._sum_initial_query(cr, uid, data, query)

    def _sum_debit_obj(self, cr, uid, obj, data):
        select_query = "sum(l.debit)"
        return self._sum(cr, uid, data, select_query, False, obj)

    def _sum_credit_obj(self, cr, uid, obj, data):
        select_query = "sum(l.credit)"
        return self._sum(cr, uid, data, select_query, False, obj)

    def _sum_debit(self, cr, uid, data):
        select_query = "sum(l.debit)"
        where_query = " "+ self.PARTNER +" l.account_id IN (" + self.account_ids + ") "
        return self._sum(cr, uid, data, select_query, where_query)

    def _sum_credit(self, cr, uid, data):
        select_query = "sum(l.credit)"
        where_query = " "+ self.PARTNER +" l.account_id IN (" + self.account_ids + ") "
        return self._sum(cr, uid, data, select_query, where_query)

    def _get_company(self, cr, uid, form):
        return self.pool.get('res.company').browse(cr, uid, form['company_id']).name

    def _get_currency(self, cr, uid, form):
        return self.pool.get('res.company').browse(cr, uid, form['company_id']).currency_id.name

    def _get_label(self, cr, uid, form):
        result = ('','')
        if form['result_selection'] == 'aged':
            if form['direction_selection'] == 'past':
                result = ('Por Vencer','+ de '+form['0']['name_stop'])
            else:
                result = ('Vencido','+ de '+form['0']['name_stop'])
        return result

    def _get_code(self, cr, uid, obj, group_by):
        if group_by == 'partner':
            res = obj.ref
        else:
            res = obj.code
        return res

    def _date_sp(self, cr, uid, date):
		return str(time.strftime('%d-%m-%Y', time.strptime(date,'%Y-%m-%d')))

    def date_range(self, start, end):
        if not start or not end:
			return []
        start = datetime.date.fromtimestamp(time.mktime(time.strptime(start,"%Y-%m-%d")))
        end = datetime.date.fromtimestamp(time.mktime(time.strptime(end,"%Y-%m-%d")))
        full_str_date = []
        r = (end+datetime.timedelta(days=1)-start).days
        date_array = [start+datetime.timedelta(days=i) for i in range(r)]
        for date in date_array:
			full_str_date.append(str(date))
        return full_str_date

    def transform_period_into_date_array(self, cr, uid, data):
        if not data['form']['periods_ids'][0][2] :
			periods_id =  self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',data['form']['fiscalyear'])])
        else:
			periods_id = data['form']['periods_ids'][0][2]
        date_array = []
        for period_id in periods_id:
			period_obj = self.pool.get('account.period').browse(cr, uid, period_id)
			date_array = date_array + self.date_range(period_obj.date_start,period_obj.date_stop)
        self.date_lst = date_array
        self.date_lst.sort()

    def transform_date_into_date_array(self, cr, uid, data):
        return_array = self.date_range(data['form']['date1'],data['form']['date2'])
        self.date_lst = return_array
        self.date_lst.sort()

    def transform_both_into_date_array(self, cr, uid, data):
        if not data['form']['periods_ids'][0][2] :
			periods_id =  self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',data['form']['fiscalyear'])])
        else:
			periods_id = data['form']['periods_ids'][0][2]
        date_array = []
        for period_id in periods_id:
			period_obj = self.pool.get('account.period').browse(cr, uid, period_id)
			date_array = date_array + self.date_range(period_obj.date_start,period_obj.date_stop)

        period_start_date = date_array[0]
        date_start_date = data['form']['date1']
        period_stop_date = date_array[-1]
        date_stop_date = data['form']['date2']

        if period_start_date<date_start_date:
			start_date = period_start_date
        else :
			start_date = date_start_date

        if date_stop_date<period_stop_date:
			stop_date = period_stop_date
        else :
			stop_date = date_stop_date
        final_date_array = []
        final_date_array = final_date_array + self.date_range(start_date, stop_date)
        self.date_lst = final_date_array
        self.date_lst.sort()

    def transform_none_into_date_array(self, cr, uid, data):
        sql = "SELECT min(date) as start_date from account_move_line"
        cr.execute(sql)
        start_date = cr.fetchone()[0]
        sql = "SELECT max(date) as start_date from account_move_line"
        cr.execute(sql)
        stop_date = cr.fetchone()[0]
        array= []
        array = array + self.date_range(start_date, stop_date)
        self.date_lst = array
        self.date_lst.sort()

    def _get_total_aged(self):
        return self.sum_aged

    def _get_total_obj_aged(self, obj):
        return (self.sum_obj_aged.has_key(obj.id) and self.sum_obj_aged[obj.id]) or 0

    def _get_QUERY_AGED(self, cr, uid, data):
        QUERY_AGED = " "
        cr.execute(
            "select l.move_line_id from payment_line l, payment_order p " \
	            "where l.order_id = p.id and p.state = 'done' and move_line_id is not null and not l.partial " )
        res_1 = ','.join([str(a) for (a,) in cr.fetchall()]) or str(0)
        cr.execute(
            "select l.move_line_id from payment_cheque_line l, payment_cheque p " \
	            "where l.cheque_id = p.id and p.state = 'done' and move_line_id is not null and not l.partial " )
        res_2 = ','.join([str(a) for (a,) in cr.fetchall()]) or str(0)
        cr.execute(
            "select ml.id from payment_line pl, payment_order p, account_move_line ml, account_move m " \
	        "where ml.account_id in (" + self.account_ids + ") " \
        	"and p.state = 'done' and pl.move_line_id is not null and not pl.partial " \
	        "and pl.order_id = p.id and pl.move_id = m.id and ml.move_id = m.id " )
        res_3 = ','.join([str(a) for (a,) in cr.fetchall()]) or str(0)
        cr.execute(
            "select ml.id from payment_cheque_line pl, payment_cheque p, account_move_line ml, account_move m "
	        "where ml.account_id in (" + self.account_ids + ") "
	        "and p.state = 'done' and pl.move_line_id is not null and not pl.partial "
	        "and pl.cheque_id = p.id and p.move_id = m.id and ml.move_id = m.id " )
        res_4 = ','.join([str(a) for (a,) in cr.fetchall()]) or str(0)
        if data['form']['payment'] == 'exclude':
            QUERY_AGED = "AND l.id NOT IN (" + res_1 + res_2 + res_3 + res_4 + ") "
        if data['form']['payment'] == 'only':
            QUERY_AGED = "AND l.id IN (" + res_1 + res_2 + res_3 + res_4 + ") "
        return QUERY_AGED

    def _get_lines(self, cr, uid, obj, data, add=False):
        inicio = time.time()
        if self.date_lst_string:
            if data['form']['group_by'] == 'partner':
                OBJ = "l.partner_id = %s AND l.account_id IN (" + self.account_ids + ") "
            else:
                if data['form']['partner_ids'][0][2]:
                    partner = ','.join([str(a) for a in data['form']['partner_ids'][0][2]])
                    OBJ = "l.partner_id in ("+ partner +") AND l.account_id = %s "
                else:
                    OBJ = "l.account_id = %s "
#FROM a LEFT JOIN b ON (a.bid = b.id) LEFT JOIN c ON (a.cid = c.id)
            cr.execute(
				"SELECT a.code as acc_code, a.name as acc_name, l.cost_center_id, l.date, j.code, l.partner_id, l.ref, l.name, l.debit, l.credit, " \
                "l.move_id as mid, m.name as move_name, l.id as lid, l.date_maturity, l.reconcile_id, l.reconcile_partial_id " \
				"FROM account_move_line l " \
                "LEFT JOIN account_account a ON (l.account_id = a.id) " \
                "LEFT JOIN account_journal j ON (l.journal_id = j.id) " \
                "LEFT JOIN account_move m ON (l.move_id = m.id) " \
				"WHERE " + OBJ + " " \
				" " + self.QUERY_AGED + " " \
				" " + self.RECONCILE_TAG + " " \
				" " + self.QUERY_DATE + " " \
				" " + self.QUERY_CC + " " \
                "AND  " + self.QUERY_JOURNAL + " " \
                "a.type != 'view' " \
                "AND l.state = 'valid' " \
                "ORDER BY l.date",(obj.id,))
            res = cr.dictfetchall()
            #imprimimos el resultado
            full_account = []
            if not res:
                return full_account
            inicio = time.time()
            full_account = self._add_partner_inf(cr, uid, obj, data, res, add)
            return full_account

    def _add_partner_inf(self, cr, uid, obj, data, res, add):
            full_account = []
            form = data['form']
            if form['result_selection'] == 'aged':
                sum = 0.0
            else:
                sum = self._sum_initial_obj(cr, uid, obj, data)
            today = datetime.date.today()
            inicio = time.time()
            self.sum_obj_aged[obj.id] = [0,0,0,0,0,0]
            for r in res:
                r['progress'] = sum + r['debit'] - r['credit']
                if r['partner_id']:
                    partner = self.pool.get('res.partner').browse(cr, uid, r['partner_id'])
                    r['partner_id'] = partner.name
                    r['payment_term'] = partner.property_payment_term and partner.property_payment_term.name or ''
                    if r['date_maturity']:
                        maturity = time.strptime(r['date_maturity'],'%Y-%m-%d')
                    else:
                        maturity = time.strptime(r['date'],'%Y-%m-%d')
                    maturity = datetime.date(maturity[0], maturity[1], maturity[2])
                    r['aged'] = maturity and (today - maturity).days
                    full_account.append(r)
                    if form['result_selection'] == 'aged':
                        r = self._add_periods(cr, uid, obj, data, r, add=True)
                else:
                    full_account.append(r)
            return full_account

    def _add_periods(self, cr, uid, obj, data, r, add):
        form = data['form']
        seg0 = seg1 = seg2 = seg3 = segi = 0
        if (form['direction_selection'] == 'past'):
            aged = r['aged']
            if int(aged) < 0:
                segi = r['debit'] - r['credit']
            if int(aged) < int(form['2']['name_stop']):
                seg0 = r['debit'] - r['credit']
            elif int(aged) < int(form['1']['name_stop']):
                seg1 = r['debit'] - r['credit']
            elif int(aged) < int(form['0']['name_stop']):
                seg2 = r['debit'] - r['credit']
            elif int(aged) >= int(form['0']['name_stop']):
                seg3 = r['debit'] - r['credit']
            if add:
                self.sum_obj_aged[obj.id][0] += segi
                self.sum_obj_aged[obj.id][1] += seg0
                self.sum_obj_aged[obj.id][2] += seg1
                self.sum_obj_aged[obj.id][3] += seg2
                self.sum_obj_aged[obj.id][4] += seg3
                self.sum_obj_aged[obj.id][5] = self.sum_obj_aged[obj.id][1] + self.sum_obj_aged[obj.id][2]+ \
                                               self.sum_obj_aged[obj.id][3] + self.sum_obj_aged[obj.id][4]
                self.sum_aged[0] += segi
                self.sum_aged[1] += seg0
                self.sum_aged[2] += seg1
                self.sum_aged[3] += seg2
                self.sum_aged[4] += seg3
                self.sum_aged[5] = self.sum_aged[1]+self.sum_aged[2]+self.sum_aged[3]+self.sum_aged[4]
            r['segi'], r['seg0'], r['seg1'], r['seg2'], r['seg3'],  = segi, seg0, seg1, seg2, seg3
        else:
            pass
        return r

    def _get_reconcile(self, cr, uid, data, query):
        cr.execute(
				"SELECT DISTINCT rec.id " \
				"FROM account_move_reconcile as rec, account_move_line AS l, account_account AS a " \
				"WHERE " + query + " " \
					"AND l.account_id IN (" + self.account_ids + ") " \
                    "AND l.reconcile_id = rec.id " \
					"AND l.state = 'valid' " \
					"AND l.account_id = a.id AND a.company_id = %s " ,
			(data['form']['company_id'],))
        res = ','.join([str(a) for (a,) in cr.fetchall()]) or str(0)
        if data['form']['reconcil'] == 'reconcile_inrange':
            reconcile =  "AND l.reconcile_id IN (" + res + ") " 
        elif data['form']['reconcil'] == 'unreconcile_inrange':
            reconcile =  "AND (l.reconcile_id IS NULL OR l.reconcile_id IN (" + res + ")) "
        else:
            reconcile = self.RECONCILE_TAG
        return reconcile

    def _get_context(self, cr, uid, objects, data, ids, report_type = None):
        self.PARTNER_REQUEST = ''
        self.sum_obj_aged = {}
        self.sum_aged = [0,0,0,0,0,0]
        self.QUERY_AGED = ''
        self.QUERY_JOURNAL = QUERY_JOURNAL = self._get_QUERY_JOURNAL(data)
        self.QUERY_CC = self._get_QUERY_CC(data)
        if data['form'].has_key('partner_ids'):
            if data['form']['partner_ids'][0][2]:
    			self.PARTNER_REQUEST =  "AND l.partner_id IN (" + ','.join(map(str, data['form']['partner_ids'][0][2])) + ")"
		# Transformation des date
        if data['form']['state'] == 'none':
			self.transform_none_into_date_array(cr, uid, data)
        elif data['form']['state'] == 'bydate':
			self.transform_date_into_date_array(cr, uid, data)
        elif data['form']['state'] == 'byperiod':
			self.transform_period_into_date_array(cr, uid, data)
        elif data['form']['state'] == 'all':
			self.transform_both_into_date_array(cr, uid, data)
        self.date_lst_string = ''
        if self.date_lst:
			self.date_lst_string = '\'' + '\',\''.join(map(str, self.date_lst)) + '\''
        self.QUERY_DATE = QUERY_DATE = self._get_query_date(cr, uid, data)
        if type(data['form']['account_ids'][0]).__name__ == 'tuple':
            data['form']['account_ids'] = data['form']['account_ids'][0][2]
        cr.execute(
			"SELECT a.id " \
			"FROM account_account a " \
			"WHERE a.company_id = %s " \
				"AND a.active AND a.id in %s", (data['form']['company_id'], tuple(data['form']['account_ids'])))#[0][2])))
        self.account_ids = ','.join([str(a) for (a,) in cr.fetchall()])
		# select reconcile type
        self.RECONCILE_TAG = " "
        if data['form']['reconcil'] == 'all':
			self.RECONCILE_TAG = RECONCILE_TAG = " "
        elif data['form']['reconcil'] == 'unreconcile_today':
			self.RECONCILE_TAG = RECONCILE_TAG = "AND reconcile_id IS NULL "
        elif data['form']['reconcil'] == 'unreconcile_inrange':
            self.RECONCILE_TAG = RECONCILE_TAG = self._get_reconcile(cr, uid, data, "l.date >= '" + self.date_lst[-1] + "' ")
        elif data['form']['reconcil'] == 'reconcile_today':
			self.RECONCILE_TAG = " "
        elif data['form']['reconcil'] == 'reconcile_inrange':
            self.RECONCILE_TAG = RECONCILE_TAG = self._get_reconcile(cr, uid, data, "l.date IN (" + self.date_lst_string + ") ")
        else: # 'reconcile_inrange'
			self.RECONCILE_TAG = " "
#        if data['form']['result_selection'] == 'aged':
#            self.QUERY_AGED = QUERY_AGED = self._get_QUERY_AGED(cr, uid, data)
        if data['form']['report_zero'] == 'zero':
            self.QUERY_AGED = QUERY_DATE = QUERY_JOURNAL = RECONCILE_TAG = ''
        if data['form']['group_by'] == 'partner':
            cr.execute(
				"SELECT DISTINCT l.partner_id, partner.name " \
				"FROM account_move_line AS l " \
                "LEFT JOIN account_account AS account ON (l.account_id = account.id) " \
                "LEFT JOIN res_partner as partner ON (l.partner_id = partner.id) " \
                "LEFT JOIN account_journal as j ON (l.journal_id = j.id) " \
				"WHERE l.partner_id IS NOT NULL " \
					"AND l.state = 'valid' " \
					   " " + self.QUERY_AGED + " " \
    				   " " + QUERY_DATE + " " \
                       " " + QUERY_JOURNAL + " " \
					   " " + RECONCILE_TAG + " "\
					"AND l.account_id IN (" + self.account_ids + ") " \
					                    " " + self.PARTNER_REQUEST + " " \
					"AND account.company_id = %s " \
					"AND account.active ORDER BY partner.name" ,
				(data['form']['company_id'],))
            res = cr.dictfetchall()
            partner_to_use = []
            for res_line in res:
				    partner_to_use.append(res_line['partner_id'])
            new_ids = partner_to_use
            self.partner_ids = ','.join(map(str, new_ids))
            self.PARTNER = "l.partner_id IN (" + self.partner_ids + ") AND "
            objects = self.pool.get('res.partner').browse(cr, uid, new_ids)
        else:
            new_ids = data['form']['account_ids'] #[0][2]
            objects = self.pool.get('account.account').browse(cr, uid, new_ids)
            self.PARTNER = " "
            if data['form']['partner_ids'][0][2]:
                self.PARTNER = "l.partner_id IN (" + ','.join(map(str, data['form']['partner_ids'][0][2])) + ") AND "
        return objects, new_ids 

    def get_result(self, cr, uid, data, context={}):
        objects, ids = False, False
        form = data['form']
        objects, new_ids = self._get_context(cr, uid, objects, data, ids, report_type = None)
        category = form['category_ids'] and ' (' + ','.join(map(str, form['category_ids'])) + ') ' or ''
        partners = form['partner_ids'][0][2] and '(' + ','.join(map(str, form['partner_ids'][0][2])) + ')' or ''
        cc = form['cost_center_id'] or 0
        aged = form['result_selection'] == 'aged'
        period = form['period_length']
        zero = False
        if form['report_zero'] == 'zero': zero = True
        reconcile = False
        if form['reconcil'] == 'unreconcile_today': reconcile = True
        balance = False
        if form['balance'] == (1 or True): balance = True
        fyear = False
        if form['fiscalyear'] == (1 or True): fyear = True
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('code','=',form['currency'])])
        c = currency_ids and currency_ids[0] or 0
        result = []
        result += [(self._get_company(cr, uid, form),)]
        result += [(self._get_title(cr, uid, form),)]
        result += [ ('Rango de Fechas', self._get_date(cr, uid, form)) ]
        result += [ ('Tipo de Reporte', self._get_type(cr, uid, form)) ]
#        print form['account_id'], form['date1'], \
#            form['date2'], category, partners, cc, balance, (form['group_by'] == 'partner'), zero, reconcile, aged, period, \
#            c, form['partner_type'][0], fyear
#        cr.execute("SELECT * FROM getLedger(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(form['account_id'], form['date1'], \
#            form['date2'], category, partners, cc, balance, (form['group_by'] == 'partner'), zero, reconcile, aged, period, \
#            c, form['partner_type'][0], fyear))
#        res = cr.dictfetchall()
        res = self.pool.get('financial.reports').get_function(cr, uid, data, context=context)
        if form['result_selection'] == 'aged':
            if form['balance']:
                print 'aged balance'
                result += [('EMPRESA', 'POR VENCER', form['2']['name'], form['1']['name'],
                        form['0']['name'], '+ de '+form['0']['name_stop'], 'SALDO')]
                for l in res:
                    result += [(
                        l['line_ref'], 
                        c and l['uto_mature'] or l['to_mature'] or '', 
                        c and l['urange_0'] or l['range_0'] or '', 
                        c and l['urange_1'] or l['range_1'] or '', 
                        c and l['urange_2'] or l['range_2'] or '', 
                        c and l['uout_range'] or l['out_range'] or '', 
                        (c and l['title']=='t' and l['ubalance'] ) or (not c and l['balance']) or '' 
                        )]
            else:
                print 'aged ledger'
                result += [('REFERENCIA/EMPRESA', 'FECHA', 'CODIGO', 'CUENTA','DIAS DE CREDITO', 'DIAS VENCIDOS', 'POR VENCER', form['2']['name'], 
                            form['1']['name'], form['0']['name'], '+ de '+form['0']['name_stop'], 'SALDO', 'LID', 'POLIZA', 'CONCILIACION', 'PARCIAL', 
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
                        l['line_id'], 
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
                            'Débito', 'Crédito', 'Saldo', 'Conciliacion', 'Parcial', 'Fecha de Pago')]
                for l in res:
                    result += [(l['account_code'], l['account_name'], l['cost_center_code'], l['line_date'], l['line_journal'], l['line_move_id'], \
                                l['line_move'], l['line_id'], l['partner_name'] or '', l['line_ref'], l['line_name'], l['initial'] or '', \
                                l['line_debit'] or '', l['line_credit'] or '', l['balance'] or '', l['reconcile'], l['reconcile_partial'], \
                                l['payment_date'], l['title'] or '' )]
        return result

    def get_id_to_open(self, cr, uid, data, context={}):
        objects, ids = False, False
        form = data['form']
        objects, new_ids = self._get_context(cr, uid, objects, data, ids, report_type = None)
        result = []
        for p in objects:
            for l in self._get_lines(cr, uid, p, data):
                result += [( l['lid'] )]
        return str(result)

account_custom_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

