# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 OpenBIAS S de RL de CV (<http://www.bias.com.mx>). All Rights Reserved
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
import base64


class aaia_applications_xml_wizard(osv.osv_memory):
    _name = 'aaia.applications.xml.wizard'
    _columns = {'xmldata': fields.binary('XML File', readonly=True),
                'categ_ids': fields.many2many('product.category', 'product_categ_rel', 'categ_id', 'product_id', string='Category'),
                'partner_id': fields.many2one('res.partner', 'Customer'),
                'partner_name': fields.char('Customer', size=64),
                'state': fields.selection((('start','start'),
                                           ('withpartner','withpartner'),
                                           ('nopartner', 'nopartner'),
                                           ('attach', 'attach'),
                                           ('done', 'done')))}

    _defaults = {'state': 'start'}

    def select_partner(self, cr, uid, ids, context=None):
        partnerid = self.read(cr, uid, ids, ['partner_id'])[0]['partner_id']
        if partnerid:
            par_obj = self.pool.get('res.partner')
            myres = par_obj.read(cr, uid, partnerid, ['aaia_category', 'name'])
            catlist = myres['aaia_category']
            myname = myres['name']
            line_obj = self.pool.get('aaia.product.apply.line')
            idlist = line_obj.search(cr, uid, [('categ_id', 'in', catlist)])
            return self.write(cr, uid, ids, {'state': 'withpartner',
                                             'partner_name': myname,
                                             'categ_ids': [(6, False, catlist)]})
        else:
            return {}

    def no_partner(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'nopartner'})

    def load_categ(self, cr, uid, ids, context=None):
        partner_id = self.read(cr, uid, ids, ['categ_ids','partner_id'])[0]['partner_id']
        if partner_id:
            catlist = self.pool.get('res.partner').read(cr, uid, partner_id, ['aaia_category'])['aaia_category']
            return self.write(cr, uid, ids, {'state': 'start', 'partner_id': partner_id, 'categ_ids':[(6, False, catlist)]})
        else:
            return self.write(cr, uid, ids, {'state': 'start', 'partner_id': False, 'categ_ids': [(6, False, [])]})

    def create_xml_file(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, ['categ_ids','partner_id'])[0]
        partner_id = data['partner_id']
        catlist = data['categ_ids']
        if catlist:
            line_obj = self.pool.get('aaia.product.apply.line')
            idlist = line_obj.search(cr, uid, [('categ_id', 'in', catlist)])
            xmldata = base64.encodestring(line_obj.getXml(cr, uid, idlist))
            if partner_id:
                state = 'attach'
            else:
                state = 'done'
            return self.write(cr, uid, ids, {'state': state, 'xmldata': xmldata}, context=context)
        else:
            return {}

    def attach_xml_file(self, cr, uid, ids, context=None):
        import time
        res = self.read(cr, uid, ids, ['xmldata', 'partner_id', 'partner_name'])[0]
        (yr, mo, day, hr, mn, sec, wday, jday, dst) = time.localtime()
        datestr = "%i-%02i-%02i_%02i-%02i-%02i" %(yr, mo, day, hr, mn, sec)
        name = "Descriptions_%s.xml" %(datestr, )
        mydict = {'name': name,
                  'datas_fname': name,
                  'res_name': res['partner_name'],
                  'datas': res['xmldata'],
                  'res_model': 'res.partner',
                  'type': 'binary',
                  'res_id': res['partner_id']}
        attach_id = self.pool.get('ir.attachment').create(cr, uid, mydict)
        return {}

    def attach_file(self, cr, uid, product_id, _file, name, context=None):
        product_name = product_id and self.pool.get('product.product').browse(cr, uid, product_id).name[:126] or False
        return self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas_fname': name,
            'res_name': product_name,
            'datas': _file,
            'res_model': 'product.product',
            'type': 'binary',
            'res_id': product_id})

    def create_partner_xml_file(self, cr, uid, ids, context=None):
        if context:
            context['bin_size_xmldata'] = True
        else:
            context = {'bin_size_xmldata': True}
        catlist = self.read(cr, uid, ids, ['categ_ids'])[0]['categ_ids']
        if catlist:
            line_obj = self.pool.get('aaia.product.apply.line')
            idlist = line_obj.search(cr, uid, [('categ_id', 'in', catlist)])
            rawdata = line_obj.getXml(cr, uid, idlist)
            xmldata = base64.encodestring(rawdata)
            return self.write(cr, uid, ids, {'state': 'attach', 'xmldata': xmldata}, context=context)
        else:
            return {}

aaia_applications_xml_wizard()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
