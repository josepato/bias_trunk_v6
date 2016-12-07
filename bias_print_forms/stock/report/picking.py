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
from report import report_sxw
from osv import osv
import pooler

class picking(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal,
            'convert_value': self._convert_value,
        })

    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total+=move.product_qty
        return {'quantity':total,'uom':uom}

    def _convert_value(self, value, context={}):            
        if not value:
            return ''
        if context.get('strip', False) and context.get('model', False):
            quitar=len(context['model'])+3
            value = value[quitar:]
            return value
        if context.get('money_format', False):
            return '$ ' + text.moneyfmt( '%.2f' % float(value))
        if context.get('status', False):
            state_dict = {'assigned': 'Reservado','done':'Realizado', '2binvoiced': 'Para Facturar', 'invoiced': 'Facturado', 'none': 'No Aplicable', 'draft': 'Borrador', 'confirmed': 'Confirmado', 'cancel': 'Cancelado'}
            return state_dict[value]            
        return value



report_sxw.report_sxw('report.stock.picking.bias','stock.picking','addons/bias_print_forms/stock/report/picking.rml',parser=picking)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
