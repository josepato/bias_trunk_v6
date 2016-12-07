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
#Bias Product / PriceList 
#
from osv import osv
from osv import fields
from ftplib import FTP
from StringIO import StringIO

TEMPLATE_ENGINES = []

from tools.translate import _


try:
    from mako.template import Template as MakoTemplate
    TEMPLATE_ENGINES.append(('mako', 'Mako Templates'))
except ImportError:
    logging.getLogger('init').warning("module email_template: Mako templates not installed")

import tools
import pooler
import logging

def get_value(cr, uid, recid, message=None, lable=None, context=None):
    """
    Evaluates an expression and returns its value
    @param cr: Database Cr
    @param uid: ID of current uid
    @param recid: ID of the target record under evaluation
    @param message: The expression to be evaluated
    @param lable: BrowseRecord object of the current lable
    @param context: OpenERP Context
    @return: Computed message (unicode) or u""
    """
    pool = pooler.get_pool(cr.dbname)
    if message is None:
        message = {}
    #Returns the computed expression
    reply = ""
    if message:
        try:
            message = tools.ustr(message)
            object = pool.get(lable.model_int_name).browse(cr, uid, recid, context=context)
            env = {
                'uid':pool.get('res.users').browse(cr, uid, uid, context=context),
                'db':cr.dbname
                   }
            templ = MakoTemplate(message, input_encoding='utf-8')
            message_list = message.split('\n')
            res_message = []
            for mm_line in message_list:
                try:
                    res = MakoTemplate(mm_line).render_unicode(object=object,
                                                               peobject=object,
                                                               env=env,
                                                               format_exceptions=True)
                except:
                    res = False
                if res:
                    res_message.append(res)
##            reply = MakoTemplate(message).render_unicode(object=object,
##                                                         peobject=object,
##                                                         env=env,
##                                                         format_exceptions=True)
            for line in res_message:
                reply += line + '\n'
            reply = reply.rstrip('\n')
            #print reply
            return reply or False
        except Exception:
            raise osv.except_osv(_("Error!!!"), _("Error procesing the lable"))

    else:
        return message




class print_host(osv.osv):
    _name = "print.host"
    _description = 'Prints Labels on a Zebra Printer'


    def change_model(self, cr, uid, ids, object_name, context=None):
        if object_name:
            mod_name = self.pool.get('ir.model').read(
                                              cr,
                                              uid,
                                              object_name,
                                              ['model'], context)['model']
        else:
            mod_name = False
        return {
                'value':{'model_int_name':mod_name}
                }





    
    _columns = {'name': fields.char('Host', size=80),
                'object_name':fields.many2one('ir.model', 'Resource'),
                'model_int_name':fields.char('Model Internal Name', size=200,),
                'port': fields.integer('Port'),
                'user': fields.char('username', size=64),
                'passwd': fields.char('password', size=64),
                'fname': fields.char('Remote filename', size=80),
                'lable': fields.text('Label Info', reqquired=True),
                'ref_ir_act_window':fields.many2one(
                    'ir.actions.act_window',
                    'Window Action',
                    help="Action that will open this email template on Resource records",
                    readonly=True),
                'ref_ir_value':fields.many2one(
                   'ir.values',
                   'Wizard Button',
                   help="Button in the side bar of the form view of this Resource that will invoke the Window Action",
                   readonly=True),
                }

    _defaults = {'port': 21,
                 'fname': 'printdata'
                 }

    def printData(self, cr, uid, myid, data):
        my_brw = self.browse(cr, uid, myid)
        ftp = FTP()
        resp = ftp.connect(my_brw.name, my_brw.port)
        ftp.set_pasv(False)
        if my_brw.passwd:
            resp = ftp.login(my_brw.user, my_brw.passwd)
        else:
            resp = ftp.login(my_brw.user)
        fid = StringIO(data)
        resp = ftp.storbinary("STOR %s" %(my_brw.fname, ), fid)


    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        if context is None:
            context = {}
        template_obj = self.browse(cr, uid, ids, context=context)[0]
        src_obj = template_obj.object_name.model
        vals['ref_ir_act_window'] = self.pool.get('ir.actions.act_window').create(cr, uid, {
             'name': template_obj.fname,
             'type': 'ir.actions.act_window',
             'res_model': 'print.label',
             'src_model': src_obj,
             'view_type': 'form',
             'context': "{'src_model':'%s','template_id':'%d','src_rec_id':active_id,'src_rec_ids':active_ids}" % (src_obj, template_obj.id),
             'view_mode':'form,tree',
             'view_id': self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'print_lable.send.lable.form')], context=context)[0],
             'target': 'new',
             'auto_refresh':1
        }, context)
        vals['ref_ir_value'] = self.pool.get('ir.values').create(cr, uid, {
             'name': _('Print Lable (%s)') % template_obj.fname,
             'model': src_obj,
             'key2': 'client_action_multi',
             'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
             'object': True,
         }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals['ref_ir_act_window'],
            'ref_ir_value': vals['ref_ir_value'],
        }, context)
        return True


    def unlink_action(self, cr, uid, ids, context=None):
        for template in self.browse(cr, uid, ids, context=context):
            try:
                if template.ref_ir_act_window:
                    self.pool.get('ir.actions.act_window').unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    self.pool.get('ir.values').unlink(cr, uid, template.ref_ir_value.id, context)
            except:
                raise osv.except_osv(_("Warning"), _("Deletion of Record failed"))

    def delete_action(self, cr, uid, ids, context=None):
        self.unlink_action(cr, uid, ids, context=context)
        return True


print_host()
