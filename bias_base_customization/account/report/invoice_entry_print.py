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
            'validate': self._validate,
            'state': self._state,
        })

    def _state(self, obj):
        res = 'Borrador'
        if obj.move_id.state == 'posted':
            res = 'Validado'
        return res

    def _validate(self, obj):
        invoice = self.pool.get('account.invoice').validate(obj)
        return invoice

    def _sum_debit(self, obj):
        res = 0
        for ll in obj.move_id.line_id:
            res += ll.debit
        return res

    def _sum_credit(self, obj):
        res = 0
        for ll in obj.move_id.line_id:
            res += ll.credit
        return res
		
report_sxw.report_sxw('report.invoice.entry.print.bias', 'account.invoice', 'addons/bias_customization/account/report/invoice.entry.print.rml', parser=account_move, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
