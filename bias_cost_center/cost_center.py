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
#
#Bias Account / Cost Center
#

from osv import osv
from osv import fields
from tools import config
import time
import netsvc

#----------------------------------------------------------
# Cost Center
#----------------------------------------------------------
class cost_center(osv.osv):

    _name = "cost.center"
    _order = "code,parent_id,name"
    _parent_order = "code"
    _parent_store = True


    _description = "Bias Cost Center"

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        pos = 0

        while pos < len(args):

            if args[pos][0] == 'code' and args[pos][1] in ('like', 'ilike') and args[pos][2]:
                args[pos] = ('code', '=like', str(args[pos][2].replace('%', ''))+'%')
            pos += 1

        return super(cost_center, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)


    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' '+name
            res.append((record['id'], name))
        return res

    def full_name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.full_name_get(cr, uid, ids, context=context)
        return dict(res)


    def get_children(self, cr, uid, ids,context={}):
        res = []
        for rec in self.browse(cr, uid, ids, context=context):
            for child in rec.child_parent_ids:
                if child.child_parent_ids:
                    res += self.get_children(cr, uid, [child.id])
                else:
                    res += [child.id]
            res += [rec.id]
        return res


    def _get_child_ids(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for record in self.browse(cr, uid, ids, context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []

         #   if record.child_consol_ids:
          #      for acc in record.child_consol_ids:
           #         result[record.id].append(acc.id)

        return result

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from cost_center where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name': fields.char('Name', size=64, required=True, select=1, 
                            help="Determines multiple cost center of a company, like a brach, cetain office or a city"),
        'code': fields.char('Code', size=32, required=True, select=1),
        'active': fields.boolean('Active', help="Actives / Deactives The Cost Center"),
        'note': fields.text('Description',),
        'parent_id': fields.many2one('cost.center', 'Parent', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_parent_ids': fields.one2many('cost.center','parent_id','Children'),
#        'child_consol_ids': fields.many2many('cost.center', 'cost_center_consol_rel', 'child_id', 'parent_id', 'Consolidated Children'),
        'child_id': fields.function(_get_child_ids, method=True, type='many2many', relation="cost.center", string="Child Cost Center"),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive Cost Center.', ['parent_id'])
    ]
    _defaults = {
        'active': lambda *a: 1,
    }

    
cost_center ()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),

    }

    def _invoice_line_hook(self, cursor, user, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        super(stock_picking, self)._invoice_line_hook(cursor, user, move_line, invoice_line_id)
        cr, uid = cursor, user
        m_cc_id = move_line.cost_center_id.id
        self.pool.get('account.invoice.line').write(cr, uid, [invoice_line_id], {'cost_center_id': m_cc_id})
        return

    def _invoice_hook(self, cursor, user, picking, invoice_id):
        '''Call after the creation of the invoice'''
        super(stock_picking, self)._invoice_hook(cursor, user, picking, invoice_id)
        cr, uid = cursor, user
        p_cc_id = picking.cost_center_id.id
        self.pool.get('account.invoice').write(cr, uid, [invoice_id], {'cost_center_id': p_cc_id})
        return


stock_picking()


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False),

    }
    def _default_cost_center_id(self, cr, uid, context={}):
        if context.get('move_line', []):
            return context['move_line'][0][2]['cost_center_id']
        return False

    _defaults = {
        'cost_center_id': _default_cost_center_id,
    }

    def get_move_lines(self, cr, uid, move, amount, acc_src, ref, date, partner_id, acc_dest):
        '''Return the account move line created for the stock move'''
        res = super(stock_move, self).get_move_lines(cr, uid, move, amount, acc_src, ref, date, partner_id, acc_dest)
        res[0][2]['cost_center_id'] = move.cost_center_id.id
        res[1][2]['cost_center_id'] = move.cost_center_id.id
        return res


stock_move()


