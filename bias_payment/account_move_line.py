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

from osv import fields, osv
from tools.translate import _

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def amount_to_pay(self, cr, uid, ids, name, arg={}, context={}):
        """ Return the amount still to pay regarding all the payemnt orders
        (excepting cancelled orders)"""
        if not ids:
            return {}
        cr.execute("""SELECT ml.id,
                    CASE WHEN ml.amount_currency < 0
                        THEN - ml.amount_currency
                        ELSE ml.credit
                    END -
                    (SELECT coalesce(sum(amount_currency),0)
                        FROM payment_line pl
                            INNER JOIN payment_order po
                                ON (pl.order_id = po.id)
                        WHERE move_line_id = ml.id
                        AND po.state != 'cancel') as amount
                    FROM account_move_line ml
                    WHERE id in (%s)""" % (",".join(map(str, ids))))
        r=dict(cr.fetchall())
        for i in self.browse(cr, uid, r.keys()):
            total = 0.0
            if i.invoice:
                for l in i.invoice.payment_ids:
                    if l.account_id.id == i.account_id.id:
                        if i.amount_currency:
                            total += l.amount_currency
                        else:
                            total += (l.debit or 0.0) - (l.credit or 0.0)
            r[i.id] = r[i.id] or 0.0 - total
        return r

    def _to_pay_search(self, cr, uid, obj, name, args):
        if not len(args):
            return []
        line_obj = self.pool.get('account.move.line')
        query = line_obj._query_get(cr, uid, context={})
        where = ' and '.join(map(lambda x: '''(SELECT
        CASE WHEN l.amount_currency < 0
            THEN - l.amount_currency
            ELSE l.credit
        END - coalesce(sum(pl.amount_currency), 0)
        FROM payment_line pl
        INNER JOIN payment_order po ON (pl.order_id = po.id)
        WHERE move_line_id = l.id AND po.state != 'cancel')''' \
        + x[1] + str(x[2])+' ',args))

        cr.execute(('''select id
            from account_move_line l
            where account_id in (select id
                from account_account
                where type=%s and active)
            and reconcile_id is null
            and credit > 0
            and ''' + where + ' and ' + query), ('payable',) )
        res = cr.fetchall()
        if not len(res):
            return [('id','=','0')]
        return [('id','in',map(lambda x:x[0], res))]

    _columns = {
        'amount_to_pay' : fields.function(amount_to_pay, method=True,
            type='float', string='Amount to pay', fnct_search=_to_pay_search),
    }

account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

