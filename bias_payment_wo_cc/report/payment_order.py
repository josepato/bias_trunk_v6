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

class payment_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payment_order, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'get_partners': self._get_partners,
            'get_line': self._get_line,
            'get_entry': self._get_entry,
            'get_partial': self._get_partial,
            'get_partner_total': self._get_partner_total,
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

    def _get_partner_total(self, payment, partner):
        self.cr.execute("select sum(calc_amount ) from payment_line " \
                        "where order_id = %s and partner_id = %s " , (payment.id, partner.id))
        res = self.cr.fetchone()[0]
        return res

    def _get_entry(self, payment, partner):
        self.cr.execute("select distinct(m.name) from payment_line l, account_move m where l.order_id = %s and l.partner_id = %s and l.move_id = m.id" , (payment.id, partner.id))
        res = ', '.join(map(str, [x[0] for x in self.cr.fetchall()]))
        return str(res)

    def _get_partners(self, payment):
        part_obj = self.pool.get('res.partner')
        self.cr.execute("select distinct(l.partner_id), m.name from payment_line l, account_move m  " \
                        "where order_id = %s and l.move_id = m.id order by m.name " , (payment.id,))
        res = part_obj.browse(self.cr, self.uid, [x[0] for x in self.cr.fetchall()])
        return res

    def _get_line(self, payment, partner):
        pay_obj = self.pool.get('payment.line')
        self.cr.execute("select id from payment_line where order_id = %s and partner_id = %s" , (payment.id, partner.id))
        res = [x[0] for x in self.cr.fetchall()]
        res = pay_obj.browse(self.cr, self.uid, res)
        return res

    def _get_partial(self, line):
        return line.partial and 'Parcial' or ''

report_sxw.report_sxw('report.payment.order.bias', 'payment.order', 'addons/bias_payment_wo_cc/report/order.rml', parser=payment_order, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