#----------------------------------------------------------
# Account Invoice
#----------------------------------------------------------


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def line_get_convert(self, cr, uid, x, part, date, inv_cc, context=None):
        if not 'cost_center_id' in x and inv_cc:
            x['cost_center_id'] = inv_cc

        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id':part,
            'name':x['name'][:64],
            'date': date,
            'debit':x['price']>0 and x['price'],
            'credit':x['price']<0 and -x['price'],
            'account_id':x['account_id'],
            'cost_center_id':x.get('cost_center_id', False),
            'analytic_lines':x.get('analytic_lines', []),
            'amount_currency':x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id':x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref':x.get('ref',False),
            'quantity':x.get('quantity',1.00),
            'product_id':x.get('product_id', False),
            'product_uom_id':x.get('uos_id',False),
            'analytic_account_id':x.get('account_analytic_id',False),
        }

    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False, readonly=True, states={'draft':[('readonly',False)]}),

    }

    def action_move_create(self, cr, uid, ids, *args):
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        context = {}
        for inv in self.browse(cr, uid, ids):
            if inv.move_id:
                continue

            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            line_ids = self.read(cr, uid, [inv.id], ['invoice_line'])[0]['invoice_line']
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # check if taxes are all computed

            context.update({'lang': inv.partner_id.lang})
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=context)
            if not inv.tax_line:
                for tax in compute_taxes.values():
                    ait_obj.create(cr, uid, tax)
            else:
                tax_key = []
                for tax in inv.tax_line:
                    if tax.manual:
                        continue
                    key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
                    tax_key.append(key)
                    if not key in compute_taxes:
                        raise osv.except_osv(_('Warning !'), _('Global taxes defined, but are not in invoice lines !'))
                    base = compute_taxes[key]['base']
                    if abs(base - tax.base) > inv.company_id.currency_id.rounding:
                        raise osv.except_osv(_('Warning !'), _('Tax base different !\nClick on compute to update tax base'))
                for key in compute_taxes:
                    if not key in tax_key:
                        raise osv.except_osv(_('Warning !'), _('Taxes missing !'))

            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = self._convert_ref(cr, uid, inv.number)

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            for i in iml:
                if inv.currency_id.id != company_currency:
                    i['currency_id'] = inv.currency_id.id
                    i['amount_currency'] = i['price']
                    i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
                            company_currency, i['price'],
                            context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                    i['price'] = round(i['price'], 3)
                else:
                    i['amount_currency'] = False
                    i['currency_id'] = False
                i['ref'] = ref
                if inv.type in ('out_invoice','in_refund'):
                    total += i['price']
                    total_currency += i['amount_currency'] or i['price']
                    i['price'] = - i['price']
                    i['price'] = round(i['price'], 3)
                else:
                    total -= round(i['price'], 3)
                    total_currency -= i['amount_currency'] or i['price']
            acc_id = inv.account_id.id

            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = self.pool.get('account.payment.term').compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid,
                                company_currency, inv.currency_id.id, t[1])
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and  amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity' : inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')
            part = inv.partner_id.id
            inv_cc_id = inv.cost_center_id.id
            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, inv_cc_id, context={})) ,iml)
            if inv.journal_id.group_invoice_lines:
                line2 = {}
                for x, y, l in line:
                    tmp = str(l['account_id'])
                    tmp += '-'+str(l.get('tax_code_id',"False"))
                    tmp += '-'+str(l.get('product_id',"False"))
                    tmp += '-'+str(l.get('analytic_account_id',"False"))
                    tmp += '-'+str(l.get('date_maturity',"False"))
                    
                    if tmp in line2:
                        am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
                        line2[tmp]['debit'] = (am > 0) and am or 0.0
                        line2[tmp]['credit'] = (am < 0) and -am or 0.0
                        line2[tmp]['tax_amount'] += l['tax_amount']
                        line2[tmp]['analytic_lines'] += l['analytic_lines']
                    else:
                        line2[tmp] = l
                line = []
                for key, val in line2.items():
                    line.append((0,0,val))
            journal_id = inv.journal_id.id #self._get_journal(cr, uid, {'type': inv['type']})
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create invoice move on centralised journal'))
            move = {'ref': inv.number, 'line_id': line, 'journal_id': journal_id, 'date': date}
            period_id=inv.period_id and inv.period_id.id or False
            if not period_id:
                period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id=period_ids[0]
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id
            move_id = self.pool.get('account.move').create(cr, uid, move)
            new_move_name = self.pool.get('account.move').browse(cr, uid, move_id).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name})
            self.pool.get('account.move').post(cr, uid, [move_id])
        self._log_event(cr, uid, ids)
        return True

    def _refund_cleanup_lines(self, cr, uid, lines):
