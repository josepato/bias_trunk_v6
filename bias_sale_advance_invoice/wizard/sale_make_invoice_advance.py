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

from osv import fields, osv
from tools.translate import _

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    _columns = {
        'copy_lines': fields.boolean('Copy Sale Order Lines', help="Check to copy all Sale Order Lines."),
        }
    _defaults = {
        'copy_lines': True
    }

    def create_invoices(self, cr, uid, ids, context=None):
        """
             To create invoices.
             copys all sale order lines and cretes it on the invoice
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs if we want more than one
             @param context: A standard dictionary

             @return:

        """
        res = super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context=context)
        list_inv = []
        obj_sale = self.pool.get('sale.order')
        obj_lines = self.pool.get('account.invoice.line')
        inv_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        for invoice_id in res['context']['invoice_id']:
            for sale_adv_obj in self.browse(cr, uid, ids, context=context):
                if sale_adv_obj.copy_lines:
                    for sale in obj_sale.browse(cr, uid, context.get('active_ids', []), context=context):
                        for sale_line in sale.order_line:
                            val = obj_lines.product_id_change(cr, uid, [], sale_line.product_id.id,
                                                              uom = False, partner_id = sale.partner_id.id, fposition_id = sale.fiscal_position.id)
                            line_id = obj_lines.create(cr, uid, {
                                'name': val['value']['name'],
                                'account_id': val['value']['account_id'],
                                'price_unit': 0.0,
                                'quantity': sale_line.product_uom_qty,
                                'discount': False,
                                'uos_id': val['value']['uos_id'],
                                'product_id': sale_line.product_id.id,
                                'invoice_line_tax_id': [(6, 0, val['value']['invoice_line_tax_id'])],
                                'note':sale_line.notes,
                                'invoice_id':invoice_id,
                                })
        return res


sale_advance_payment_inv()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
