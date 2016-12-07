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
import wizard
import pooler

dates_form = '''<?xml version="1.0"?>
<form string="Seleccion de Facturas">
	<field name="company_id"/>
	<newline/>
	<field name="partner_id"/>
	<field name="type"/>
	<newline/>
	<field name="date_start"/>
	<field name="date_end"/>
	<newline/>
	<field name="based_on"/>
	<field name="order_by"/>
</form>'''

dates_fields = {
	'company_id': {'string': 'Company', 'type': 'many2one',
		'relation': 'res.company', 'required': True},
	'partner_id': {'string': 'Partner', 'type': 'many2one',
		'relation': 'res.partner', 'required': False},
	'based_on':{'string':'State', 'type':'selection', 'selection':[
			('all','All'),
			('open','Open'),
			('paid','Paid '),
			('all_but_cancelled','All but cancel'),
			], 'required':True, 'default': lambda *a: 'all'},
	'order_by':{'string':'Order by', 'type':'selection', 'selection':[
			('date','Date'),
			('partner','Partner'),
			], 'required':False, 'default': lambda *a: 'date'},
	'type':{'string':'Invoice Type', 'type':'selection', 'selection':[
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
			], 'required':False, 'default': lambda *a: 'out_invoice'},
	'date_start': {'string': 'Start Date', 'type': 'date',
		 'required':True, 'default':  lambda *a: time.strftime('%Y-%m-%d')},
	'date_end': {'string': 'End Date', 'type': 'date',
		 'required':True, 'default':  lambda *a: time.strftime('%Y-%m-%d')},
}


class wizard_report(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        period_obj = pool.get('account.period')
        data['form']['period_id'] = period_obj.find(cr, uid)[0]
        user = pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        else:
            company_id = pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        return data['form']

    def _check(self, cr, uid, data, context):
        form = data['form']
        dic = {'date': 'ORDER BY date_invoice, partner_id, number', 'partner': 'ORDER BY partner_id, date_invoice, number'}
        order_query = dic[form['order_by']]
        partner_query = ''
        if form['partner_id']:
            partner_query = " AND partner_id = "+str(form['partner_id'])+" "
        dic = {'paid_in': "AND state IN  ('paid')", 'all': "", 'all_but_cancelled': "AND state IN  ('open','paid')",
               'open': "AND state IN  ('open')", 'paid': "AND state IN  ('paid')"}
        line_query = dic[form['based_on']]
        cr.execute("SELECT id, number FROM account_invoice " \
				"WHERE date_invoice between %s AND %s " \
                ""+partner_query+"" \
				""+line_query+"" \
				"AND type = '"+form['type']+"' "+order_query+"",(form['date_start'],form['date_end']))
        res = cr.fetchall()
        if not res:
            raise wizard.except_wizard(('No Data Available'), ('No records found for your selection!'))
        return 'report'


    states = {
		'init': {
			'actions': [_get_defaults],
			'result': {
				'type': 'form',
				'arch': dates_form,
				'fields': dates_fields,
				'state': [
					('end', 'Cancel'),
					('check', 'Print')
				]
			}
		},
        'check': {
            'actions': [],
            'result': {'type':'choice','next_state':_check}
        },
		'report': {
			'actions': [],
			'result': {
				'type': 'print',
				'report': 'account.invoice.report',
				'state':'end'
			}
		}
	}

wizard_report('account.invoice.report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
