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
from report  import report_sxw
import text
import pooler
from lxml import etree

class account_invoice(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(account_invoice, self).__init__(cr, uid, name, context)
		#user = self.pool.get('res.users').browse(cr, uid, uid)
		self.localcontext.update({
			'time': time,
                        'date_sp': text.date_sp,
                        'moneyfmt': text.moneyfmt,
                        'texto': text.text,
                        #'fix_space': text.fix_space,
			#'user': user,
			'get_impuestos': self._get_impuestos,
			'tipoDeComprobante': self._get_tipoDeComprobante,
			'cadena': self._get_cadena,
			#'give_me_space':self._give_me_space,
		})

	def _get_lines(self, txt):
		res = txt[:len(txt)/2] + ' ' + txt[len(txt)/2:]
		return res

	def _get_cadena(self, cadena):				
		rows = len(cadena)/120
		res = ''
		for rn in range(rows):
			res += cadena[200*rn:(200*(rn+1))] + '\n'
		return res

	def _get_tipoDeComprobante(self, inv_brw):
		if inv_brw.type == 'out_invoice':
			return 'Ingreso'
		elif  inv_brw.type == 'out_refund':
			return 'Egreso'
		elif inv_brw.company_id.partner_id.vat == inv_brw.partner_id.vat:
			return 'Traslado'
		return ''
	
	def _get_impuestos(self, invoice_obj):
		tax_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
		tax_xml = tax_obj.get_impuestos(self.cr, self.uid, invoice_obj.tax_line)
		res = []
		for tax_type in tax_xml:
			for tax in tax_type:
				res_dir = {}
				tax.values()
				if tax.get('impuesto'):
					if tax_type[0].tag in ('retain_iva', 'retain_isr'):
						res_dir['impuesto'] =  'Retencion' + ' ' + tax.get('impuesto')
					else:
						res_dir['impuesto'] =  'Traslado' + ' ' + tax.get('impuesto')
				else:
					res_dir['impuesto'] = ''
				if tax.get('importe'):
					res_dir['importe'] =  tax.get('importe')
				else:
					res_dir['importe'] =  ''
				if tax.get('tasa'):
					res_dir['tasa'] =  tax.get('tasa') + '%'
				else:
					res_dir['tasa'] = ''
				res.append(res_dir)
		return res

report_sxw.report_sxw('report.account.invoice.electronic2', 'account.invoice', 'addons/bias_electronic_invoice/report/invoice.rml', parser=account_invoice, header=False)

