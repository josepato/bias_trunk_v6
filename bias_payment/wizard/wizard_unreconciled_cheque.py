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

import wizard
import pooler

class wizard_unreconciled_cheque(wizard.interface):

        def _action_open_window(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		chk_obj = pool.get('payment.cheque')
		cheques = []
		chk = chk_obj.search(cr, uid, [('state','=','done')])
		for c in chk_obj.browse(cr,uid,chk):
			if c.reconciled == False:
				cheques.append(c.id)
		domain = str(('id','in',cheques))
               	return {
                'domain': "["+domain+"]",
		'name': 'Unreconciled Cheques',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'view_id': False,              
		'res_model': 'payment.cheque',
		'type': 'ir.actions.act_window',
		'limit': len(cheques)
    		}
        
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
		},
	}

wizard_unreconciled_cheque('payment.cheque.unreconciled')


