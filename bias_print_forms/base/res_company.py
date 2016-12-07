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

from osv import osv
from osv import fields
import os
import tools
from tools.translate import _
from tools.safe_eval import safe_eval as eval


class res_company(osv.osv):
    _inherit = "res.company"




    def _get_header3(self,cr,uid,ids):
        return """
<header>
<pageTemplate>
    <frame id="first" x1="28.0" y1="28.0" width="786" height="525"/>
    <pageGraphics>

    </pageGraphics>
    </pageTemplate>
</header>"""


    def _get_header2(self,cr,uid,ids):
        return """
        <header>
        <pageTemplate>
        <frame id="first" x1="28.0" y1="28.0" width="539" height="772"/>
        <pageGraphics>

        </pageGraphics>
        </pageTemplate>
</header>"""


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
        <frame id="first" x1="1.3cm" y1="2.5cm" height="23.0cm" width="19cm"/>
        <pageGraphics>

        </pageGraphics>
    </pageTemplate>
</header>"""

            
    _defaults = {
        'rml_header':_get_header,
        'rml_header2': _get_header2,
        'rml_header3': _get_header3,
        #'logo':_get_logo
    }


res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

