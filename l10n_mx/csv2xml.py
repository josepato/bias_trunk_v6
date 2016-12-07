##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

import csv
import re
import types

def csv2xml(catalogo):
    spamReader = csv.reader(open(catalogo), delimiter=',', quotechar='"')
    i = 0
    result = []
    parent_code_1 = False
    parent_code_2 = False
    parent_code_3 = False
    parent_code_4 = False
    for row in spamReader:
        i +=1
        if i < 7:
            continue
        if row[0] == '1':
            row = strip(row,1)
            row[0] = 'view'
            row[3] = 'user_type_view'
            row[7] = ''
            parent_code_1  = row[1]
            row.append('_root')
            result.append(row)
        elif row[0].strip('" ') == '2':
            row = strip(row,2)
            row[0] = 'view'
            row[3] = 'user_type_view'
            row[7] = ''
            parent_code_2  = row[1]
            row.append(parent_code_1)
            result.append(row)
        elif row[0].strip('" ') == '3':
            count = 0
            row = strip(row,3)
            row[0] = 'other'
            row[3] = 'user_type_other'
            parent_code_3 = row[1]
            row.append(parent_code_2)
            if row[1] == '201-0000':
                print 'row strip=', row
            result.append(row)
        elif row[0].strip('" ') == '4':
            count = 0
            print 'row=',row
            row = strip(row,4)
            row[0] = 'other'
            row[3] = 'user_type_other'
            parent_code_4 = row[1]
            row.append(parent_code_3)
            if parent_code_3 == '201-0000':
                print 'row strip=', row
            result.append(row)
        elif row[0].strip('" ') == '5':
            count = 0
            row = strip(row,5)
            row[0] = 'other'
            row[3] = 'user_type_other'
            row.append(parent_code_4)
            result.append(row)
        else:
            print ' falla=',row
    buff = open('account.xml','w')   
    xmlData = '<?xml version="1.0" encoding="utf-8"?>\n<openerp>\n    <data noupdate="1">\n' \
    '<!-- \naccount.account.template\nChart template of l10n_mx\nAccount template definition\n-->\n\n' \
    '       <record id="a_root" model="account.account.template">\n' \
    '           <field name="code">0</field>\n' \
    '           <field name="name">Catalogo Contable</field>\n' \
    '           <field name="type">view</field>\n' \
    '           <field name="user_type" ref="user_type_view"/>\n' \
    '       </record>\n'

    for data in result:
        csvData = ''
        record = _process_data(data)
        for d in data:
            if type(d).__name__ == 'unicode':
                d = d.encode('utf-8')
            if type(d)==types.StringType:
                csvData += (csvData and ',' or '') + '"' + str(d.replace('\n',' ').replace('\t',' ')) + '"'
            else:
                csvData += (csvData and ',' or '') + str(d)
        currency = (record[7] and '         <field name="currency_id">2</field>\n') or ''
        xmlData += '' \
        '       <record id="' +'a' + record[1] + '" model="account.account.template">\n' \
        '           <field name="code">' + record[1] + '</field>\n' \
        '           <field name="name">' + record[2] + '</field>\n' \
        '           <field name="type">' + record[0] + '</field>\n' \
        '           <field name="user_type" ref="' + record[3] + '"/>\n' \
        '' + currency + '' \
        '           <field name="parent_id" ref="' +'a' + record[9] + '"/>\n' \
        '       </record>\n'

    xmlData += '    </data>\n</openerp>'
    buff.write(xmlData)
    buff.close()

def _process_data(data):
    count = 0
    for d in data:
        if type(d).__name__ == 'unicode':
            d = d.encode('utf-8')
        if type(d)==types.StringType:
            data[count] = str(d.replace('\n',' ').replace('\t',' '))# + '"'
        else:
            data[count] = str(d)
        count += 1
    return data

def strip(row, label):
    count = 0
    for data in row:
        row[count] = row[count].rstrip('" ')
        row[count] = row[count].lstrip('" ')
        if (count == 7) and (label == 3):
            if row[count] == 'Pesos':
                row[count] = ''
            else:
                row[count] = 'USD'
        count += 1
    return row


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

