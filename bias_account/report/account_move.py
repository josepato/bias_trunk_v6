##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw
from report.report_sxw import rml_parse as rml_parse2
import text

class account_move(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(account_move, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
                        'date_sp': text.date_sp,
                        'moneyfmt': text.moneyfmt,
                        'texto': text.text,
			'_sum_debit': self._sum_debit,
			'_sum_credit': self._sum_credit,
			'get_state': self._get_state,
			'get_type': self._get_type,
		})

	def _get_type(self, move_type):
		if move_type == 'pay_voucher':
			res = 'Poliza de Egreso de Efectivo'
		if move_type == 'bank_pay_voucher':
			res = 'Poliza de Egreso Bancario'
		if move_type == 'rec_voucher':
			res = 'Poliza de Ingreso de Efectivo'
		if move_type == 'bank_rec_voucher':
			res = 'Poliza Ingreso Bancario'
		if move_type == 'cont_voucher':
			res = 'Contra'
		if move_type == 'journal_sale_vou':
			res = 'Poliza de Ventas'
		if move_type == 'journal_pur_voucher':
			res = 'Poliza de Compras'
		if move_type == 'journal_voucher':
			res = 'Poliza de Diario'
		return res

	def _get_state(self, state):
		res = 'Borrador'
		if state == 'posted':
			res = 'Validado'
		return res

	def _sum_debit(self, obj):
		res = 0
		for ll in obj.line_id:
			res += ll.debit
		return res

	def _sum_credit(self, obj):
		res = 0
		for ll in obj.line_id:
			res += ll.credit
		return res

report_sxw.report_sxw('report.account.move.print', 'account.move', 'addons/bias_account/report/account_move.rml', parser=account_move, header=False)

