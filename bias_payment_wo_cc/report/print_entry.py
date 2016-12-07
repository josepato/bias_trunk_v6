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

class print_cheque(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
        	super(print_cheque, self).__init__(cr, uid, name, context)
        	self.localcontext.update({
        	    'time': time,
		    'texto': text.text,
		    'date_sp': text.date_sp,
		    'moneyfmt': text.moneyfmt,
		    'total_debit': self._total_debit,
		    'total_credit': self._total_credit,
		    'get_cheques': self._get_cheques,
        	})

	def _get_cheques(self, obj, data):
		chk_obj = self.pool.get('payment.cheque')
		res = []
		for cheque in data['cheque']:
			cheque_id = cheque[2] and chk_obj.browse(self.cr, self.uid, cheque[1])
			if cheque_id:
				res.append(cheque_id)
		return res

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

report_sxw.report_sxw('report.payment.cheque.entry', 'payment.cheque',
	'addons/bias_payment/report/print_entry.rml', parser=print_cheque, header=False)

report_sxw.report_sxw('report.payment.cheque.print_from_wizard_a', 'payment.cheque',
	'addons/bias_payment_wo_cc/report/print_cheque_from_wizard_a.rml', parser=print_cheque, header=False)



