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
import text


class custom_refound(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(custom_refound, self).__init__(cr, uid, name, context)
        self.sum_subtotal = 0.00
        self.sum_deductions = 0.00
        self.localcontext.update({
			'time': time,
            'date_sp': text.date_sp,
            'moneyfmt': text.moneyfmt,
            'texto': text.text,
            'get_lines': self._get_lines,
            'get_deductions': self._get_deductions,
            'get_subtotal': self._get_sum_subtotal,
            'get_sum_deductions': self._get_sum_deductions,
            'deductions': self._deductions,
        })

    def _get_sum_subtotal(self):
        return self.sum_subtotal

    def _get_sum_deductions(self):
        return self.sum_deductions

    def _get_lines(self, obj):
        res = []
        for line in obj.invoice_line:
            if not line.deduction:
                res.append(line)
                self.sum_subtotal += line.price_subtotal
        return res

    def _get_deductions(self, obj):
        res = []
        for line in obj.invoice_line:
            if line.deduction:
                res.append(line)
                self.sum_deductions += line.price_subtotal
        return res

    def _deductions(self, obj):
        res = False
        for line in obj.invoice_line:
            if line.deduction:
                res = True
        return res

report_sxw.report_sxw('report.account.custom.refound.bias', 'account.invoice', 'addons/bias_customization/account/report/custom_refound.rml', parser=custom_refound, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
