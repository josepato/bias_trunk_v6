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

class res_company(osv.osv):
	_inherit = 'res.company'

	_columns = {
		#'invoice_url': fields.char('Invoice Validate url', size=64, required=False),
		'certificate': fields.many2one('ir.attachment','Certificate Number',  required=False,
					       help='Attach your Certificate .cer to the company as an Attachment,/n and then select it here'),
		'nocertificado': fields.char('Numero de Certificado', size=20, required=False),
		'key': fields.many2one('ir.attachment','Key',  required=False, 					       help='Attach your Key .key to the company as an Attachment,/n and then select it here'),
		'key_phrase': fields.char('Key Phrase', size=32, invisible=True, required=False, ),
		'folio_ids': fields.one2many('res.company.folios', 'company_id', 'Folios'),
		'proveedor_cfd': fields.selection([
			('propios_medios', 'Propios Medios'),
			('my_suite_cfd', 'My Suite - CFDI'),
			('my_suite_timbre', 'My Suite - Timbrado'),
			('buzon_fiscal_cfd', 'Buzon Fiscal - CFDI'),
			('buzon_fiscal_timbre', 'Buzon Fiscal - Timbrado'),
			('tralix_timbre', 'Tralix - Timbrado')
			], 'Proveedor CDF',required=True, help="""Seleccionar el Proveedor para la generacion del CFD o CFDI."""),
		'requestor': fields.char('Requestor', size=64, invisible=True, required=False, ),
		'user_mysuite': fields.char('User MySuite', size=64, invisible=True, required=False, ),
		'username_mysuite': fields.char('UserName MySuite', size=64, invisible=True, required=False, ),
		'entity': fields.char('Entity MySuite', size=64, invisible=True, required=False, ),
		

	}
	_defaults = {
		'proveedor_cfd': lambda *a: 'propios_medios',}




res_company()



class res_company_folios(osv.osv):
    _name = "res.company.folios"
    _description = "Folios autorizados a la compania"

    _rec_name = 'folio_from'
    
    _columns = {
	    'serie': fields.char('Serie', size=5,),
	    'folio_from': fields.integer('Folio From', required=True),
	    'folio_to': fields.integer('Folio To', required=True),
	    'approved_year': fields.integer('Approved Year',required=True),
	    'approved_number': fields.integer('Approved Number', required=True,),
	    'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
	    }
    _defaults = {

    }
    _order = "folio_from"

    def get_folio_info(self, cr, uid, company_id, folio, field, serie=''):
	    if serie:
		    serie = " and serie='%s'"%(serie)
	    else:
		    serie = ''
	    query = "SELECT %s from res_company_folios where %s <= folio_to and %s >= folio_from and company_id=%s %s"%(field, folio, folio, company_id, serie)
	    cr.execute(query)
	    res = cr.fetchone()
	    try:
		    res = str(res[0])
	    except:
		    raise osv.except_osv(('Error !'), ('No se encontro un folio valido!.'))
	    return res
						

res_company_folios()




