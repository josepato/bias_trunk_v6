# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import pooler
from report import report_sxw
import text
import re

class order(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
        	super(order, self).__init__(cr, uid, name, context)
        	self.localcontext.update({
			'time': time,
			'texto': self._get_text,
			'moneyfmt': text.moneyfmt,
			'get_money_name': text.get_money_name,
			'comma_me': self.comma_me,
			'convert_value': self._convert_value,

        	})

	def _get_text(self, amount):
		return text.text(int(amount))
	
	def comma_me(self,amount):
		if not amount:
		    amount = 0.0
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

	def _convert_value(self, value, context={}):
		if not value:
			return ''
		if context.get('strip', False) and context.get('model', False):
			quitar=len(context['model'])+3
			value = value[quitar:]
			return value
		if context.get('money_format', False):
			return '$ ' + text.moneyfmt( '%.2f' % float(value))
		return value

report_sxw.report_sxw('report.sale.order.bias', 'sale.order', 'addons/bias_print_forms/sale/report/sale_order.rml', parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

