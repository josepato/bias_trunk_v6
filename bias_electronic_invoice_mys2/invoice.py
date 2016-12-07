# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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

from osv import fields, osv
import time
from mx.DateTime import *
import tools
import SOAPpy
import re
import StringIO
from lxml import etree
import base64
from lxml.builder import ElementMaker
import codecs
#import text

class account_invoice(osv.osv):
	_name = "account.invoice"
	_inherit = 'account.invoice'
	_description = 'Invoice'


	_columns = {
		'sign_date':fields.datetime('Sing Date'),
		'approve_year':fields.integer('Approve Year'),
		'approve_number':fields.integer('Approve Number'),
		'certificate': fields.text('Certificate'),
		'digital_signature': fields.text('Signature'),
		'provider_signature':  fields.text('Signature Provider'),
		#'invoice_xml':fields.text('Invoice_Xml'),
		}

	def test_open(self, cr, uid, ids, *args):
		super(account_invoice, self).action_date_assign( cr, uid, ids, *args)
		super(account_invoice, self).action_move_create( cr, uid, ids, *args)
		super(account_invoice, self).action_number( cr, uid, ids, *args)
		for inv_id in ids:
			cfe = self.create_xml(cr, uid, [inv_id], *args)
			cfe_str = etree.tostring(cfe, pretty_print=True)
			util = SOAPpy.WSDL.Proxy("CorporativoWS2.2.wsdl")
			#util = SOAPpy.WSDL.Proxy("demobuzonfiscal.wsdl")
			new_cfe  = util.GeneraCFD(cfe_str)
			response_r = open('/tmp/response.xml', 'r')
			response = response_r.read()
			tree = etree.parse(codecs.open('/tmp/response.xml', 'r', 'utf-8'))
			root = tree.getroot()
			try:
				folio = root[0][0][0].attrib['folio']
			except:
				raise osv.except_osv(('Error al crear factura!'),("Error al crear factura !") )
			self.write(cr, uid, inv_id, {'number':int(folio)})
			self.attach_xml(cr, uid, inv_id, response)
		return True

	def attach_xml(self, cr, uid, id, cfe):
		inv_brw = self.browse(cr, uid, id)
		self.pool.get('ir.attachment').create(cr, uid, {
                            'name': 'Fact.-' + inv_brw.number,
                            'datas': base64.encodestring(cfe),
                            'datas_fname': inv_brw.number + '.xml',
                            'res_model': self._name,
                            'res_id': inv_brw.id,
                            }, )
		return True
						   

	
	
	def create_xml(self,cr, uid, ids, *args):
		
		E = ElementMaker(namespace="http://www.buzonfiscal.com/ns/xsd/bf/remision/4", 
				 nsmap={
					 'ns':"http://www.buzonfiscal.com/ns/xsd/bf/remision/4", 
					 'ns2':"http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2", 
					 'ns1':"http://www.buzonfiscal.com/ns/addenda/bf/2"},)
		
		for inv_brw in self.browse(cr, uid, ids):
			CFD = self.get_remision(cr, uid, inv_brw,E)
		return CFD

	def get_remision(self, cr, uid, inv_brw, E):
		E2 = ElementMaker(namespace="http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2", 
				 nsmap={
					 'ns':"http://www.buzonfiscal.com/ns/xsd/bf/remision/4", 
					 'ns2':"http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2", 
					 'ns1':"http://www.buzonfiscal.com/ns/addenda/bf/2"},)
		DOC = E2.RequestGeneraCFD
		TITLE = E.Remision
		title = TITLE({'version':'4.0'})
		INFOBASICA = E.InfoBasica
		INFOADICIONAL = E.InfoAdicional
		EMISOR = E.Emisor
		DOMICILIOFISCAL = E.DomicilioFiscal
		RECEPTOR = E.Receptor
		DOMICILIO_RECEPTOR = E.DomicilioReceptor
		CONCEPTOS = E.Conceptos
		CONCEPTO = E.Concepto
		concepto = CONCEPTOS()
		IMPUESTOS = E.Impuestos
		TRASLADOS = E.Traslados
		TRASLADO = E.Traslado
		traslado = TRASLADOS()
		RETENCIONES = E.Retenciones
		RETENCION = E.Retencion
		retencion = RETENCIONES()
		Impuestos_complex = self.get_complex_tax(cr, uid, inv_brw.tax_line, IMPUESTOS , TRASLADO, traslado , RETENCION, retencion,)
		cfd = DOC(TITLE({'version':'4.0'},
			INFOBASICA(self.get_info_basica(cr, uid, inv_brw)),
			INFOADICIONAL(self.get_info_adicional(cr, uid, inv_brw)),
			EMISOR(self.get_emisor(cr, uid, inv_brw)),
			DOMICILIOFISCAL(self.get_emision_domicilo_Fiscal(cr, uid, inv_brw)),
			RECEPTOR(self.get_receptor(cr, uid, inv_brw)),
			DOMICILIO_RECEPTOR(self.get_domicilio_receptor(cr, uid, inv_brw)),
			self.get_conceptos(cr, uid, inv_brw.invoice_line, CONCEPTO, concepto),
			Impuestos_complex
				))
			
		return cfd

	def get_info_basica(self, cr, uid, inv_brw):
		res = {}
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_brw = inv_brw.company_id.partner_id
		if not partner_brw.vat:
			raise osv.except_osv(('No RFC Defined on Emisor Partner!'),("You must define a RFC for the company !") )
		res['rfcEmisor'] = re.sub('-','',partner_brw.vat)
		###Receptor
		partner_brw = inv_brw.partner_id
		if not partner_brw.vat:
			raise osv.except_osv(('No RFC Defined on Receptor Partner!'),("You must define a RFC for the Client !") )
		res['rfcReceptor'] = re.sub('-','',partner_brw.vat)
		res['rfcReceptor'] = re.sub('\ ','',res['rfcReceptor'])
		res['serie'] = "A"
		return res

	def get_info_adicional(self, cr, uid, inv_brw):
		res = {}
		res['formaDePago'] = "PAGO EN UNA SOLA EXHIBICION"
		if not inv_brw.payment_term.name:
			raise osv.except_osv(('No payment term defined!'),("No payment term defined !") )
		res['condicionesDePago'] = inv_brw.payment_term.name
		res['subTotal'] = str(inv_brw.amount_untaxed)
		res['total'] = str(inv_brw.amount_total)
		if inv_brw.type == 'out_invoice':
			res['tipoDeComprobante'] = 'ingreso'
		elif inv_brw.type == 'out_refund':
			res['tipoDeComprobante'] = 'traslado'
		return res
	
	def get_emisor(self, cr, uid, inv_brw):
		res = {}
		res['nombre'] = inv_brw.company_id.name
		return res

	def get_emision_domicilo_Fiscal(self, cr, uid, inv_brw):
		res = {}
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_brw = inv_brw.partner_id
		partner_id = inv_brw.partner_id.id
		inovice_addres_id = partner_obj.address_get(cr, uid, [partner_id], ['invoice'])
		address_brw = address_obj.browse(cr, uid, inovice_addres_id['invoice'])
		res['codigoPostal'] = address_brw.zip 
		res['pais'] = address_brw.country_id.name 
		res['estado'] = address_brw.state_id.name
		res['colonia'] =address_brw.street2
		res['calle'] = address_brw.street
		res['municipio'] = address_brw.city
 		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_brw = inv_brw.company_id.partner_id
		partner_id = inv_brw.company_id.partner_id.id
		inovice_addres_id = partner_obj.address_get(cr, uid, [partner_id], ['invoice'])
		address_brw = address_obj.browse(cr, uid, inovice_addres_id['invoice'])
		res['codigoPostal'] = address_brw.zip 
		res['pais'] = address_brw.country_id.name 
		res['estado'] = address_brw.state_id.name
		res['colonia'] =address_brw.street2
		res['calle'] = address_brw.street
		res['municipio'] = address_brw.city
		return res

	def get_receptor(self, cr, uid, inv_brw):
		res = {}
		res['nombre'] = inv_brw.partner_id.name
		return res
	
	def get_domicilio_receptor(self, cr, uid, inv_brw):
		res = {}
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_brw = inv_brw.partner_id
		partner_id = inv_brw.partner_id.id
		inovice_addres_id = partner_obj.address_get(cr, uid, [partner_id], ['invoice'])
		address_brw = address_obj.browse(cr, uid, inovice_addres_id['invoice'])
		res['calle'] = address_brw.street or ''
		res['colonia'] = address_brw.street2 or ''
		res['codigoPostal'] = address_brw.zip or ''
		res['pais'] = address_brw.country_id.name or ''
		res['estado'] = address_brw.state_id.name or ''
		res['localidad'] = address_brw.city or ''
		return res

	def get_conceptos(self, cr, uid, lines_brw_lst, CONCEPTO, concepto):
		for line in lines_brw_lst:
			res = {}
			res['cantidad'] =  str(line.quantity)

			res['descripcion'] = line.name
			res['valorUnitario'] =str(line.price_unit)
			res['importe'] =str(line.price_subtotal)
			uos = line.uos_id.name
			if uos:
				res['unidad'] = uos
			concepto.append(CONCEPTO(res))
		return concepto



	def get_tax(self, cr, uid, tax, tax_type):
		res = {}
		if tax_type == 'retain_iva':
			res['impuesto'] ='IVA'
			res['importe'] = '%.2f'%(tax.amount)
		elif tax_type == 'retain_isr':
			res['impuesto']= 'ISR'
			res['importe'] = '%.2f'%(tax.amount)
		if tax_type == 'tax_ieps':
			res['impuesto'] = 'IEPS'
			res['tasa'] = '%.2f'%(tax.amount / tax.base * 100)
			res['importe'] = '%.2f'%(tax.amount)
		elif tax_type == 'tax_iva':
			res['impuesto'] = 'IVA'
			res['tasa'] = '%.2f'%(tax.amount / tax.base * 100)
			res['importe'] = '%.2f'%(tax.amount)
		return res



	def get_traslados(self, cr, uid, tax_line, VAR_IMPUESTO, var_impuesto, t_type):
		for tax in tax_line:
			res = {}
			tax_type = tax.tax_code_id.code
			if ((tax_type == 'retain_iva') or (tax_type == 'retain_isr')) and (t_type == 'retencion'):
				var_impuesto.append(VAR_IMPUESTO(self.get_tax(cr, uid, tax, t_type)))
			elif ((tax_type == 'tax_iva') or (tax_type == 'tax_ieps')) and (t_type == 'traslado'):
				var_impuesto.append(VAR_IMPUESTO(self.get_tax(cr, uid, tax, tax_type)))
		return var_impuesto

	def get_complex_tax(self, cr, uid, tax_line, IMPUESTOS, TRASLADO, traslado,  RETENCION, retencion):
		tax_type = []
		for tax in tax_line:
			tax_type.append(tax.tax_code_id.code)
		if (('retain_iva' in tax_type) or ('retain_isr' in tax_type)) and (('tax_iva' in tax_type) or ( 'tax_ieps' in tax_type)):
			return IMPUESTOS(self.get_total_impuestos(cr, uid, tax_line),
				  self.get_traslados(cr, uid, tax_line, TRASLADO, traslado, 'traslado'),
				  self.get_traslados(cr, uid, tax_line, RETENCION, retencion, 'retencion')
				  )
		elif ( 'retain_iva' in tax_type) or ( 'retain_isr' in tax_type):
			return IMPUESTOS(self.get_total_impuestos(cr, uid, tax_line),
				  self.get_traslados(cr, uid, tax_line, RETENCION, retencion, 'retencion')
				  )
		elif ( 'tax_iva' in tax_type) or ( 'tax_ieps' in tax_type):
			return IMPUESTOS(self.get_total_impuestos(cr, uid, tax_line),
				  self.get_traslados(cr, uid, tax_line, TRASLADO, traslado, 'traslado'),
				  )
		return IMPUESTOS

	def get_total_impuestos(self, cr, uid, tax_line):
		total_retenciones = 0
		total_traslados = 0 
		res = {}
		for tax in tax_line:
			tax_type = tax.tax_code_id.code
			if (tax_type == 'retain_iva') or (tax_type == 'retain_isr'):
				total_retenciones += tax.amount
			elif (tax_type == 'tax_iva') or (tax_type == 'tax_ieps'):
				total_traslados += tax.amount
		if total_retenciones:
			res['totalImpuestosRetenidos'] = '%.2f'%(total_retenciones)
		if total_traslados:
			res['totalImpuestosTrasladados'] = '%.2f'%(total_traslados)
		return res



	def get_discount(self, cr, uid, inv_brw):
		return 0

	def get_payment_form(self, cr, uid, inv_brw):
		return False



	def action_cancel(self, cr, uid, ids, *args):
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		for inv_brw in self.browse(cr, uid, ids):
			if inv_brw.type in ('out_invoice','out_refund'):
				partner_brw = inv_brw.company_id.partner_id
				if not partner_brw.vat:
					raise osv.except_osv(_('No RFC Defined on Emisor Partner!'),_("You must define a RFC for the company !") )
				rfc = re.sub('-','',partner_brw.vat)
				###Receptor
				partner_brw = inv_brw.partner_id
				if not partner_brw.vat:
					raise osv.except_osv(('No RFC Defined on Receptor Partner!'),("You must define a RFC for the Client !") )
				rfcReceptor = re.sub('-','',partner_brw.vat)
				rfcReceptor = re.sub('\ ','',rfcReceptor)
				serie = 'A'
				folio = inv_brw.number
				cfe = etree.Element('RequestCancelaCFD')
				cfe.set('xmlns',"http://www.buzonfiscal.com/ns/xsd/bf/bfcorp/2")
				cfe.set('rfcEmisor', rfc)
				cfe.set('rfcReceptor',rfcReceptor)
				cfe.set('serie','A')
				cfe.set('folio', folio)
				cfe.set('refID',"73102746002024")
				cfe_xml = etree.tostring(cfe)
				cfe_xml = '<?xml version="1.0" encoding="UTF-8"?>' + cfe_xml
				util = SOAPpy.WSDL.Proxy("CorporativoWS2.2.wsdl")
				cancelar = util.CancelaCFD(cfe_xml)
				super(account_invoice, self).action_cancel( cr, uid, [inv_brw.id], *args)
				print 'cancelar',cancelar
		return cancelar

	def action_cancel_draft(self, cr, uid, ids, *args):
		for inv_brw in self.browse(cr, uid, ids):
			if inv_brw.type in ('out_invoice','out_refund'):
				raise osv.except_osv(('Warning!'),("You can not send to draft this kind of documents !") )
		super(account_invoice, self).action_cancel_draft( cr, uid, [inv_brw.id], *args)
		return True

