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
from report import report_sxw
from osv import osv
import pooler
import re
import datetime
import text

class fiscal_statements(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		self.date_lst = []
		self.date_lst_string = ''
		super(fiscal_statements, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'comma_me': self.comma_me,
			'get_company': self._get_company,
			'get_title': self._get_title,
			'get_date_end': self._get_date_end,
			'lines': self._get_lines,
			'get_information': self._get_information,
			'get_message': self._get_message,
		})

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

	def set_context(self, objects, data, ids, report_type = None):
		self.fis_obj = self.pool.get('fiscal.statements')
		objects, new_ids = self.fis_obj._get_context(self.cr, self.uid, objects, data, ids, report_type = None)
		super(fiscal_statements, self).set_context(objects, data, new_ids, report_type)

	def _get_message(self, form):
		return form['message_text'] 

	def _get_information(self, form):
		return self.fis_obj._get_information(self.cr, self.uid, form)

	def _get_company(self, form):
		self.fis_obj = self.pool.get('fiscal.statements')
		return self.fis_obj._get_company(self.cr, self.uid, form)

	def _get_title(self, form):
		return self.fis_obj._get_title(self.cr, self.uid, form)

	def _get_date_end(self, form):
		return self.fis_obj._get_date_end(self.cr, self.uid, form)

	def _get_lines(self, obj, data):
		return self.fis_obj._get_lines(self.cr, self.uid, obj, data)

report_sxw.report_sxw('report.fiscal_statements_balance', 'res.partner',
		'addons/bias_fiscal_statements/report/fiscal_statements_balance.rml',parser=fiscal_statements,
		header=False)
report_sxw.report_sxw('report.fiscal_statements_balance_1', 'res.partner',
		'addons/bias_fiscal_statements/report/fiscal_statements_balance_1.rml',parser=fiscal_statements,
		header=True)
report_sxw.report_sxw('report.fiscal_statements_balance_1_message', 'res.partner',
		'addons/bias_fiscal_statements/report/fiscal_statements_balance_1_message.rml',parser=fiscal_statements,
		header=True)
report_sxw.report_sxw('report.fiscal_statements_income', 'res.partner',
		'addons/bias_fiscal_statements/report/fiscal_statements_income.rml',parser=fiscal_statements,
		header=True)
report_sxw.report_sxw('report.fiscal_statements_income_message', 'res.partner',
		'addons/bias_fiscal_statements/report/fiscal_statements_income_message.rml',parser=fiscal_statements,
		header=True)


