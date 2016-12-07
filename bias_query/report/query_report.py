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



from report.interface import report_int
import reportlab.lib.pagesizes as pagesize
import pooler
import tools
from lxml  import etree
from report import render
import csv
import re

import time, os
import mx.DateTime
import StringIO
import base64
import utilRML_std

class report_printscreen_list(report_int):
    def __init__(self, name):
        report_int.__init__(self, name)



    def unicode_csv_reader(self, utf8_data, dialect=csv.excel, **kwargs):
        csv_reader = csv.reader(utf8_data, delimiter = ',', quotechar = '"')
        for row in csv_reader:
            yield [unicode(cell, 'utf-8') for cell in row]



    def comma_me(self,amount):
        if  type(amount) is float :
            amount = str('%.2f'%amount)
        else :
            amount = str(amount)
        if (amount == '0'):
            return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>,\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)


    def get_para_style(self, uid, field):
        result = {}
        para = utilRML_std.para()
        para.setnoClosing()
        col_options = field.keys()
        for option in dir(para):
            if option in col_options:
                para_str = 'para.%s("%s")'%(option, field[option])
                if field.has_key('conditioning'):
                    result['conditioning'] = field['conditioning']
                if field[option]:
                    eval(para_str)
        result['para'] = para
        return result

    def evaluate_condition(self, uid, condition_brw, elem):
        for condition in condition_brw:
            try:
                res = eval("%s %s %s"%(elem, condition.name, condition.value))
            except:
                res = eval("'%s' %s '%s'"%(elem, condition.name, condition.value))
            if res:
                field ={'setfontname':condition.fontname,
                        'setfontsize':condition.fontsize,
                        'setalignment':condition.align,
                        'settextColor':condition.textcolor,
                        'setbackColor':condition.backcolor,
                         }
                para_style = self.get_para_style(uid, field)['para']
                return para_style
        return ''
            

    def _parse_node(self, root_node):
        result = []
        for node in root_node.getchildren():
            if node.tag == 'field':
                attrsa = node.attrib
                attrs = {}
                if not attrsa is None:
                   for key,val in attrsa.items():
                    attrs[key] = val
                result.append(attrs['name'])
            else:
                result.extend(self._parse_node(node))
        return result

