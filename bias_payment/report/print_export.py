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
import pooler
from report import report_sxw
import text

class print_export(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
        	super(print_export, self).__init__(cr, uid, name, context)
            	self.sum = {}
        	self.localcontext.update({
        	    'time': time,
		    'texto': text.text,
		    'get_lines': self._get_lines,
		    'moneyfmt': self._moneyfmt,
		    'money': self._money,
		    'sum': self._sum,
        	})

	def _sum(self, code):
		_sum = False
		if code in self.sum.keys():
			_sum = self.sum[code]
			_sum = text.moneyfmt(_sum)
		return _sum

	def _get_lines(self,payment, code):
		payment = eval(payment)
		lines = []
		for pay in payment:
			if pay[0] == code:
				lines.append(pay)
		if not lines:
			lines = [(False,False,False,False,False)]
#			lines = [(0,0,0,0,0)]
		return lines

	def _money(self, number):
		if not number:
			return False
		number = float(number)
		number = text.moneyfmt('%.2f' % number)
		if not number:
			number = False
		return number

	def _moneyfmt(self, number, code):
		if not number:
			return False
		number = float(number)/100
		if not code in self.sum.keys():
			self.sum[code] = 0.0
		self.sum[code] = self.sum[code] + number
		number = text.moneyfmt('%.2f' % number)
		if not number:
			number = False
		return number

	def _total_debit(self,move_id):
		self.cr.execute("SELECT SUM(credit) " \
				"FROM account_move_line AS line " \
				"WHERE (line.move_id = %s) ",
					(move_id.id,))
		total = self.cr.fetchone()[0]
		return total

	def _total_credit(self,move_id, obj=False):
		self.cr.execute("SELECT SUM(debit) " \
				"FROM account_move_line AS line " \
				"WHERE (line.move_id = %s) ",
					(move_id.id,))
		total = self.cr.fetchone()[0]
		chk_obj = self.pool.get('payment.cheque')
		chk_obj.write(self.cr, self.uid, [obj.id],{'state': 'printed'})
		return total

report_sxw.report_sxw('report.print.export', 'payment.order',
	'addons/bias_payment/report/print_export.rml', parser=print_export, header=True)



