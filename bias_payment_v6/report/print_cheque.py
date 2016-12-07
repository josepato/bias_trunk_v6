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

import ir
import os, time
import netsvc

import random
import StringIO

import tools
import pooler

from report.render import render 
from report.interface import report_int
from pychart import *
import text
from report import report_sxw

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

#theme.use_color = 1
#theme.scale = 2
#random.seed(0)
#x, y = (100, 129)
x, y = (0, 0)

class external_pdf(render):
	def __init__(self, pdf):
		render.__init__(self)
		self.pdf = pdf
		self.output_type='pdf'
		
	def _render(self):
		return self.pdf

class report_custom(report_int):
	def create(self, cr, uid, ids, datas, context={}):
		assert len(ids), 'You should provide some ids!'
		pdf_string = StringIO.StringIO()
		can = canvas.Canvas(pdf_string, pagesize=letter)
		global x, y

		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		rep_chk_obj = pool.get('report.cheque')
		for chk in chk_obj.browse(cr, uid, ids):
			lines = chk.mode.report_cheque_id.line_id
			adj_x = chk.mode.report_cheque_id.adjustment_x or 0
			adj_y = chk.mode.report_cheque_id.adjustment_y or 0
            		for lin in lines:
				can.setFont(lin.font, lin.size)
               			data, plus = 'chk.'+lin.field_id.name, ''
				if type(eval(data)) == type(lin):
					data = data+'.name'
				if lin.method and lin.method == 'text.formatLang': 
				    data = lin.method+'(cr, uid, "'+eval(data)+'", False, True)'
                		if lin.method and lin.method == 'text.moneyfmt': 
				    data = lin.method+'(str('+str('%.2f' % eval(data))+'))'
                		if lin.method and lin.method == 'text.text': 
				    currency = (chk.mode.journal.currency or chk.mode.journal.default_debit_account_id.company_id.currency_id)
				    data, plus = lin.method+'('+str(int(eval(data)))+')', ' '+currency.name+' '+('%.2f' % eval(data))[-2:]+font.quotemeta('/100 ')+currency.name
				can.drawString(x+adj_x+lin.x, y+adj_y+lin.y, eval(data)+plus)
		can.showPage()
        	can.save()
        	self.obj = external_pdf(pdf_string.getvalue())
        	self.obj.render()
        	pdf_string.close()
        	return (self.obj.pdf, 'pdf')

report_custom('report.payment.cheque.print')



