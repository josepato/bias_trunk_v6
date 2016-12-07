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
import re


class account_invoice(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(account_invoice, self).__init__(cr, uid, name, context)
		user = self.pool.get('res.users').browse(cr, uid, uid)
		self.localcontext.update({
			'time': time,
                        'date_sp': text.date_sp,
                        'moneyfmt': text.moneyfmt,
                        'texto': self._get_text,
			'get_money_name': text.get_money_name,
                        #'fix_space': text.fix_space,
			'user': user,
			'get_impuestos':self._get_impuestos,
			'tipoDeComprobante': self._get_tipoDeComprobante,
			'leyendaTipoDeCambio': self._get_leyendaTipoDeCambio,
			'leyenda':self._get_leyenda_UDS,
			'leyenda_pitex':self._get_leyenda_pitex,
			'cadena':self._get_cadena,
			'get_nopartidas': self._get_nopartidas,
			'get_lineas_partidas': self._get_lineas_partidas,
			'get_total_products': self._get_total_products,
			'convert_value': self._convert_value,
			#'give_me_space':self._give_me_space,
		})

	def _get_lines(self, txt):
		res = txt[:len(txt)/2] + ' ' + txt[len(txt)/2:]
		return res

	def _get_text(self, amount):
		return text.text(int(amount))

	def _get_cadena(self, cadena):
		rows = len(cadena)/120
		res = ''
		for rn in range(rows):
			res += cadena[200*rn:(200*(rn+1))] + '\n'
		return res

	def _get_leyenda_UDS(self, obj):
		if obj.currency_id.code == 'USD':
			return 'LA PRESENTE FACTURA SE SOLVENTARA ENTREGADO EL EQUIVALENTE EN MONEDA NACIONAL, AL TIPO DE CAMBIO QUE EL BANCO DE MEXICO PUBLIQUE EN EL DIARIO OFICIAL DE LA FEDERACION, EL DIA HABIL BANCARIO INMEDIATO ANTERIOR A AQUEL EN QUE SE EFECTUE EL PAGO'
		else:
			return ''

	def _get_leyenda_pitex(self, obj):
		if obj.partner_id.property_account_position.name == 'RETENEDOR DEL IVA':
			return 'Impuesto retenido de conformidad con la Ley del Impuesto al Valor Agregado'
		else:
			return ''


	def _get_tipoDeComprobante(self, inv_brw):
		if inv_brw.type == 'out_invoice':
			return 'Ingreso'
		elif  inv_brw.type == 'out_refund':
			return 'Egreso'
		elif inv_brw.company_id.partner_id.vat == inv_brw.partner_id.vat:
			return 'Traslado'
		return ''



	def _get_leyendaTipoDeCambio(self, inv_brw):
		if inv_brw.currency_id.code == 'USD':
			return 'La presente factura se solventara entregado el equivalente en moneda nacional, al tipo de cambio que el Banco de Mexico publique en el Diario Oficial de la Federacion, el dia habil bancario inmediato anterior a aquel en que se efectue el pago'
		else:
			return 'abc'


	
	def _get_impuestos(self, invoice_obj):
		tax_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
		tax_xml = tax_obj.get_impuestos(self.cr, self.uid, invoice_obj.tax_line)
		res = []
		for tax_type in tax_xml:
			for tax in tax_type:
				res_dir = {}
				tax.values()
				if tax.get('impuesto'):
					res_dir['impuesto'] =  tax_type[0].tag + ' ' + tax.get('impuesto')
				else:
					res_dir['impuesto'] = ''
				if tax.get('importe'):
					res_dir['importe'] =  '$ ' +   text.moneyfmt('%.2f' % float(tax.get('importe')))
				else:
					res_dir['importe'] =  ''
				if tax.get('tasa'):
					res_dir['tasa'] =  tax.get('tasa') + '%'
				else:
					res_dir['tasa'] = ''
				res.append(res_dir)
		if not res:
			res_dir ={'impuesto':'', 'importe':'', 'tasa':''}
			res.append(res_dir)
		return res

##	def _get_impuestos(self, invoice_obj):
##		tax_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
##		tax_xml = tax_obj.get_impuestos(self.cr, self.uid, invoice_obj.tax_line)
##		res = []
##		for tax_type in tax_xml:
##			for tax in tax_type:
##				res_dir = {}
##				if tax.get('impuesto'):
##					res_dir['impuesto'] =  tax_type[0].tag + ' ' + tax.get('impuesto')
##				else:
##					res_dir['impuesto'] = ''
##				if tax.get('importe'):
##					res_dir['importe'] =  tax.get('importe')
##				else:
##					res_dir['importe'] =  ''
##				if tax.get('tasa'):
##					res_dir['tasa'] =  tax.get('tasa') + '%'
##				else:
##					res_dir['tasa'] = ''
##				res.append(res_dir)
##		return res
	
	def _get_nopartidas(self, invoice_obj):
		query = "SELECT count(id) FROM account_invoice_line WHERE invoice_id=%s"%(invoice_obj.id)
		self.cr.execute(query)
		res = self.cr.fetchone()
		if res:
			res=res[0]
		return res


	def _get_lineas_partidas(self, invoice_obj):
		query2 = "SELECT a.quantity, a.name, a.price_unit, a.discount, a.price_subtotal, p.default_code, a.note FROM account_invoice_line a, product_product p WHERE invoice_id=%s and a.product_id = p.id order by name"%(invoice_obj.id)
		self.cr.execute(query2)
		res = self.cr.dictfetchall()
		count =0
		total_discount = 0
		for rr in res:
			count +=1 
			rr.update({'renglon':count})
			if rr['discount']:
				rr.update({'discount':str(rr['discount']) +'%'})

		return res

	def _get_total_products(self, invoice_obj):
		totales = "SELECT SUM(quantity) FROM account_invoice_line WHERE invoice_id=%s"%(invoice_obj.id)
		self.cr.execute(totales)
		res = self.cr.fetchone()
		if res:
			res=res[0]
		return text.moneyfmt( '%.2f' % float(res))

	def _convert_value(self, value, context={}):
		if not value:
			return ''
		if context.get('strip', False) and context.get('model', False):
			quitar=len(context['model'])+3
			value = value[quitar:]
			return value
		if context.get('currency', False):	
			if value == 'USD':	
				return 'EL VALOR DE ESTA FACTURA ESTA EN USD'
			else:
				return ''
		if context.get('money_format', False):
			return '$ ' + text.moneyfmt( '%.2f' % float(value))
		if context.get('re', False):
			return re.sub(',',"",str(value))
		if context.get('vat_fmt', False):
			return re.sub('[-. |*]',"",str(value)).upper()
		return value



report_sxw.report_sxw('report.account.invoice.electronic', 'account.invoice', 'addons/bias_electronic_invoice_v6/report/invoice_b.rml', parser=account_invoice, header=False)

