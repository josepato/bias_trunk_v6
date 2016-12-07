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
import codecs, cfdutil
import os


#import text

class account_invoice(osv.osv):
	_name = "account.invoice"
	_inherit = 'account.invoice'
	_description = 'Invoice'


	_columns = {
		'sign_date':fields.datetime('Sing Date'),
		'cancel_date':fields.datetime('Cancel Date'),
		'approved_year':fields.integer('Approved Year'),
	        'approved_number': fields.char('Approved Number', size=32),
		'certificate': fields.text('Certificate'),
		'digital_signature': fields.text('Signature'),
		'cadena':fields.text('Cadena')
		#'provider_signature':  fields.text('Signature Provider'),
		#'invoice_xml':fields.text('Invoice_Xml'),
		}


	def copy(self, cr, uid, id, default=None, context=None):
		if default is None:
			default = {}
		default = default.copy()
		default.update({'state':'draft', 'number':False, 'move_id':False, 'move_name':False, 'cancel_date':False, 'sign_date':False, 
			'approved_year':False, 'approved_number':False, 'certificate':False, 'digital_signature':False, 'cadena':False, 'period_id':False})
		if 'date_invoice' not in default:
			default['date_invoice'] = time.strftime('%Y-%m-%d')
		if 'date_due' not in default:
			default['date_due'] = False
		if 'cancel_date' not in default:
			default['cancel_date'] = False
		return super(account_invoice, self).copy(cr, uid, id, default, context)

	def cfdutil_getLineaReporte(self, xml_str_obj, state='False'):
		return cfdutil.getLineaReporte(xml_str_obj, state)

	
	def cfdutil_verifySello(self, cadena, certfname, sello):
		return cfdutil.verifySello(cadena, certfname, sello)

	def elimante_double_space(self, data):
		data = re.sub('[ \t\n\r\f\v]', ' ',data)
		data = data.strip(' ')
		while '  ' in data:
			data = re.sub('  ', ' ', data)
		return data

	def make_utf(self, data, required=''):
		if not data and required:
			raise osv.except_osv(('Error !'), ('Campo %s es Requerido y esta faltando en la captura.'%(required,)))
		elif data and required:
			
			return unicode(self.elimante_double_space(data), 'utf-8')
		elif data:
			return unicode(self.elimante_double_space(data), 'utf-8')
		else:
			return ''

	def _period_get(self, cr, uid, ctx={}):
		try:
			ids = self.pool.get('account.period').find(cr, uid, context=ctx)
			return ids[0]
		except:
			return False
		
	def action_cancel(self, cr, uid, ids, *args):
		account_move_obj = self.pool.get('account.move')
		invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids', 'id'])
		for i in invoices:
			if i['payment_ids']:
				account_move_line_obj = self.pool.get('account.move.line')
				pay_ids = account_move_line_obj.browse(cr, uid , i['payment_ids'])
				for move_line in pay_ids:
				    if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
					raise osv.except_osv(_('Error !'), _('You cannot cancel the Invoice which is Partially Paid! You need to unreconcile concerned payment entries!'))
			if i['move_id']:
				reconcile_obj = self.pool.get('account.move.reconcile')
				line_obj = self.pool.get('account.move.line')
				move_obj = self.pool.get('account.move')
				date = time.strftime('%Y-%m-%d')
				period = self._period_get(cr, uid)
				inv = self.browse(cr, uid, i['id'])
				if inv.state in ['draft', 'proforma2', 'cancel']:
					raise wizard.except_wizard(_('Error !'), _('Can not cancel draft/proforma/cancel invoice.'))
				if inv.type == 'in_invoice':
					description = 'Fac. '+inv.reference+' Cancelada'
				elif inv.type == 'out_invoice':
					description = 'Fac. '+inv.number+' Cancelada'
				else:
					description = 'Fac. '+inv.number+' Cancelada'
				if not period:
					raise wizard.except_wizard(_('Data Insufficient !'), _('No Period found on Invoice!'))
				default={'date':date, 'period_id':period, 'ref':description , 'state':'draft', 'name':'/',}
				move_obj.button_cancel(cr, uid, [inv.move_id.id,])
				move_id = move_obj.copy(cr, uid, inv.move_id.id, context={}, default={'date':date, 'period_id':period, 'ref':description })
				move_obj.post(cr, uid,  [inv.move_id.id,])
				move = move_obj.browse(cr, uid, move_id)
				move_obj.write(cr, uid, [move_id], {'date':date})
				for line in move.line_id:
					line_obj.write(cr, uid, [line.id], {
						'debit': line.credit,
						'credit': line.debit,
						'amount_currency': line.amount_currency and -line.amount_currency or False,
						'date':date
						}, context={'multireconcile':True})

				    #move_obj.post(self, cr, uid, [move_id])
				move_obj.post(cr, uid, [move_id])
				#if inv is paid we unreconcile
                                movelines = inv.move_id.line_id
                                #we unreconcile the lines
                                to_reconcile_ids = {}
                                for line in movelines :
                                    #if the account of the line is the as the one in the invoice
                                    #we reconcile
                                    if line.account_id.id == inv.account_id.id :
                                        to_reconcile_ids[line.account_id.id] =[line.id]
                                    if type(line.reconcile_id) != osv.orm.browse_null :
                                        reconcile_obj.unlink(cr,uid, line.reconcile_id.id)

                                #we match the line to reconcile
                                for tmpline in move.line_id :
                                    if tmpline.account_id.id == inv.account_id.id :
                                        to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                                for account in to_reconcile_ids :
                                    line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                        type = 'simple',
                                        writeoff_period_id=period,
                                        writeoff_journal_id=inv.journal_id.id,
                                        writeoff_acc_id=inv.account_id.id
                                    )
                                date_time = now().Format('%Y-%m-%d %H:%M:%S')
                                self.write(cr, uid, inv.id, {'cancel_date':date_time, 'state':'cancel'})
                                #Original
                                #account_move_obj.button_cancel(cr, uid, [i['move_id'][0]])
                                # delete the move this invoice was pointing to
                                # Note that the corresponding move_lines and move_reconciles
                                # will be automatically deleted too
                                #account_move_obj.unlink(cr, uid, [i['move_id'][0]])


                                self.write(cr, uid, ids, {'state':'cancel'})
                                self._log_event(cr, uid, ids,-1.0, 'Cancel Invoice')
                                date_time = now().Format('%Y-%m-%d %H:%M:%S')
                                self.write(cr, uid, ids, {'cancel_date':date_time})
		return True

	def action_cancel_draft(self, cr, uid, ids, *args):
		for invoice in self.browse(cr, uid, ids):
			if invoice.type != 'out_invoice':
				return super(account_invoice, self).action_cancel_draft( cr, uid, ids, *args)
		self.write(cr, uid, ids, {'cancel_date':False,
					  'sign_date':False,
					  'approved_year':'',
					  'approved_number':'',
					  'certificate':'',
					  'digital_signature':'',
					  'cadena':''})
		for inv_brw in self.browse(cr, uid, ids):
			if inv_brw.journal_id.code in ('factura_e' ,'nota_credito_e'):
				number, prefix = self.get_inv_number(cr, uid, inv_brw)
				if inv_brw.journal_id.code == 'factura_e':
					invtype = inv_brw.journal_id.code
				else:
					invtype = inv_brw.type
				if number:
					if inv_brw.journal_id.invoice_sequence_id:
						sid = inv_brw.journal_id.invoice_sequence_id.id
					else:
						seq_code =  'account.invoice.' + invtype
						cr.execute("SELECT id FROM ir_sequence WHERE code='%s'"%(seq_code))
						sid = cr.fetchone()[0]
					sid_brw = self.pool.get('ir.sequence').browse(cr, uid, sid)
					next_number = sid_brw.number_next
					number_increment = sid_brw.number_increment
					if (number + number_increment) == next_number:
						super(account_invoice, self).action_cancel_draft( cr, uid, ids, *args)
						move_line_brw = inv_brw.move_id.line_id
						move_line_ids = [m_line.id for m_line in move_line_brw]
						query = "SELECT reconcile_id from account_move_line where reconcile_id is not null and id in %s"%(tuple(move_line_ids), )
						cr.execute(query)
						rec_ids = cr.fetchall()
						rec_ids = [x[0] for x in rec_ids]
						if len(rec_ids) == 1:
							
							query2 = "SELECT id, move_id from account_move_line where reconcile_id = %s"%rec_ids[0]
							cr.execute(query2)
							move_ids = cr.fetchall()
							move_ids = [x[1] for x in move_ids]
							self.pool.get('account.move.reconcile').unlink(cr, uid, rec_ids)
							self.pool.get('account.move').button_cancel(cr, uid, move_ids)
							self.pool.get('account.move').unlink(cr, uid, move_ids)
						else:
							#solo cancela y borra el asiento de la factura ya que no esta conciliado o bien se rompio la conciliacion a mano
							self.pool.get('account.move').button_cancel(cr, uid, inv_brw.move_id.id)
							self.pool.get('account.move').unlink(cr, uid, inv_brw.move_id.id)
						attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_id','in',ids),('res_model','=', self._name)])
						self.pool.get('ir.attachment').unlink(cr, uid,attachment_ids)
						return True
					else:
						raise osv.except_osv(('Warrnig !'), ('This invoice can not be set to draft.'))
			else:
				super(account_invoice, self).action_cancel_draft( cr, uid, ids, *args)



	def action_number(self, cr, uid, ids, *args):
		cr.execute('SELECT id, type, number, move_id, reference ' \
				'FROM account_invoice ' \
				'WHERE id IN ('+','.join(map(str,ids))+')')
		for (id, invtype, number, move_id, reference) in cr.fetchall():
			if not number:
				if self.browse(cr, uid, id).journal_id.code == 'factura_e':
					invtype = 'factura_e'
				elif self.browse(cr, uid, id).journal_id.code == 'nota_credito_e':
					invtype = 'nota_credito_e'
				number = self.pool.get('ir.sequence').get(cr, uid,
						'account.invoice.' + invtype)
				if type in ('in_invoice', 'in_refund'):
					ref = reference
				else:
					ref = self._convert_ref(cr, uid, number)
				cr.execute('UPDATE account_invoice SET number=%s ' \
						'WHERE id=%d', (number, id))
				cr.execute('UPDATE account_move_line SET ref=%s ' \
						'WHERE move_id=%d AND (ref is null OR ref = \'\')',
						(ref, move_id))
				cr.execute('UPDATE account_analytic_line SET ref=%s ' \
						'FROM account_move_line ' \
						'WHERE account_move_line.move_id = %d ' \
							'AND account_analytic_line.move_id = account_move_line.id',
							(ref, move_id))
		return True

	def undo_action_number(self, cr, uid, inv_brw , *args):
		number = inv_brw.number
		if not number:
			if inv_brw.journal_id.code == 'factura_e':
				invtype = 'factura_e'
			elif inv_brw.journal_id.code == 'nota_credito_e':
				invtype = 'nota_credito_e'
			cr.execute('lock table ir_sequence')
			cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code = 'account.invoice." + invtype + "' and active=True")
			res = cr.dictfetchone()
			if res:
				cr.execute('update ir_sequence set number_next=number_next-number_increment where id=%s and active=True', (res['id'],))
				cr.commit()
		return True


	def test_open(self, cr, uid, ids, *args):
		#super(account_invoice, self).action_date_assign( cr, uid, ids, *args)
		for inv_brw in self.browse(cr, uid, ids):
			super(account_invoice, self).action_move_create( cr, uid, [inv_brw.id], *args)
			#super(account_invoice, self).action_number( cr, uid, [inv_brw.id], *args)
			self.action_number( cr, uid, [inv_brw.id], *args)
			if (inv_brw.journal_id.code in ('factura_e', 'nota_credito_e')) and (inv_brw.type in ('out_invoice', 'out_refund')):
				#try:
				#self.action_number( cr, uid, [inv_brw.id], *args)
				cfe = self.create_xml(cr, uid, [inv_brw.id], *args)
				cfe_str = etree.tostring(cfe, pretty_print=True, encoding='utf-8')
				self.attach_xml(cr, uid, inv_brw.id, cfe_str)
				#except:
					#self.undo_action_number( cr, uid, inv_brw , *args)
					#raise osv.except_osv(('Error !'), ('Error al crear la Factura.'))
		return True

	def attach_xml(self, cr, uid, id, cfe):
		inv_brw = self.browse(cr, uid, id)
		self.pool.get('ir.attachment').create(cr, uid, {
			'name': 'Fact.-' + inv_brw.number,
			'datas': base64.encodestring(cfe),
			'datas_fname': inv_brw.number or inv_brw.name + '.xml',
			'res_model': self._name,
			'res_id': inv_brw.id,
			}, )
		return True
						   

	def set_cfe_defaults(self):
		NS='http://www.w3.org/2001/XMLSchema-instance'
		TREE = '{%s}' % NS
		NSMAP = {'xsi': NS}
		schema_location = '{%s}schemaLocation' % NS
		cfe = etree.Element('Comprobante', attrib={schema_location:"http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv2.xsd http://www.sat.gob.mx/ecc http://www.sat.gob.mx/sitio_internet/cfd/ecc/ecc.xsd"})
		cfe.set('xmlns',"http://www.sat.gob.mx/cfd/2")
		cfe.set('version','2.0')
		return cfe

	
	def create_xml(self,cr, uid, ids, context={}):
		for inv_brw in self.browse(cr, uid, ids):
			cfe = self.set_cfe_defaults()
			cfe = self.get_datos_comprobante(cr, uid, inv_brw, cfe, context)
			emisor = self.get_emisor(cr, uid, inv_brw)
			receptro = self.get_receptor(cr, uid, inv_brw)
			conceptos = self.get_conceptos(cr, uid, inv_brw.invoice_line)
			impuestos = self.get_impuestos(cr, uid, inv_brw.tax_line)
			addenda = self.get_addenda(cr, uid, inv_brw)
			#certificado = self.get_certificado(cr, uid, inv_brw)
			cfe.append(emisor)
			cfe.append(receptro)
			cfe.append(conceptos)
			cfe.append(impuestos)
			cfe.append(addenda)
			cadena = cfdutil.getCadenaOriginal(etree.parse(StringIO.StringIO(etree.tostring(cfe))))
			keyfname = inv_brw.company_id.key
			sello = cfdutil.getSelloSHA1(cadena, keyfname, inv_brw.company_id.key_phrase)
			if not sello:
				raise osv.except_osv(('Error !'), ('Error al crear el sello.'))
			cfe.set('sello', sello)
			self.write(cr, uid, inv_brw.id, {'sign_date':cfe.get('fecha'),
							 'approved_year':int(cfe.get('anoAprobacion')),
							 'approved_number':int(cfe.get('noAprobacion')),
							 'certificate':cfe.get('certificado'),
							 'digital_signature':sello,
							 'cadena':cadena,
							 'date_invoice': cfe.get('fecha').split('T')[0]})
			#certfname = os.path.join(tools.config['root_path'], 'filestore/%s/%s'%(cr.dbname, inv_brw.company_id.certificate.store_fname))
			#certfname = os.path.join(tools.config['root_path'], 'ore/%s/%s'%(cr.dbname, inv_brw.company_id.certificate))
			certfname = inv_brw.company_id.certificate
			verify = cfdutil.verifySelloSHA1(cadena, certfname, sello)
		return cfe


	def get_domicilio_fiscal(self, cr, uid, inv_brw):
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_brw = inv_brw.company_id.partner_id
		partner_id = inv_brw.company_id.partner_id.id
		address = etree.Element('Domicilio')
		#address_obj = self.pool.get('res.partner.address')
		address = etree.Element('DomicilioFiscal')
		inovice_addres_id = partner_obj.address_get(cr, uid, [partner_id], ['invoice'])
		address_brw = address_obj.browse(cr, uid, inovice_addres_id['invoice'])
		address.set('calle', self.make_utf(address_brw.street, 'Calle Emisior'))
		address.set('colonia', self.make_utf(address_brw.street2, 'Colonia Emisior'))
		address.set('municipio',self.make_utf(address_brw.city,'Ciudad Emisior'))
		address.set('estado', self.make_utf(address_brw.state_id.name, 'Estado Emisior'))
		address.set('pais',self.make_utf(address_brw.country_id.name, 'Pais Emisior'))
		address.set('codigoPostal',self.make_utf(address_brw.zip, 'Codigo Postal Emisior'))
		return address

	def get_domicilio_ubicacion(self, cr, uid, inv_brw):
		partner_obj = self.pool.get('res.partner')
		address_obj = self.pool.get('res.partner.address')
		partner_id = inv_brw.partner_id.id
		address = etree.Element('Domicilio')
		inovice_addres_id = partner_obj.address_get(cr, uid, [partner_id], ['invoice'])
		address_brw = address_obj.browse(cr, uid, inovice_addres_id['invoice'])
		address_brw.street and address.set('calle', self.make_utf(address_brw.street or ''))
		address_brw.street2 and address.set('colonia', self.make_utf(address_brw.street2 or ''))
		address_brw.city and address.set('municipio',self.make_utf(address_brw.city or ''))
		address_brw.state_id and address.set('estado', self.make_utf(address_brw.state_id.name or ''))
		address_brw.country_id and address.set('pais',self.make_utf(address_brw.country_id.name or 'Pais Emisor'))
		address_brw.zip and address.set('codigoPostal',self.make_utf(address_brw.zip or ''))
		return address
	
	def get_emisor(self, cr, uid, inv_brw):
		partner_brw = inv_brw.company_id.partner_id
		emisor = etree.Element('Emisor')
		emisor.append(self.get_domicilio_fiscal(cr, uid, inv_brw))
		if not partner_brw.vat:
			raise osv.except_osv(_('No RFC Defined on Emisor Partner!'),_("You must define a RFC for the company !") )
		emisor.set('rfc',re.sub('[-,._ \t\n\r\f\v]','',partner_brw.vat))
		emisor.set('nombre',self.make_utf(inv_brw.company_id.name, 'Company Name'))
		return emisor
	
	def get_receptor(self,cr, uid, inv_brw):
		partner_brw = inv_brw.partner_id
		receptor = etree.Element('Receptor')
		receptor.append(self.get_domicilio_ubicacion(cr, uid, inv_brw))
		if not partner_brw.vat:
			raise osv.except_osv(_('No RFC Defined on Receptor Partner!'),_("You must define a RFC for the Client !") )
		receptor.set('rfc',re.sub('[-,._ \t\n\r\f\v]','',partner_brw.vat))
		receptor.set('nombre',self.make_utf(inv_brw.partner_id.name or 'Empresa Receptora'))
		return receptor

	def get_conceptos(self, cr, uid, lines_brw_lst):
		conceptos = etree.Element('Conceptos') 
		for line in lines_brw_lst:
			concept = etree.Element('Concepto')
			concept.set('cantidad', '%.2f'%(line.quantity))
			concept.set('descripcion',self.make_utf(line.name, 'Descripcion de Producto'))
			concept.set('valorUnitario','%.2f'%(line.price_unit))
			concept.set('importe','%.2f'%(line.price_subtotal))
			uos = line.uos_id.name
			if uos:
				concept.set('unidad', uos)
			conceptos.append(concept)
		return conceptos



	def get_tax(self, cr, uid, tax, tax_type, tax_name):
		retencion = etree.Element(tax_name)
		if tax_type == 'retain_iva':
			retencion.set('impuesto','IVA')
			tax_pct = round(float(tax.amount) / float(tax.base), 2)
			retencion.set('tasa', '%.2f'%(tax_pct * 100))
		elif tax_type == 'retain_isr':
			retencion.set('impuesto','ISR')
			tax_pct = round(float(tax.amount) / float(tax.base), 2)
			retencion.set('tasa', '%.2f'%(tax_pct * 100))
		if tax_type == 'tax_ieps':
			retencion.set('impuesto','IEPS')
			tax_pct = round(float(tax.amount) / float(tax.base), 2)
			retencion.set('tasa', '%.2f'%(tax_pct * 100))
		elif tax_type == 'tax_iva':
			retencion.set('impuesto','IVA')
			tax_pct = round(float(tax.amount) / float(tax.base), 2)
			retencion.set('tasa', '%.2f'%(tax_pct * 100))
		retencion.set('importe', '%.2f'%(abs(tax.amount)))
		
		return retencion

	
	def get_impuestos(self, cr, uid, tax_line):
		impuestos = etree.Element('Impuestos')
		traslados = etree.Element('Traslados')
		retenciones = etree.Element('Retenciones')
		total_retenciones = 0
		total_traslados = 0 
		for tax in tax_line:
			tax_type = tax.tax_code_id.code

			if (tax_type == 'retain_iva') or (tax_type == 'retain_isr'):
				retenciones.append(self.get_tax(cr, uid, tax, tax_type, 'Retencion' ))
				total_retenciones += tax.amount
			elif (tax_type == 'tax_iva') or (tax_type == 'tax_ieps'):
				traslados.append(self.get_tax(cr, uid, tax, tax_type, 'Traslado' ))
				total_traslados += tax.amount
		if total_retenciones:
			impuestos.set('totalImpuestosRetenidos', '%.2f'%(abs(total_retenciones)))
			impuestos.append(retenciones)
		if total_traslados:
			impuestos.set('totalImpuestosTrasladados', '%.2f'%(abs(total_traslados)))
			impuestos.append(traslados)
		return impuestos



	def get_addenda(self,cr, uid, inv_brw):
		addenda = etree.Element('Addenda') 
		partner_brw = inv_brw.partner_id
		if not partner_brw.addenda:
			return addenda
		addenda_brw = partner_brw.addenda
		addenda_name = etree.Element(addenda_brw.name)
		for line_brw in addenda_brw.line_ids:
			value = self.make_utf(str(eval('inv_brw.' + line_brw.default)))
			addenda_line = etree.Element(line_brw.tag)
			addenda_line.set(line_brw.tag,value)
			addenda_name.append(addenda_line)
		addenda.append(addenda_name)
		return addenda

	def get_discount(self, cr, uid, inv_brw):
		return 0

	def get_payment_form(self, cr, uid, inv_brw):
		return False

	def get_inv_number(self, cr, uid, inv_brw):
		prefix = ''
		if inv_brw.journal_id.invoice_sequence_id:
			prefix = inv_brw.journal_id.invoice_sequence_id.prefix
		else:
			prefix = inv_brw.journal_id.sequence_id.prefix
		if prefix:
			number = int(inv_brw.number[len(prefix):])
		else:
			#number = int(inv_brw.number)
			try:
				number = int(inv_brw.number)
			except ValueError:
				sequence_type = 'account.invoice.' + inv_brw.journal_id.code
				cr.execute("SELECT prefix from ir_sequence where code ='%s'"%(sequence_type))
				
				prefix = cr.fetchone()
				if prefix:
					prefix = prefix[0]
				number = int(inv_brw.number.strip(prefix))
		return number, prefix


	def get_datos_comprobante(self, cr, uid, inv_brw, cfe, context={}):
		company_obj = self.pool.get('res.company.folios')
		if inv_brw.journal_id.invoice_sequence_id:
			prefix = inv_brw.journal_id.invoice_sequence_id.prefix
		else:
			prefix = inv_brw.journal_id.sequence_id.prefix
		if prefix:
			number = int(inv_brw.number[len(prefix):])
			cfe.set('serie',prefix)
		else:
			try:
				number = int(inv_brw.number)
			except ValueError:
				sequence_type = 'account.invoice.' + inv_brw.journal_id.code
				cr.execute("SELECT prefix from ir_sequence where code ='%s'"%(sequence_type))
				
				prefix = cr.fetchone()
				if prefix:
					prefix = prefix[0]
					cfe.set('serie',prefix)
				number = int(inv_brw.number.strip(prefix))
				#raise osv.except_osv(_('Error !'),_('The invoice number has to be an integer. Wrong configuratin, check your secuenceses.'))

		cfe.set('folio',str(int(number)))
		if context.has_key('date'):
			cfe.set('fecha',context['date'])
		else:
			cfe.set('fecha',now().strftime('%Y-%m-%dT%H:%M:%S'))
		cfe.set('anoAprobacion',company_obj.get_folio_info(cr, uid, inv_brw.company_id.id, number, 'approved_year', prefix))
		cfe.set('formaDePago','Pago en una sola exhibicion')###ahy que poner una forma de pago valida
		cfe.set('noAprobacion',company_obj.get_folio_info(cr, uid, inv_brw.company_id.id, number, 'approved_number', prefix))
		cfe.set('condicionesDePago',self.make_utf(inv_brw.payment_term.name, 'Condiciones de Pago'))
		#### El certificado
		certfname = inv_brw.company_id.certificate
		nocert = cfdutil.getNoSerie(certfname)
		certstr = cfdutil.getCertString(certfname)
		cfe.set('noCertificado', nocert)
		cfe.set('certificado', certstr)
		#cfe.set('noCertificado',inv_brw.company_id.certificate_no)
		cfe.set('subTotal','%.2f'%(inv_brw.amount_untaxed))
		cfe.set('total','%.2f'%(inv_brw.amount_total))
		if inv_brw.type == 'out_invoice':
			cfe.set('tipoDeComprobante','ingreso')
		elif  inv_brw.type == 'out_refund':
			cfe.set('tipoDeComprobante','egreso')
		elif inv_brw.company_id.partner_id.vat == inv_brw.partner_id.vat:
			cfe.set('tipoDeComprobante','traslado')
		discount = self.get_discount(cr, uid, inv_brw)
		#Optinal Stuff
		if discount:
			cfe.set('descuento',str(discount))
		payment_form = self.get_payment_form(cr, uid, inv_brw)
		if payment_form:
			cfe.set('metodoDePago',payment_form)
		
		return cfe



account_invoice()



class account_invoice_addenda(osv.osv):
    _name = "account.invoice.addenda"
    _description = "Addenda for the Electronic Invoice"
    _columns = {
        'name': fields.char('Addenda', size=64, required=True),
        'active': fields.boolean('Active'),
        'note': fields.text('Description', translate=True),
        'line_ids': fields.one2many('account.invoice.addenda.lines', 'addenda_id', 'Terms'),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
    _order = "name"


account_invoice_addenda()

class account_invoice_addenda_lines(osv.osv):
    _name = "account.invoice.addenda.lines"
    _description = "Lines of the Electronic Invoice Addenda"

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
	    'addenda_id': fields.many2one('account.invoice.addenda', 'Addenda', required=True, select=True),
	    }
    _defaults = {
        'sequence': lambda *a: 5,

    }
    _order = "sequence"

account_invoice_addenda_lines()




