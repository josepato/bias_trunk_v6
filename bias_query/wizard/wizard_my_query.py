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

class wizard_my_query(wizard.interface):

    def _account_chart_open_window(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'query.tool', 'query_normal_action_tree')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id], context=context)[0]
#        result['context'] = str({'fiscalyear': data['form']['fiscalyear'],'state':data['form']['target_move']})
#        if data['form']['fiscalyear']:
#            result['name']+=':'+pooler.get_pool(cr.dbname).get('account.fiscalyear').read(cr,uid,[data['form']['fiscalyear']])[0]['code']
        return result

    def _action_open_window(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        query_obj = pool.get('query.tool')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')
        querys = []
        for q in query_obj.search(cr,uid,[]):
            if uid in [x.id for x in query_obj.browse(cr, uid, q).user_ids]:
                querys.append(q)
        domain = str(('id','in',querys))
        id = act_obj.search(cr, uid, [('res_model','=','query.category'),('name','=','Querys by Category')])
        result = act_obj.read(cr, uid, id, context=context)[0]
        result['context'] = str({'user_ids': [uid]})
        return result
        return {
        'domain': "["+domain+"]",
		'name': 'My Querys',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'view_id': False,              
		'res_model': 'query.category',
		'type': 'ir.actions.act_window',
		'limit': len(querys)
        }
        
    states = {
        'init': {
			'actions': [],
			'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
		},
	}

wizard_my_query('my.query.tool')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
