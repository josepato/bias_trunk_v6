# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 OpenBIAS S de RL de CV (<http://www.bias.com.mx>). All Rights Reserved
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


from osv import fields, osv
from bias_zebra_print.print_host import get_value
from tools.translate import _
import StringIO
import base64


class print_label(osv.osv_memory):
    _name = 'print.label'
    _columns = {'host_id': fields.many2one('print.host', 'Printer host'),
                'zebra_data': fields.text('Label data'),
                'lable_file': fields.binary('Lable File'), 
                'picking_id': fields.many2one('stock.picking', 'Picking'),
                'copys' : fields.integer('Copys Number' ),
                'state': fields.selection((('start','start'),
                                           ('attach', 'attach'),
                                           ('dbload', 'dbload'),
                                           ('get_file','get_file'),
                                           ('done', 'done')))
                }

    _defaults = {'state': 'start',
                 'copys': 1,
                 }




    def get_value(self, cr, uid, template, message, context=None, id=None):
        """Gets the value of the message parsed with the content of object id (or the first 'src_rec_ids' if id is not given)"""
        if not message:
            return ''
        if not id:
            id = context['src_rec_ids'][0]
        return get_value(cr, uid, id, message, template, context)
    

    def _get_template(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not 'template' in context and not 'template_id' in context:
            return None
        if 'template_id' in context.keys():
            template_ids = self.pool.get('print.host').search(cr, uid, [('id','=',context['template_id'])], context=context)
        elif 'template' in context.keys():
            # Old versions of email_template used the name of the template. This caused
            # problems when the user changed the name of the template, but we keep the code
            # for compatibility with those versions.
            template_ids = self.pool.get('print.host').search(cr, uid, [('name','=',context['template'])], context=context)
        if not template_ids:
            return None
        template = self.pool.get('print.host').browse(cr, uid, template_ids[0], context)

        ctx = context.copy()
        template = self.pool.get('print.host').browse(cr, uid, template.id, ctx)
        return template

    def _get_template_value(self, cr, uid, field='lable' , context=None):
        if context is None:
            context = {}
        template = self._get_template(cr, uid, context)
        if not template:
            return False
        if len(context['src_rec_ids']) > 1: # Multiple Mail: Gets original template values for multiple email change
            return getattr(template, field)
        else: # Simple Mail: Gets computed template values
            return self.get_value(cr, uid, template, getattr(template, field), context )

    
    def getCompanyId(self, cr, uid):
        return self.pool.get('res.users').read(cr, uid, uid, ['company_id'])['company_id'][0]


    def printLabels(self, cr, uid, ids, context):
        picking_id = context['active_id']
        host_id = self.read(cr, uid, ids, ['host_id'])[0]['host_id']
        copys = self.read(cr, uid, ids, ['copys'])[0]['copys']
        print_obj = self.pool.get('print.host')
        print_brw = print_obj.browse(cr, uid, host_id)
        move_obj = self.pool.get('stock.picking')
        data = self._get_template_value(cr, uid, 'lable', context)
        for x in range(copys-1):
            data +=  '\n' + data
        try:
            print_obj.printData(cr, uid, host_id, data)
        except:
            raise osv.except_osv(_("Error!!!"), _("Conection Error. Check your Printer IP or Printer Status"))

        return self.write(cr, uid, ids, {'state': 'done', 'zebra_data': data})

    def make_file(self, cr, uid, ids, context):
        picking_id = context['active_id']
        host_id = self.read(cr, uid, ids, ['host_id'])[0]['host_id']
        copys = self.read(cr, uid, ids, ['copys'])[0]['copys']
        print_obj = self.pool.get('print.host')
        print_brw = print_obj.browse(cr, uid, host_id)
        move_obj = self.pool.get('stock.picking')
        data = self._get_template_value(cr, uid, 'lable', context)
        for x in range(copys-1):
            data +=  '\n' + data
	buf=StringIO.StringIO()
	writer=buf.write(data)
	out=base64.encodestring(buf.getvalue())
        return self.write(cr, uid, ids, {'state': 'start', 'zebra_data': data, 'lable_file':out})

print_label()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
