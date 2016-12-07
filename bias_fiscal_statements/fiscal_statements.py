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


from osv import osv
from osv import fields
import time

#----------------------------------------------------------
# Account Fiscal Statements
#----------------------------------------------------------
class fiscal_statements(osv.osv):
    _name = "fiscal.statements"
    _description = "Fiscal Statements"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'fiscal_statements_line_id': fields.one2many('fiscal.statements.lines', 'fiscal_statements_id', 'Fiscal Statements Lines'),
        'format' : fields.selection([
                        ('balance', 'Balance Sheet'),
                        ('balance_1', 'Balance Sheet one row'),
                        ('statement', 'Income statement / Statement of earnings')],"Format"),
        'name_1': fields.char('Nombre 1', size=64),
        'name_2': fields.char('Nombre 2', size=64),
        'title_1': fields.char('Titulo 1', size=64),
        'title_2': fields.char('Titulo 2', size=64),
        'message_text': fields.text('Mensaje'),
    }

    def _get_context(self, cr, uid, objects, data, ids, report_type = None):
        ids = [data['form']['fiscal_statements_id']]
        objects = self.browse(cr, uid, ids)
        return objects, ids 

    def _get_company(self, cr, uid, form):
        return self.pool.get('res.company').browse(cr, uid, form['company_id']).name

    def _get_title(self, cr, uid, form):
        return self.browse(cr, uid, form['fiscal_statements_id']).name

    def _get_date_end(self, cr, uid, form):
        date_stop = self.pool.get('account.period').browse(cr, uid, form['period_id']).date_stop
        date_stop = time.strftime('%d-%b-%Y', time.strptime(date_stop,'%Y-%m-%d'))
        return str(date_stop)

    def _process_col1(self, cr, uid, col, account_ids, data):
        format = self.browse(cr, uid, data['form']['fiscal_statements_id']).format
        date_stop = self.pool.get('account.period').browse(cr, uid, data['form']['period_id']).date_stop
        date_start = self.pool.get('account.period').browse(cr, uid, data['form']['period_id']).date_start
        amount_1, amount_2, percent_1, percent_2 = 0, 0, 0, 0
        child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, account_ids)
        cr.execute(
					"SELECT (sum(debit) - sum(credit)) FROM account_move_line " \
					"WHERE account_id IN (" + ','.join(map(str, child_ids)) + ") AND state = 'valid' AND date >= %s AND date <= %s " , \
                    (date_start, date_stop))
        amount_1 = cr.fetchone()[0] or 0.0
        cr.execute(
					"SELECT (sum(debit) - sum(credit)) FROM account_move_line " \
					"WHERE account_id IN (" + ','.join(map(str, child_ids)) + ") AND state = 'valid' AND date <= %s " ,(date_stop,))
        amount_2 = cr.fetchone()[0]
        if col.income:
            self.income_1 = amount_1
            self.income_2 = amount_2
        if self.income_1 and amount_1 and col.display_amount:
            percent_1 = str('%.2f'%(abs(amount_1 / self.income_1 * 100))) + ' %'
        if self.income_2 and amount_2 and col.display_amount:
            percent_2 = str('%.2f'%(abs(amount_2 / self.income_2 * 100))) + ' %'
        if col.invert_sign and col.display_amount:
            amount_1 = amount_1 * -1
            amount_2 = amount_2 * -1
        return col, (col and col.display_amount and amount_1), (col and col.display_amount and percent_1), \
                    (col and col.display_amount and amount_2), (col and col.display_amount and percent_2)

    def _get_lines(self, cr, uid, obj, data):
        lin_obj = self.pool.get('fiscal.statements.lines')
        acc_obj = self.pool.get('account.account')
        self.income_1, self.income_2 = 0, 0
        report = data['form']['fiscal_statements_id']
        format = self.browse(cr, uid, report).format
        full_account = []
        cr.execute(
				"SELECT distinct sequence FROM fiscal_statements_lines " \
				"WHERE fiscal_statements_id = %s " \
				"ORDER BY sequence ", (report,))
        res = map(lambda x: x[0], cr.fetchall() )
        lines_dic = {}
        for sequence in res:
            count = 0
            if format == 'balance':
                if data['form']['level'] == 1:
                    # process column 1
                    col_1 = amount_1 = p_1 = amount_2 = p_2 = False
                    cr.execute(
        			"SELECT id FROM fiscal_statements_lines WHERE fiscal_statements_id = %s and sequence = %s and section = 'column_1' ", \
                    (report,  sequence))
                    line_id = cr.fetchone()
                    if line_id:
                        col = lin_obj.browse(cr, uid, line_id[0])
                        account_ids_report = [x.id for x in col.account_id]
                        col_1, amount_1, p_1, amount_2, p_2 = self._process_col(cr, uid, data, col, account_ids_report)
                    # process column 2
                    col_2 = amount_3 = p_3 = amount_4 = p_4 = False
                    cr.execute(
        			"SELECT id FROM fiscal_statements_lines WHERE fiscal_statements_id = %s and sequence = %s and section = 'column_2' ", \
                    (report,  sequence))
                    line_id = cr.fetchone()
                    if line_id:
                        col = lin_obj.browse(cr, uid, line_id[0])
                        account_ids_report = [x.id for x in col.account_id]
                        col_2, amount_3, p_3, amount_4, p_4 = self._process_col(cr, uid, data, col, account_ids_report)
                    r = { 
                        'font_style_1': (col_1 and col_1.font_style) or False, 
                        'name_1': (col_1 and col_1.display_label and col_1.name) or '', 
                        'amount_1': (col_1 and amount_1) or 0, 
                        'p_1': (col_1 and p_1) or '', 
                        'amount_2': (col_1 and amount_2) or 0, 
                        'p_2': (col_1 and p_2) or '', 
                        'font_style_2': (col_2 and col_2.font_style) or False, 
                        'name_2': (col_2 and col_2.display_label and col_2.name) or '', 
                        'amount_3': (col_2 and amount_3) or 0, 
                        'p_3': (col_2 and p_3) or '', 
                        'amount_4': (col_2 and amount_4) or 0, 
                        'p_4': (col_2 and p_4) or '',
                        'type_1': (col_1 and col_1.state) or '',
                        'type_2': (col_2 and col_2.state) or ''
                        }                     
                    full_account.append(r)
            else:
                cr.execute(
    			"SELECT id FROM fiscal_statements_lines WHERE fiscal_statements_id = %s and sequence = %s and section = 'column_1' ", (report, sequence))
                line_id = cr.fetchone()
                col = lin_obj.browse(cr, uid, line_id[0])
                account_ids_report = [x.id for x in col.account_id]
                account_ids_level = self._process_label(cr, uid, report, sequence, data)
                if not col.level:
                    i = 1
                else:
                    i = len(account_ids_level) <= 1 and 1 or len(account_ids_level) 
                while i > 0: 
                    i -= 1
                    if not col.level:
                        acc = account_ids_report
                    else:
                        acc = [account_ids_level[count]]
                    col_1, amount_1, p_1, amount_2, p_2 = self._process_col(cr, uid, data, col, acc)
                    if not col.level or count == 0:
                        name = col_1 and col_1.display_label and col_1.name
                    else:
                        account = acc_obj.browse(cr, uid, acc[0])
                        name = ' - ' + account.code + ' - ' + account.name
                    r = {
                        'font_style': (col_1 and col_1.font_style) or False, 
                        'name': (name) or '', 
                        'amount_1': (col_1 and amount_1) or 0, 
                        'p_1': (col_1 and p_1) or '', 
                        'amount_2': (col_1 and amount_2) or 0, 
                        'p_2': (col_1 and p_2) or '',
                        'type': (col_1 and col_1.state) or ''
                        }
                    count += 1
                    full_account.append(r)
        return full_account

    def _process_col(self, cr, uid, data, col, account_ids):
        format = self.browse(cr, uid, data['form']['fiscal_statements_id']).format
        date_stop = self.pool.get('account.period').browse(cr, uid, data['form']['period_id']).date_stop
        date_start = self.pool.get('account.period').browse(cr, uid, data['form']['period_id']).date_start
        amount_1, amount_2, percent_1, percent_2 = 0, 0, 0, 0
        QUERY_CC = ""
        if 'cost_center_id' in data['form'] and data['form']['cost_center_id']:
            QUERY_CC = " AND cost_center_id = "+str(data['form']['cost_center_id'])+" "
        # Get list of statement lines
        if account_ids:
            child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, account_ids)
            if child_ids:
                cr.execute(
					"SELECT (sum(debit) - sum(credit)) " \
					"FROM account_move_line " \
					"WHERE account_id IN (" + ','.join(map(str, child_ids)) + ") AND state = 'valid' AND date >= %s AND date <= %s "
                    " "+QUERY_CC+" ", (date_start, date_stop))
                amount_1 = cr.fetchone()[0] or 0.0
                date_start = self.pool.get('account.fiscalyear').browse(cr, uid, data['form']['fiscalyear']).date_start
                cr.execute(
					"SELECT (sum(debit) - sum(credit)) " \
					"FROM account_move_line " \
					"WHERE account_id IN (" + ','.join(map(str, child_ids)) + ") AND state = 'valid' AND date >= %s AND date <= %s "
                    " "+QUERY_CC+" ", (date_start, date_stop))
                amount_2 = cr.fetchone()[0]
                if col.income:
                    self.income_1 = amount_1
                    self.income_2 = amount_2
                if self.income_1 and amount_1 and col.display_amount:
                    percent_1 = str('%.2f'%(abs(amount_1 / self.income_1 * 100))) + ' %'
                if self.income_2 and amount_2 and col.display_amount:
                    percent_2 = str('%.2f'%(abs(amount_2 / self.income_2 * 100))) + ' %'
                if col.invert_sign and col.display_amount:
                    amount_1 = amount_1 and (amount_1 * -1)
                    amount_2 = amount_2 and (amount_2 * -1)
        return col, (col and col.display_amount and amount_1), (col and col.display_amount and percent_1), \
                    (col and col.display_amount and amount_2), (col and col.display_amount and percent_2)
        
    def _process_label(self, cr, uid, report, sequence, data):
        level = data['form']['level']
        res = [] 
        child = True
        cr.execute("SELECT id FROM fiscal_statements_lines WHERE fiscal_statements_id = %s and sequence = %s and section = 'column_1' and level = True " \
				"ORDER BY sequence ", (report, sequence))
        result = cr.fetchone()
        if result:
            col = self.pool.get('fiscal.statements.lines').browse(cr, uid, result[0])
            account_ids = [x.id for x in col.account_id]
            acc = str(account_ids[0])
            res += account_ids
            while child and level > 1 :
                level -= 1
                cr.execute("SELECT id FROM account_account WHERE parent_id in ("+acc+") ")
                child = [x[0] for x in cr.fetchall()]
                acc = ','.join(map(str,child))
                res += child 
            acc = ','.join(map(str,res))
            cr.execute("SELECT id FROM account_account WHERE id in ("+acc+") order by code")
            res = [x[0] for x in cr.fetchall()]
        return res

    def get_result(self, cr, uid, data, context={}):
        format = self.browse(cr, uid, data['form']['fiscal_statements_id']).format
        objects, ids = False, False
        form = data['form']
        objects, new_ids = self._get_context(cr, uid, objects, data, ids, report_type = None)
        result = []
        result += [(self._get_company(cr, uid, data['form']),)]
        result += [(self._get_title(cr, uid, data['form']) + ' al',self._get_date_end(cr, uid, data['form']))]
        if format == 'balance':
            result += [('','Periodo','%','(Acumulado)','%','','Periodo','%','(Acumulado)','%')]
            for p in objects:
                for l in self._get_lines(cr, uid, p, data):
                    result += [(l[1],l[2] or '',l[3] or '',l[4] or '',l[5] or '', \
                                l[7],l[8] or '',l[9] or '',l[10] or '',l[11] or '')]
        else:
            result += [('','Periodo','%','(Acumulado)','%')]
            for p in objects:
                for l in self._get_lines(cr, uid, p, data):
                    result += [(l[1],l[2] or '',l[3] or '',l[4] or '',l[5] or '')]
        return result