##    def _parse_string(self, view):
##        try:
##            dom = etree.XML(view.encode('utf-8'))
##        except:
##            dom = etree.XML(view)   
##        return self._parse_node(dom)

    def create(self, cr, uid, ids, datas, context=None):
        if not context:
            context={}
        pool = pooler.get_pool(cr.dbname)
        model = pool.get(datas['model'])
        model_id = pool.get('ir.model').search(cr, uid, [('model','=',model._name)])
        model_brw =  model.browse(cr, uid, datas['id'])
        datas['ids'] = ids
        model = pooler.get_pool(cr.dbname).get(datas['model'])
        lables = model_brw.label_ids
        fields = {}
        fields_order = []
        invisible  = []
        for label in model_brw.label_ids:
            if not label.invisible:
                invisible.append(0)
                fields_order.append(label.label_new or label.name)
                fields[label.label_new or label.name] = {
                    'size':label.size,
                    'string':label.label_new or label.name,
                    'type':label.f_type,
                    'setfontname':label.fontname,
                    'setfontsize':label.fontsize,
                    'setalignment':label.align,
                    'settextColor':label.textcolor,
                    'setbackColor':label.backcolor,
                    'sum':label.sum,
                    }
                if label.style_ids:
                    fields[label.label_new or label.name].update({'conditioning':label.style_ids})
            else:
                invisible.append(1)
        rows = datas['form']['file.csv']
        buf = StringIO.StringIO(rows)
        report_name = '/tmp/report_%s.csv'%(uid)
        ss = open(report_name,'w')
        ss.write(base64.decodestring(buf.getvalue()))
        ss.close()
        buf.close()
        #rows = csv.reader(open(report_name,'rb'), delimiter = ',', quotechar = '"')
        rows = self.unicode_csv_reader(open(report_name,'rb'))
        rows_lst = []
        sniff = []
        integer = ''
        header = []
        if datas['form']['header']:
            count = 0
            for rr in rows:
                if count == 4:
                    first_row_titles = rows.next()
                    self.title = header[2]
                    break
                header += rr
                count +=1
        else:
            self.title = model_brw.name
        for row in rows:
            count = 0
            new_row = []
            for rr in row:
                if not invisible[count]:
                    new_row.append(rr)
                count += 1
            rows_lst.append(new_row)
        res = self._create_table(uid, model_brw, datas['ids'], fields, fields_order, rows_lst, context, self.title , header)
        return (self.obj.get(), 'pdf')


    def add_row_element(self, uid, elem, para_col_tag, count, type=0):
        if type:
            if elem:
                cc = self.comma_me(elem)
                if para_col_tag[count].has_key('conditioning'):
                    new_para = self.evaluate_condition(uid, para_col_tag[count]['conditioning'], re.sub(' %','',elem))
                    if new_para:
                        return new_para + self.comma_me(elem) +'</para>' or '' 
                    else:
                        return para_col_tag[count]['para'] + self.comma_me(elem) +'</para>' or '' 
                else:
                    return para_col_tag[count]['para'] + self.comma_me(elem) +'</para>' or '' 
            else:
                return ''
        else:
            if elem:
                if para_col_tag[count].has_key('conditioning'):
                    new_para = self.evaluate_condition(uid, para_col_tag[count]['conditioning'], re.sub(' %','',elem))
                    if new_para:
                        return new_para + elem +'</para>' or '' 
                    else:
                        return para_col_tag[count]['para'] + elem +'</para>' or '' 
                else:
                    return para_col_tag[count]['para'] + elem +'</para>' or '' 
            else:
                return ''

    def _create_table(self, uid, model_brw, ids, fields, fields_order, results, context, title='', header = ''):
        stylesheet = utilRML_std.stylesheet()
        style = utilRML_std.getdefaultStyles()
        stylesheet.addElement(style)
        story = utilRML_std.story()
        style_acc = utilRML_std.blockTableStyle('location_heder')
        style_acc.setblockFont('Helvetica-Bold',{'size':'9'})
        style_acc.setblockAlignment('LEFT')
        style_acc.setlineStyle('LINEBELOW', 'black', {'thickness':'2','start':'0,-1', 'stop':'-1,-1'})
        stylesheet.addElement(style_acc)
        table_functions = {'page':model_brw.page_size,
                           'portrait' : model_brw.portrait,}
        #table_h, style_heder = utilRML_std.getstandarReportHeader(header, table_functions)
        #stylesheet.addElement(style_heder)
        pageSize =  'pagesize.%s'%(table_functions['page'])
        pageSize = eval(pageSize)
        if table_functions['portrait']:
            pageSize = (pageSize[1], pageSize[0])

        l = []
        t = 0
        rowcount=0;
        strmax = (pageSize[0] - 60) 
        temp = []
        count = len(fields_order)
        for i in range(0,count):
            temp.append(0)
        if header:
            table = utilRML_std.blockTable()
            table.setstyle('header')
            table.setcolWidths('%s,%s,%s'%(strmax/3 , strmax/3, strmax/3))
            row = utilRML_std.tr()
            row.addElement(' ')
            row.addElement(header[0])
            r20 = header[1].split(',')[0]
            row.addElement(r20)
            row2 = utilRML_std.tr()
            row2.addElement('')
            row2.addElement(header[2])
            r21 = header[1].split(',')[1]
            row2.addElement(r21)
            table.addElement(row)
            table.addElement(row2)
            count = 0
            row = utilRML_std.tr()
            story.addElement(table)
            #### adds the options
            table = utilRML_std.blockTable()
            table.setstyle('header-options')
            table.setcolWidths('%s'%(strmax))
            row = utilRML_std.tr()
            row.addElement('<para>' + header[3] + '</para>')
            table.addElement(row)
            story.addElement(table)
        ince = -1;
        para_col_tag = []
        row = utilRML_std.tr()
        context = {'fontName':'Helvetica-Bold'}
        for f in fields_order:
            row.addElement(f, context)
            s = 0
            ince += 1
            if (fields[f]['type'] in ('float','integer')) and not (fields[f]['sum']):
                temp[ince] = 1
            elif (fields[f]['type'] in ('float','integer')) and (fields[f]['sum']):
                temp[ince] = 2
            elif (fields[f]['type'] == 'pct') and not (fields[f]['sum']):
                temp[ince] = 3
            elif (fields[f]['type'] == 'pct') and (fields[f]['sum']):
                temp[ince] = 4
            t += fields[f].get('size', 10)# / 28 + 1
            l.append(s)
            para_col_tag.append(self.get_para_style( uid, fields[f]))
        for pos in range(len(l)):
            if not l[pos]:
                s = fields[fields_order[pos]].get('size', 10) #/ 28 + 1
                l[pos] = strmax * s / t
        nl = ''        
        for size in map(str,l):
            nl += size + ' ,'
        nl = nl.rstrip(',')
        tsum = []
        count = len(fields_order)
        for i in range(0,count):
            tsum.append(0)
        table = utilRML_std.blockTable()
        table.setcolWidths(nl)
        table.setstyle('products')
        table.setrepeatRows(1)
        table.addElement(row)
        trows = 0
        for line in results:
            trows += 1
            row = utilRML_std.tr()
            #node_line = etree.Element("row")
            count = -1
            for elem in line:
                if elem == 'None' or elem == 'False':
                    elem = ''
                else:
                    elem = re.sub('&','', elem)
                count += 1
                context = {}
                if temp[count] in (1,2,3,4): ####aqui van los integers y floats y pct
                    if not elem:
                        elem = 0
                    try:
                        ss = float(elem or 0)
                    except:
                        ss = 0
                    if temp[count] in (2 ,4):
                        tsum[count] = float(tsum[count])  + ss
                    if temp[count] in (3 , 4):
                        elem = str('%.2f'%float(elem)) + ' %'
                    row.addElement(self.add_row_element( uid, elem, para_col_tag, count, temp[count]))
                else:
                    row.addElement(self.add_row_element( uid, elem, para_col_tag, count))
            table.addElement(row)
            
        ####totales
        row = utilRML_std.tr()
        total = 0
        for aa in tsum:
            total += aa
        if total:
            for f in range(0,count+1):
                context = {}
                if tsum[f] != None:
                   if (tsum[f] >= 0.01) and (temp[f] == 2) :
                       prec = '%.' +  str(2)  + 'f'
                       total = prec%(tsum[f])
                       txt = str(total or '')
                   else:
                       txt = str(tsum[f] or '')
                else:
                    txt = ' '
                if f == 0:
                    txt ='Total'
                if temp[f] == 4:
                    prec = '%.' +  str(2)  + 'f'
                    total = prec%(tsum[f]/trows)
                    txt = str(total or '') + ' %'
                row.addElement(self.add_row_element( uid, self.comma_me(txt), para_col_tag, f))
                #row.addElement(self.comma_me(txt) or '', context)
            table.addElement(row)
        story.addElement(table)

        doc = utilRML_std.document()
        doc.setfilename(self.title)
        template = utilRML_std.template()
        template.settitle(self.title)
        template.setpageSize(model_brw.page_size, model_brw.portrait)
        template.setrotation(model_brw.rotation)
        pageTemplate = utilRML_std.pageTemplate()
        pageTemplate.setid('first')
        frame = utilRML_std.frame()
        frame.setx1(model_brw.margin_x)
        frame.sety1(model_brw.margin_y)
        frame.setsize(model_brw.page_size, model_brw.portrait)
        pageGP = utilRML_std.pageGraphics()
        if model_brw.count_pages:
            drawString = utilRML_std.drawString()
            drawString.sety('10')
            drawString.setx('10')
            drawString.addElement("Pag.: '<pageNumber/>'")
            pageGP.addElement(drawString)
        pageTemplate.addElement(frame)
        pageTemplate.addElement(pageGP)
        template.addElement(pageTemplate)
        #template = utilRML_std.getdefaultTemplate(table_functions['page'], table_functions['portrait'])
        doc.addElement(template)
        doc.addElement(stylesheet)
        doc.setnoClosing()
        rml2 = `doc` + `story` + '</document>\n'
        self.obj = render.rml(rml2, title=self.title)
        self.obj.render()
        return True
    
report_printscreen_list('report.query.print.report')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