#        lines = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        for line in lines:
            if 'cost_center_id' in line:
                line['cost_center_id'] = line.get('cost_center_id', False) and line['cost_center_id'][0]
            if 'account_id' in line:
                line['account_id'] = line.get('account_id', False) and line['account_id'][0]
            if 'product_id' in line:
                line['product_id'] = line.get('product_id', False) and line['product_id'][0]
            if 'uos_id' in line:
                line['uos_id'] = line.get('uos_id', False) and line['uos_id'][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6,0, line.get('invoice_line_tax_id', [])) ]
            if 'account_analytic_id' in line:
                line['account_analytic_id'] = line.get('account_analytic_id', False) and line['account_analytic_id'][0]
            if 'tax_code_id' in line :
                if isinstance(line['tax_code_id'],tuple)  and len(line['tax_code_id']) >0 :
                    line['tax_code_id'] = line['tax_code_id'][0]
            if 'base_code_id' in line :
                if isinstance(line['base_code_id'],tuple)  and len(line['base_code_id']) >0 :
                    line['base_code_id'] = line['base_code_id'][0]
        return map(lambda x: (0,0,x), lines)

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None):
        invoices = self.read(cr, uid, ids, ['name', 'type', 'number', 'reference', 'comment', 'date_due', 'partner_id', 'address_contact_id', 'address_invoice_id', 'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id', 'invoice_line', 'tax_line', 'journal_id', 'cost_center_id'])

        new_ids = []
        for invoice in invoices:
            del invoice['id']

            type_dict = {
                'out_invoice': 'out_refund', # Customer Invoice
                'in_invoice': 'in_refund',   # Supplier Invoice
                'out_refund': 'out_invoice', # Customer Refund
                'in_refund': 'in_invoice',   # Supplier Refund
            }

            invoice_lines = self.pool.get('account.invoice.line').read(cr, uid, invoice['invoice_line'])
            invoice_lines = self._refund_cleanup_lines(cr, uid, invoice_lines)

            tax_lines = self.pool.get('account.invoice.tax').read(cr, uid, invoice['tax_line'])
            tax_lines = filter(lambda l: l['manual'], tax_lines)
            tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines)
            if not date :
                date = time.strftime('%Y-%m-%d')
            invoice.update({
                'type': type_dict[invoice['type']],
                'cost_center_id': invoice['cost_center_id'][0],
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines
            })
            if period_id :
                invoice.update({
                    'period_id': period_id,
                })
            if description :
                invoice.update({
                    'name': description,
                })
            # take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                    'account_id', 'currency_id', 'payment_term', 'journal_id'):
                invoice[field] = invoice[field] and invoice[field][0]
            # create the new invoice
            new_ids.append(self.create(cr, uid, invoice))
        return new_ids


account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def move_line_get_item(self, cr, uid, line, context=None):

        return {
            'type':'src',
            'name': line.name[:64],
            'price_unit':line.price_unit,
            'quantity':line.quantity,
            'price':line.price_subtotal,
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uos_id.id,
            'account_analytic_id':line.account_analytic_id.id,
            'taxes':line.invoice_line_tax_id,
            'cost_center_id':line.cost_center_id.id,
        }

    def default_get(self, cr, uid, fields, context={}):
        data = super(account_invoice_line, self).default_get(cr, uid, fields, context)
        if 'cost_center_id' in fields and 'parent_cost_center' in context:
            data['cost_center_id']=context['parent_cost_center']
        return data

    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False, help="The Cost Center of this entry line."),


    }

account_invoice_line()


#----------------------------------------------------------
# Account Move Line
#----------------------------------------------------------

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _default_get(self, cr, uid, fields, context={}):
        data = super(account_move_line, self)._default_get(cr, uid, fields, context)
        if not 'move_id' in data:
            return data
        move_id = data['move_id']
        move = self.pool.get('account.move').browse(cr, uid, move_id, context)
        cost_center_id = False
        for l in move.line_id:
            cost_center_id = cost_center_id or l.cost_center_id.id

        if 'cost_center_id' in fields:
            data['cost_center_id'] = cost_center_id

        return data


    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False, help="The Cost Center of this entry line."),
    }


account_move_line()

#---------------------------------------------------------
# Sale Order
#---------------------------------------------------------

