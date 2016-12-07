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
import text
from report import report_sxw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

#from pychart import *

#x, y = (0, 0)

class external_pdf(render):
	def __init__(self, pdf):
		render.__init__(self)
		self.pdf = pdf
		self.output_type='pdf'
		
	def _render(self):
		return self.pdf

class report_custom(report_int):
	def create(self, cr, uid, ids, datas, context={}):
		print 'create'
		assert len(ids), 'You should provide some ids!'
		pdf_string = StringIO.StringIO()
		can = canvas.Canvas(pdf_string, pagesize=letter)
		pool = pooler.get_pool(cr.dbname)
		inv_obj = pool.get('account.invoice')
        	for inv in inv_obj.browse(cr, uid, ids):
       	        	can = self._create_pdf(cr, uid, inv, can, context)
        	can.save()
        	self.obj = external_pdf(pdf_string.getvalue())
        	self.obj.render()
        	pdf_string.close()
        	return (self.obj.pdf, 'pdf')

    	def _python_code(self, cr, uid, l, i):
		pool = pooler.get_pool(cr.dbname)
       		localdict = {'pool':pool, 'cr':cr, 'uid':uid, 'l':l, 'i':i}
       		exec l.python_compute in localdict
                res = localdict['result']
        	return res

    	def _create_pdf(self, cr, uid, inv, can, context={}):
       	    	lines = inv.journal_id.invoice_printing_id.line_id
       	    	adj_x = inv.journal_id.invoice_printing_id.adjustment_x or 0
       	    	adj_y = inv.journal_id.invoice_printing_id.adjustment_y or 0
		y = 0
       	    	for lin in lines:
			print 'lin=',lin
			if lin.ttype == 'one2many':
				for i in eval('inv.'+lin.field):
					y = y - lin.size * 1.2
					for l in lin.line_id:
						can.setFont(lin.font, lin.size)
						if l.method == 'code':
							res = self._python_code(cr, uid, l, i)
							can = self._write_pdf(cr, uid, res, lin.domain, i.id, can, l, l.field_name, adj_x, adj_y, y)
						else:
							data = self._get_data(cr, uid, lin.domain, i.id, l.field)#_name)
							can = self._write_pdf(cr, uid, data, lin.domain, i.id, can, l, l.field_name, adj_x, adj_y, y)
			else:
				can.setFont(lin.font, lin.size)
				data = self._get_data(cr, uid, 'account.invoice', inv.id, lin.field)
				can = self._write_pdf(cr, uid, data, 'account.invoice', inv.id, can, lin, lin.field, adj_x, adj_y, y)
       	    	can.showPage()
        	return can

    	def _get_data(self, cr, uid, domain, id, field_name):
		pool = pooler.get_pool(cr.dbname)
		br = "pool.get('"+domain+"').browse(cr, uid, "+str(id)+")."
		data = br + field_name
		return eval(data)

    	def _write_pdf(self, cr, uid, data, domain, id, can, lin, field_name, adj_x, adj_y, y):
		if not data:
			return can
		pool = pooler.get_pool(cr.dbname)
		plus = ''
		br = "pool.get('"+domain+"').browse(cr, uid, "+str(id)+")."
#        	data = br + field_name
        	if lin.method and lin.method == 'text.formatLang': 
        	    	data = lin.method+'(cr, uid, "'+data+'", False, True)'
			data = eval(data)
        	elif lin.method and lin.method == 'text.moneyfmt': 
			data = lin.method+'(str('+str('%.2f' % data)+'))'
			data = eval(data)
        	elif lin.method and lin.method == 'text.moneyfmt2': 
			data = 'text.moneyfmt'+'(str('+str('%.2f' % data)+'))'
			#data = str('%.2f' % data)'
			data = eval(data)
			data = str('%13.2f' % data)
        	elif lin.method and lin.method == 'text.text': 
        	    	currency = eval(br + 'currency_id')
        	    	data,plus = lin.method+'('+str(int(data))+')', ' '+currency.name+' '+('%.2f' % data)[-2:]+'/100 '+currency.code +')***'
			data = '***('+eval(data)
		data = str(data)
		can.drawString(adj_x+lin.x, adj_y+lin.y+y, data+plus)
        	return can

report_custom('report.invoice.printing')



