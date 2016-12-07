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

import time
import wizard
import pooler
import osv

fields = {
	'move_ids': {'string': 'Entry', 'type': 'one2many', 'relation': 'account.move'},
}

class wizard_print_entries(wizard.interface):
	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
    		payment = pool.get('payment.order').browse(cr, uid, data['id'], context)
		move_ids = [x.move_id.id for x in payment.line_ids]
    		return {
        		'move_ids': move_ids,
    		}

	states = {
		'init': {
			'actions': [_get_defaults],
			'result': {
				'type': 'print',
				'report': 'payment.print.entries',
				'state':'end'
				}
			}
		}

wizard_print_entries('payment.print.entries')

