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

import pooler
import time
import re
#import rml_parse
import datetime
from report import report_sxw
import text

class custom_report(report_sxw.rml_parse):#(rml_parse.rml_parse):
	def __init__(self, cr, uid, name, context):
		self.total = []
		super(custom_report, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'lines': self._get_lines,
			'get_title': self._get_title,
			'sum_initial_partner' : self._sum_initial_obj,
			'sum_debit_partner': self._sum_debit_obj,
			'sum_credit_partner': self._sum_credit_obj,
			'sum_initial': self._sum_initial,
			'sum_debit': self._sum_debit,
			'sum_credit': self._sum_credit,
			'get_company': self._get_company,
			'get_currency': self._get_currency,
			'get_date': self._get_date,
			'get_type': self._get_type,
			'get_code': self._get_code,
			'date_sp': self._date_sp,
			'get_label': self._get_label,
			'get_total_obj_aged': self._get_total_obj_aged,
			'get_total_aged': self._get_total_aged,
			'generate_totals': self._generate_totals,
			'comma_me': self.comma_me,
			'get_balance_lines': self._get_balance_lines,
		})

	def _get_balance_lines(self, data, context={}):
	        res = self.lin_obj.get_function(self.cr, self.uid, data, context=context)
		return res

	def _get_title(self, form):
		self.lin_obj = self.pool.get('financial.reports')
		return self.lin_obj._get_title(self.cr, self.uid, form)

	def _generate_totals(self, objets, data):
		return self.lin_obj._generate_totals(self.cr, self.uid, objets, data)

	def _get_lines(self, obj, data):
		return self.lin_obj._get_lines(self.cr, self.uid, obj, data)

	def _sum_initial_obj(self, obj, data):
		return self.lin_obj._sum_initial_obj(self.cr, self.uid, obj, data)

	def _sum_debit_obj(self, obj, data):
		return self.lin_obj._sum_debit_obj(self.cr, self.uid, obj, data)

	def _sum_credit_obj(self, obj, data):
		return self.lin_obj._sum_credit_obj(self.cr, self.uid, obj, data)

	def _sum_initial(self, data):
		return self.lin_obj._sum_initial(self.cr, self.uid, data)

	def _sum_debit(self, data):
		return self.lin_obj._sum_debit(self.cr, self.uid, data)

	def _sum_credit(self, data):
		return self.lin_obj._sum_credit(self.cr, self.uid, data)

	def _get_company(self, form):
		self.lin_obj = self.pool.get('financial.reports')
		return self.lin_obj._get_company(self.cr, self.uid, form)

	def _get_currency(self, form):
		return self.lin_obj._get_currency(self.cr, self.uid, form)

	def _get_date(self, form=False):
		return self.lin_obj._get_date(self.cr, self.uid, form)

	def _get_type(self, form):
		return self.lin_obj._get_type(self.cr, self.uid, form)

	def _get_code(self, obj, group_by):
		return self.lin_obj._get_code(self.cr, self.uid, obj, group_by)

	def _date_sp(self,date):
		return self.lin_obj._date_sp(self.cr, self.uid, date)

	def _get_label(self,form):
		return self.lin_obj._get_label(self.cr, self.uid, form)

	def _get_total_aged(self):
		return self.lin_obj._get_total_aged()

	def _get_total_obj_aged(self,obj):
		return self.lin_obj._get_total_obj_aged(obj)

	def comma_me(self,amount):
		if  type(amount) is float :
			amount = str('%.2f'%amount)
		else :
			amount = str(amount)
		if (amount == '0'):
		     return ' '
		orig = amount
		new = re.sub("^(-?\d+)(\d{3})", "\g<1>,\g<2>", amount)
		if orig == new:
			return new
		else:
			return self.comma_me(new)

report_sxw.report_sxw('report.financial.reports_aged', 'res.partner',
		'addons/bias_account_report/report/financial_reports_aged.rml',parser=custom_report,
		header=False)

report_sxw.report_sxw('report.financial.reports_balance', 'res.partner',
		'addons/bias_account_report/report/financial_reports_balance.rml',parser=custom_report,
		header=False)

report_sxw.report_sxw('report.financial.reports_other', 'res.partner',
		'addons/bias_account_report/report/financial_reports_other.rml',parser=custom_report,
		header=False)