fiscal_statements()

class fiscal_statements_lines(osv.osv):
    _name = "fiscal.statements.lines"
    _description = "Fiscal Statements Lines"
    _font = [
             ('',''),
             ('Courier','Courier'),
             ('Courier-Bold','Courier-Bold'),
             ('Courier-BoldOblique','Courier-BoldOblique'),
             ('Courier-Oblique','Courier-Oblique'),
             ('Helvetica','Helvetica'),
             ('Helvetica-Bold','Helvetica-Bold'),
             ('Helvetica-Oblique','Helvetica-Oblique'),
             ('Times-Bold','Times-Bold'),
             ('Times-BoldItalic','Times-BoldItalic'),
             ('Times-Italic','Times-Italic'),
             ('Times-Roman','Times-Roman'),
            ]
    _color = [
            ('', ''),
            ('green','Green'),
            ('red','Red'),
            ('pink','Pink'),
            ('blue','Blue'),
            ('yellow','Yellow'),
            ('cyan','Cyan'),
            ('lightblue','Light Blue'),
            ('orange','Orange'),
            ]
    _style = [
            ('', ''),
            ('h1','Header 1'),
            ('h2','Header 2'),
            ('h3','Header 3'),
            ]

    _columns = {
        'fiscal_statements_id': fields.many2one('fiscal.statements', 'Fiscal Statements', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name', size=64, required=False),
        'code': fields.char('Code', size=64, required=False),
        'account_id': fields.many2many('account.account', 'fiscal_statements_rel', 'report_id', 'account_id', 'Accounts'),
        'note': fields.text('Note'),
        'report_type' : fields.selection([
            ('only_obj', 'Report Objects Only'),
            ('with_account', 'Report Objects With Accounts'),
            ('acc_with_child', 'Report Objects With Accounts and child of Accounts')],"Report Type"),
        'section' : fields.selection([('column_1', 'Column 1'),('column_2', 'Column 2')],"Section"),
        'display_amount': fields.boolean('Display Amount'),
        'display_label': fields.boolean('Display label'),
        'invert_sign': fields.boolean('Invert Sign'),
        'income': fields.boolean('Income'),
        'font_style' : fields.selection(_font, 'Font'),
        'level': fields.boolean('Process level'),
        'state': fields.selection([
                ('article','Objeto'),
                ('title','Titulo'),
                ('text','Nota'),
                ('subtotal','Sub Total'),
                ('line','Linea'),
                ('break','Salto de Pagina'),]
            ,'Tipo', select=True),
#        'color_font' : fields.many2one('color.rml','Font Color'),
#        'color_back' : fields.many2one('color.rml','Back Color'),
    }
    _defaults = {
        'section': lambda *a: 'column_1',
        'sequence': lambda *a: 1,
        'display_amount': lambda *a: True,
        'display_label': lambda *a: True,
        'font_style': lambda *a: 'Helvetica',
        'state': lambda *a: 'article',
    }

    def _check_sequence(self,cr,uid,ids):
        line = self.browse(cr, uid, ids[0])
        cr.execute(
            "select count(sequence) from fiscal_statements_lines " \
            "where fiscal_statements_id = %s and sequence = %s and section = %s " \
            " ", (line.fiscal_statements_id.id, line.sequence, line.section) )
        res= cr.fetchone()[0]
        if res !=1:
            return False
        return True

    _constraints = [
        (_check_sequence, 'Error ! Value combination sequence - section must be unique .', ['sequence'])
    ]


    _order = 'section,sequence'


fiscal_statements_lines()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

