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
import datetime
from mx.DateTime import *
import wizard
import pooler
from tools.translate import _
import StringIO
import base64
import re

summary_form = '''<?xml version="1.0"?>
<form string="Kardex Summary">
    <field name="initial_stock" readonly="1"/>
    <newline/>
    <field name="input" readonly="1"/>
    <newline/>
    <field name="output" readonly="1"/>
    <newline/>
    <field name="final_stock" readonly="1"/>
</form>'''

summary_fields = {
    'initial_stock': {'string': 'Initial stock',
                     'type': 'float',
                     'required': False
                     },
    'input': {'string': 'Incoming',
                 'type': 'float',
                 'required': False
                 },
    'output': {'string': 'Outgoing',
                'type': 'float',
                'required': False
                },
    'final_stock': {'string': 'Final stock',
                   'type': 'float',
                   'required': False
                   }
    }

report_form = '''<?xml version="1.0"?>
<form string="Kardex Report">
    <field name="date1"/>
    <field name="date2"/>
    <field name="location_id" domain="[('usage','=','internal')]"/>
    <field name="product_id"/>
</form>'''

report_fields = {
    'date1': {'string':'Start date', 'type':'datetime', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-01 00:00:00')},
    'date2': {'string':'End date', 'type':'datetime', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d %T')},
    'location_id': {'string': 'Location', 'type': 'many2one', 'relation': 'stock.location', 'help': ''},
    'product_id': {'string': 'Product', 'type': 'many2one', 'relation': 'product.product', 'help': ''},
    }

def get_all_children(cr, id):
    query = "SELECT id FROM stock_location WHERE"
    query += " location_id = %s" %(id, )
    cr.execute(query)
    idlist = [x[0] for x in cr.fetchall()]
    idtuple = (id, )
    for item in idlist:
        idtuple += (item, )
    for item in idtuple[1:]:
        idtuple += get_all_children(cr, item)
    return idtuple
    

def _action_open_window(self, cr, uid, data, context):
    form = data['form']
    query = "SELECT id FROM stock_move"
    query += " WHERE product_id='%s'" %(form['product_id'], )
    children = get_all_children(cr, form['location_id'])
    if len(children) == 1:
        children = "(%s)" %children
    query += " AND (location_id in %s OR location_dest_id in %s)" %(children, children)
    query += " AND date_planned >= '%s'" %(form['date1'], )
    query += " AND date_planned <= '%s'" %(form['date2'], )
    query += " AND location_id <> location_dest_id"
    query += " AND state = 'done'  ORDER BY date_planned"
    cr.execute(query)
    idlist = [x[0] for x in cr.fetchall()]
    return {
        'domain': "[('id','in',%s)]" % (idlist, ),
        'name': _('Kardex'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'view_id': False,
        'res_model': 'stock.move',
        'type': 'ir.actions.act_window'
    }


class wizard_kardex_report(wizard.interface):

    def _get_summary(self, cr, uid, data, context):
        form = data['form']
        children = get_all_children(cr, form['location_id'])
        if len(children) == 1:
            children = "(%s)" %children
        query = "SELECT sum(product_qty) FROM stock_move"
        query += " WHERE product_id='%s'" %(form['product_id'], )
        query += " AND location_dest_id in %s" %(children, )
        query += " AND date_planned < '%s'" %(form['date1'], )
        query += " AND state = 'done' " 
        print query
        cr.execute(query)
        data['form']['input_init'] = cr.fetchone()[0] or 0.0

        query = "SELECT sum(product_qty) FROM stock_move"
        query += " WHERE product_id='%s'" %(form['product_id'], )
        query += " AND location_id in %s" %(children, )
        query += " AND date_planned < '%s'" %(form['date1'], )
        query += " AND state = 'done' " 
        cr.execute(query)
        data['form']['output_init'] = cr.fetchone()[0] or 0.0
        data['form']['initial_stock'] = data['form']['input_init'] - data['form']['output_init']

        query = "SELECT sum(product_qty) FROM stock_move"
        query += " WHERE product_id='%s'" %(form['product_id'], )
        query += " AND location_dest_id in %s" %(children, )
        query += " AND date_planned >= '%s'" %(form['date1'], )
        query += " AND date_planned <= '%s'" %(form['date2'], )
        query += " AND location_id <> location_dest_id"
        query += " AND state = 'done' " 
        cr.execute(query)
        data['form']['input'] = cr.fetchone()[0] or 0.0

        query = "SELECT sum(product_qty) FROM stock_move"
        query += " WHERE product_id='%s'" %(form['product_id'], )
        query += " AND location_id in %s" %(children, )
        query += " AND date_planned >= '%s'" %(form['date1'], )
        query += " AND date_planned <= '%s'" %(form['date2'], )
        query += " AND location_id <> location_dest_id"
        query += " AND state = 'done' " 
        cr.execute(query)
        data['form']['output'] = cr.fetchone()[0] or 0.0
        data['form']['final_stock'] = data['form']['initial_stock'] + data['form']['input'] - data['form']['output']

        return data['form']


    states = {'init': {'actions': [],
                       'result': {'type':'form',
                                  'arch':report_form,
                                  'fields':report_fields,
                                  'state':[('end','Cancel','gtk-cancel'), ('summary','Show Summary')]}
                       },
              'summary': {'actions': [_get_summary],
                          'result': {'type': 'form',
                                     'arch': summary_form,
                                     'fields': summary_fields,
                                     'state':[('open', 'Open Kardex', '', True)]}
                       },
              'open': {'actions': [],
                       'result': {'type': 'action',
                                  'action': _action_open_window,
                                  'state':'end'}
                       }
              }
wizard_kardex_report('wizard.kardex.report')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