account_invoice()



class account_invoice_adenda(osv.osv):
    _name = "account.invoice.adenda"
    _description = "Adenda for the Electronic Invoice"
    _columns = {
        'name': fields.char('Adenda', size=64, required=True),
        'active': fields.boolean('Active'),
        'note': fields.text('Description', translate=True),
        'line_ids': fields.one2many('account.invoice.adenda.lines', 'adenda_id', 'Terms'),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
    _order = "name"


account_invoice_adenda()

class account_invoice_adenda_lines(osv.osv):
    _name = "account.invoice.adenda.lines"
    _description = "Lines of the Electronic Invoice Adenda"

    def _col_get(self, cr, user, context={}):
        result = []
        cols = self.pool.get('account.invoice')._columns
        for col in cols:
            result.append( (col, cols[col].string) )
        result.sort()
        return result

    
    _columns = {
	    'name': fields.char('Field Name', size=64, required=True),
	    'code': fields.char('Code', size=64, required=True),
	    'sequence': fields.integer('Sequence', required=True, help="The sequence field is used to order fields"),
	    'required': fields.boolean('Required'),
	    'relation': fields.many2one('ir.model', 'Relation'),
	    'default': fields.char('Default', size=64),
	    'field': fields.selection(_col_get, 'Field Name', method=True, size=64),
	    'adenda_id': fields.many2one('account.invoice.adenda', 'Adenda', required=True, select=True),
	    }
    _defaults = {
        'sequence': lambda *a: 5,

    }
    _order = "sequence"

account_invoice_adenda_lines()