class sale_order(osv.osv):
    _inherit="sale.order"
    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = True),
    }
    def _make_invoice(self, cr, uid, order, lines, context={}):
        a = order.partner_id.property_account_receivable.id
        if order.payment_term:
            pay_term = order.payment_term.id
        else:
            pay_term = False
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',):
                for preline in preinv.invoice_line:
                    inv_line_id = self.pool.get('account.invoice.line').copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        inv = {
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': "P%dSO%d" % (order.partner_id.id, order.id),
            'account_id': a,
            'cost_center_id': order.cost_center_id.id or False,
            'partner_id': order.partner_id.id,
            'address_invoice_id': order.partner_invoice_id.id,
            'address_contact_id': order.partner_invoice_id.id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': pay_term,
            'fiscal_position': order.partner_id.property_account_position.id
        }
        inv_obj = self.pool.get('account.invoice')
        inv.update(self._inv_get(cr, uid, order))
        inv_id = inv_obj.create(cr, uid, inv)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], pay_term, time.strftime('%Y-%m-%d'))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id

    def action_ship_create(self, cr, uid, ids, *args):
        res = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        sale_line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids):
            pick_ids = map(lambda x: x.id, sale.picking_ids)
            pick_obj.write(cr, uid, pick_ids, {'cost_center_id': sale.cost_center_id.id})
            for line in sale.order_line:
                move_ids = map(lambda x: x.id, line.move_ids)
                move_obj.write(cr, uid, move_ids, {'cost_center_id': line.cost_center_id.id})

        return res

sale_order()

class sale_order_line(osv.osv):
    _inherit="sale.order.line"

    def default_get(self, cr, uid, fields, context={}):

        data = super(sale_order_line, self).default_get(cr, uid, fields, context)
        if 'cost_center_id' in fields and 'parent_cost_center' in context:
            data['cost_center_id']=context['parent_cost_center']
        return data


    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = False),
    }

    def invoice_line_create(self, cr, uid, ids, context={}):
        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('mrp.procurement').quantity_get(cr, uid,
                        line.procurement_id.id, context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('mrp.procurement').uom_get(cr, uid,
                        line.procurement_id.id, context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    a = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            int(config['price_accuracy']))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'cost_center_id': line.cost_center_id.id or False,
                    'price_unit': pu,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                    'note': line.notes,
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})

                sales[line.order_id.id] = True
                create_ids.append(inv_id)

        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids


sale_order_line()


#---------------------------------------------------------
# Purchase Order
#---------------------------------------------------------

class purchase_order(osv.osv):
    _inherit="purchase.order"
    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = True),
    }

    def inv_line_create(self, cr, uid, a, ol):
        return (0, False, {
            'name': ol.name,
            'account_id': a,
            'cost_center_id': ol.cost_center_id.id,
            'price_unit': ol.price_unit or 0.0,
            'quantity': ol.product_qty,
            'product_id': ol.product_id.id or False,
            'uos_id': ol.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])],
            'account_analytic_id': ol.account_analytic_id.id,
        })

    


    def action_invoice_create(self, cr, uid, ids, *args):
        po_id = ids[0]
        res = False
        inv_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, *args)
        po_cc_id = self.read(cr, uid, po_id)['cost_center_id']
        self.pool.get('account.invoice').write(cr, uid, [inv_id], {'cost_center_id': po_cc_id[0]})
        res = inv_id
        return res

    def action_picking_create(self,cr, uid, ids, *args):
        po_id = ids[0]
        picking_id = super(purchase_order, self).action_picking_create(cr, uid, ids, *args)
        po_cc_id = self.read(cr, uid, po_id)['cost_center_id']
        self.pool.get('stock.picking').write(cr, uid, [picking_id], {'cost_center_id': po_cc_id[0]})
        s_move_obj = self.pool.get('stock.move')
        s_move_ids = s_move_obj.search(cr,uid,[('picking_id','=',picking_id),])
        for i in s_move_obj.browse(cr, uid, s_move_ids):
            line_id = i.purchase_line_id.id
            l_cc_id = self.pool.get('purchase.order.line').read(cr, uid, line_id)['cost_center_id']
            self.pool.get('stock.move').write(cr, uid, [i.id], {'cost_center_id': l_cc_id[0]})
        return picking_id

purchase_order()

#---------------------------------------------------------
# Purchase Order Line
#---------------------------------------------------------

class purchase_order_line(osv.osv):
    _inherit="purchase.order.line"

    def default_get(self, cr, uid, fields, context={}):
        data = super(purchase_order_line, self).default_get(cr, uid, fields, context)
        if 'cost_center_id' in fields and 'parent_cost_center' in context:
            data['cost_center_id']=context['parent_cost_center']
        return data

    _columns = {
       'cost_center_id': fields.many2one('cost.center', 'Cost Center', required = True),    
    }
    _defaults = {

    }

purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
