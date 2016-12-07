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
import pooler
from report import report_sxw
from report.report_sxw import rml_parse as rml_parse2
import text

class print_entries(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(print_entries, self).__init__(cr, uid, name, context)
		print 'entra al reporte entreis', context
		print 'name', name
		self.localcontext.update({
			'time': time,
                        'date_sp': text.date_sp,
                        'moneyfmt': text.moneyfmt,
                        'texto': text.text,
			'_sum_debit': self._sum_debit,
			'_sum_credit': self._sum_credit,
			'get_objects': self._get_objects,
		})
		print 'sale', context

	def _get_objects(self, obj):
		pool = pooler.get_pool(self.cr.dbname)
		for order_brw in obj:
			self.cr.execute("select move_id from payment_line where order_id = %s" % (order_brw.id))
			res  = []
			for x in self.cr.fetchall():
				if x[0] not in res:
					print 'x', x
					res.append(x[0])
			return self.pool.get('account.move').browse(self.cr, self.uid, res)
	
	def _sum_debit(self, obj):
		print 'entra a sum debit'
		res = 0
		for ll in obj.line_id:
			res += ll.debit
		return res

	def _sum_credit(self, obj):
		res = 0
		for ll in obj.line_id:
			res += ll.credit
		return res

		
report_sxw.report_sxw('report.payment.print.entries', 'payment.order', 'addons/bias_account/report/account_move.rml', parser=print_entries, header=False)

