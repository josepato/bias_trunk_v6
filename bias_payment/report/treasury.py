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
import datetime
from report import report_sxw
import re

class report_treasury(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_treasury, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
			'comma_me': self.comma_me,
        })

    def comma_me(self,amount):
        if  type(amount) is float :
            amount = str('%.2f'%amount)
        else:
            amount = str(amount)
        if (amount == '0'):
            return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>,\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

report_sxw.report_sxw('report.treasury', 'account.treasury', 'addons/bias_payment/report/treasury.rml', parser=report_treasury, header=True)
report_sxw.report_sxw('report.global.treasury', 'account.global.treasury', 'addons/bias_payment/report/treasury.rml', parser=report_treasury, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
