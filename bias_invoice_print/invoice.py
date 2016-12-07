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


from osv import osv
from osv import fields
import time

#******************************************************************************************
#   Invoice Printing Configuration
#******************************************************************************************
class invoice_printing(osv.osv):
	_name = 'invoice.printing'
	_description = 'Invoice Printing'

	_columns = {
        'name': fields.char('Name', size=64, required=True),
        'adjustment_x': fields.float('Margin Horizontal', help='Move horizontal all the fields together'),
        'adjustment_y': fields.float('Margin Vertical', help='Move vertical all the fields together'),
        'line_id': fields.one2many('invoice.printing.line', 'printing_id', 'Lines', readonly=False, ),
        'page': fields.selection([
            ('letter','Letter'), 
            ('a4','A4')], 'Page', size=32),
        'help': fields.text('Help', readonly=False),
	}
	_defaults = {
        'page': lambda *a: 'letter',
        'help': lambda *a: '''# price_unit\n# address : res.partner.address object or False\n# product : product.product object or None\n# partner : res.partner object or None\n\nresult = price_unit * 0.10''',
        'adjustment_x': lambda *a: 15,
        'adjustment_y': lambda *a: 15,
	}

invoice_printing()

class invoice_printing_line(osv.osv):
    _name = 'invoice.printing.line'
    _description = 'Invoice Printing Line'

    def _col_get(self, cr, uid, context={}):
        result = []
        fields = self.pool.get('ir.model.fields').search(cr, uid, [('model','=','account.invoice')])
        for field in self.pool.get('ir.model.fields').browse(cr, uid, fields):
            result.append((field.id, field.name))
        result = sorted(result, key=lambda x:(x[1], x[0]))
        return result

    _columns = {
		'printing_id': fields.many2one('invoice.printing','Invoice Printing'),
        'sequence': fields.integer('Sequence'),
		'many_one_id': fields.many2one('invoice.printing.line','Invoice Printing'),
        'line_id': fields.one2many('invoice.printing.line', 'many_one_id', 'Lines'),
        'function_id': fields.one2many('invoice.printing.function', 'line_id', 'Function'),
		'field_id': fields.many2one('ir.model.fields', 'Field'),
        'field': fields.char('Field', size=128),
        'field_name': fields.char('Field Name', size=64),
        'domain': fields.char('Domain', size=64),
        'ttype': fields.char('Type', size=64),
       	'x': fields.float('Horizontal', required=True),
       	'y': fields.float('Vertical', required=True),
       	'size': fields.float('Size', required=False),
       	'angle': fields.float('Angle', required=False),
        'method': fields.selection([
            ('none','None'), 
            ('text.text','Amount to Text'), 
            ('text.moneyfmt','Money Format'), 
            ('text.formatLang','Mx Date Format'),
            ('code','Python Code'), 
#            ('function','Function'), 
            ], 'Method', readonly=False, size=32),
        'font': fields.selection([
            ('Courier','Courier'), 
            ('Courier-Bold','Courier-Bold'), 
            ('Courier-BoldOblique','Courier-BoldOblique'), 
            ('Courier-Oblique','Courier-Oblique'), 
            ('Helvetica','Helvetica'), 
            ('Helvetica-Bold','Helvetica-Bold'), 
            ('Helvetica-BoldOblique','Helvetica-BoldOblique'), 
            ('Helvetica-Oblique','Helvetica-Oblique'), 
            ('Symbol','Symbol'), 
            ('Times-Bold','Times-Bold'), 
            ('Times-BoldItalic','Times-BoldItalic'), 
            ('Times-Italic','Times-Italic'), 
            ('Times-Roman','Times-Roman'), 
            ('ZapfDingbats','ZapfDingbats'), 
            ], 'Font', size=32),
        'python_compute':fields.text('Python Code'),
    }
    _defaults = {
        'sequence': lambda *a: 1,
        'x': lambda *a: 10,
        'y': lambda *a: 750,
        'size': lambda *a: 10,
        'angle': lambda *a: 0,
        'domain': lambda *a: 'account.invoice',
        'font': lambda *a: 'Helvetica',
        'python_compute': lambda *a: '''# pool : pool object\n# cr : cursor object\n# uid : user object\n# i : account.invoice.line object or False\n# l : invoice.printing.line object or None\n\nresult = i.name''',
    }

    _order = 'sequence'

    def create(self, cr, uid, vals, context={}):
#        if vals['domain'] not in ('NULL', 'one2many'):
#            raise osv.except_osv(_('Warning'), _('There are non printable fild in selection, all Domain values must contain NULL value !'))
        return super(invoice_printing_line, self).create(cr, uid, vals, context)

    def onchange_field_id(self, cr, uid, ids, text_field, field_id):
        text_field = text_field or ''
        if not field_id:
            raise osv.except_osv(_('Warning'), _('Field value can not be NULL, select a new value or delete the line !'))
        field = self.pool.get('ir.model.fields').browse(cr,uid,field_id)
        ttype = field.ttype
        relation = field.relation
        if ttype == 'one2many':
            text_field =  text_field + (text_field and '.') + field.name
        else:
            text_field =  text_field + (text_field and '.') + field.name
        return {'value': {'ttype': ttype,'domain': relation, 'field': text_field, 'field_name': field.name}}  

    def default_get(self, cr, uid, fields, context={}):
        data = super(invoice_printing_line, self).default_get(cr, uid, fields, context)
        if context.has_key('domain'):
            data['domain'] = context['domain']
        if context.has_key('y'):
            data['y'] = context['y']
#        for f in data.keys():
#            if f not in fields:
#                del data[f]
        return data

invoice_printing_line()

class invoice_printing_function(osv.osv):
    _name = 'invoice.printing.function'
    _description = 'Invoice Printing Function'

    _columns = {
		'line_id': fields.many2one('invoice.printing.line','Invoice Printing Line'),
		'field_id': fields.many2one('ir.model.fields', 'Field'),
        'field': fields.char('Field', size=128),
        'field_name': fields.char('Field Name', size=64),
        'domain': fields.char('Domain', size=64),
        'ttype': fields.char('Type', size=64),
        'function': fields.selection([
            ('and','AND'), 
            ('or','OR'), 
            ('in','IN'), 
            ('not in','NOT IN'), 
            ('get','GET'), 
            ], 'Function', size=32),
    }
    _defaults = {
        'domain': lambda *a: 'account.invoice',
    }

    def onchange_field_id(self, cr, uid, ids, text_field, field_id):
        res = self.pool.get('invoice.printing.line').onchange_field_id(cr, uid, ids, text_field, field_id)
        return res

invoice_printing_function()
#----------------------------------------------------------
# Account Journal
#----------------------------------------------------------
class account_journal(osv.osv):
    _inherit="account.journal"

    _columns = {
        'invoice_printing_id': fields.many2one('invoice.printing', 'Invoice Printing'),
    }
account_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

