# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class print_installer(osv.osv_memory):
    _name = 'bias.print.installer'
    _inherit = 'res.config.installer'

    _columns = {
        'rml_header': fields.text('RML Header', required=True),
        'rml_header2': fields.text('RML Internal Header', required=True),
        'rml_header3': fields.text('RML Internal Header3', required=True),

    }

    def _get_header3(self,cr,uid,ids):
        return """
        <header>

<pageTemplate>

<frame x1="57.0" y1="57.0" width="498" height="655"/>

<pageGraphics>
            <image x="2cm" y="25.3cm" height="50.0" width="80.29">[[company.logo]]</image>
        <setFont name="Helvetica" size="8"/>
            <drawString x="9.50cm" y="26.8cm">[[ company.partner_id.name ]]</drawString>
            <drawString x="9.50cm" y="26.4cm">R.F.C.: [[ company.partner_id.vat ]]</drawString>
            <drawString x="9.50cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]] Col. [[ company.partner_id.address and company.partner_id.address[0].street2 or  '' ]] C.P.: [[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]], [[ company.partner_id.address and company.partner_id.address[0].state_id.name or '' ]], [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString>
           <drawString x="9.50cm" y="25.6cm">email: [[ company.partner_id.address and company.partner_id.address[0].email or  '' ]] </drawString>
             <drawString x="9.50cm" y="25.2cm">Lugar de Expedición: Santa Catarina, Nuevo León, México.</drawString>


        <setFont name="Helvetica" size="8"/>
        <stroke color="#de5809"/>
        <lines>1.3cm 1.5cm 20cm 1.5cm</lines>



            <!--page bottom-->



            <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.2cm">Impreso por : [[ user.name ]] - Pagina: <pageNumber/></drawCentredString>
        </pageGraphics>
    </pageTemplate>
</header>
"""


    def _get_header2(self,cr,uid,ids):
        return """
        <header>

<pageTemplate>

<frame x1="57.0" y1="57.0" width="498" height="655"/>

<pageGraphics>
            <image x="2cm" y="25.3cm" height="50.0" width="80.29">[[company.logo]]</image>
        <setFont name="Helvetica" size="8"/>
            <drawString x="9.50cm" y="26.8cm">[[ company.partner_id.name ]]</drawString>
            <drawString x="9.50cm" y="26.4cm">R.F.C.: [[ company.partner_id.vat ]]</drawString>
            <drawString x="9.50cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]] Col. [[ company.partner_id.address and company.partner_id.address[0].street2 or  '' ]] C.P.: [[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]], [[ company.partner_id.address and company.partner_id.address[0].state_id.name or '' ]], [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString>
           <drawString x="9.50cm" y="25.6cm">email: [[ company.partner_id.address and company.partner_id.address[0].email or  '' ]] </drawString>
             <drawString x="9.50cm" y="25.2cm">Lugar de Expedición: Santa Catarina, Nuevo León, México.</drawString>


        <setFont name="Helvetica" size="8"/>
        <stroke color="#de5809"/>
        <lines>1.3cm 1.5cm 20cm 1.5cm</lines>



            <!--page bottom-->



            <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.2cm">Impreso por : [[ user.name ]] - Pagina: <pageNumber/></drawCentredString>
        </pageGraphics>
    </pageTemplate>
</header>
"""


    def _get_header(self,cr,uid,ids):
        try :
            header_file = tools.file_open(os.path.join('base', 'report', 'corporate_rml_header.rml'))
            try:
                return header_file.read()
            finally:
                header_file.close()
        except:
            return """
<header>

<pageTemplate>

<frame x1="57.0" y1="57.0" width="498" height="655"/>

<pageGraphics>
            <image x="2cm" y="25.3cm" height="50.0" width="80.29">[[company.logo]]</image>
        <setFont name="Helvetica" size="8"/>
            <drawString x="9.50cm" y="26.8cm">[[ company.partner_id.name ]]</drawString>
            <drawString x="9.50cm" y="26.4cm">R.F.C.: [[ company.partner_id.vat ]]</drawString>
            <drawString x="9.50cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]] Col. [[ company.partner_id.address and company.partner_id.address[0].street2 or  '' ]] C.P.: [[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]], [[ company.partner_id.address and company.partner_id.address[0].state_id.name or '' ]], [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString>
           <drawString x="9.50cm" y="25.6cm">email: [[ company.partner_id.address and company.partner_id.address[0].email or  '' ]] </drawString>
             <drawString x="9.50cm" y="25.2cm">Lugar de Expedición: Santa Catarina, Nuevo León, México.</drawString>


        <setFont name="Helvetica" size="8"/>
        <stroke color="#de5809"/>
        <lines>1.3cm 1.5cm 20cm 1.5cm</lines>



            <!--page bottom-->



            <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.2cm">Impreso por : [[ user.name ]] - Pagina: <pageNumber/></drawCentredString>
        </pageGraphics>
    </pageTemplate>
</header>

            """

            
    _defaults = {
        'rml_header':_get_header,
        'rml_header2': _get_header2,
        'rml_header3': _get_header3,
        #'logo':_get_logo
    }

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        super(print_installer, self).execute(cr, uid, ids, context=context)
        res = self.read(cr, uid, ids)
        company_obj = self.pool.get('res.company')
        company_ids = company_obj.search(cr, uid, [])
        res[0].pop('progress')
        res[0].pop('id')
        res[0].pop('config_logo')
        update_dir = res[0]

        company_obj.write(cr, uid, company_ids, update_dir)
        


print_installer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
