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

import time
from report import report_sxw

class consumo_suc(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(consumo_suc, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'lines': self.lines,
			'sum_debit_account': self._sum_debit_account,
			'sum_credit_account': self._sum_credit_account,
			'sum_debit': self._sum_debit,
			'sum_credit': self._sum_credit,
			'category': self._category,
			'periods': self._periods,
		})
		self.context = context

        def _get_child(self, parent):
                obj = self.pool.get('product.category')
                childs = []
                categ_id = obj.search(self.cr, self.uid, [])
                for c in categ_id:
                        if parent == obj.browse(self.cr, self.uid, c).parent_id.id:
                                childs.append(c)
                return childs

        def _category(self,form):
                print "category form = ",form
                if not form['category']:
                        categ_name = "Todas"
                        print "raul categ name = ",categ_name                        
                else:                
                        obj = self.pool.get('product.category')
                        categ_name = obj.browse(self.cr, self.uid, form['category']).name                
                        print "raul categ_name ",categ_name
                        categ_in = form['category']
                        print "raul categ name = ",categ_name
                return categ_name

        def _periods(self,form):
                if not form['periods'][0][2]:
                        period_name = "Todos"
                else:                
                        obj = self.pool.get('account.period')
                        periods = form['periods'][0][2]
                        todo = " "
                        for period in periods:
                                print "period = ",obj.browse(self.cr, self.uid, period).code
                                todo += obj.browse(self.cr, self.uid, period).code + ", "
                        period_name = todo
                        
                return period_name

        def raul_category(self,form):
                print "category form = ",form
#               if not form['category']:
#                        categ_name = "Todas"
#                        return categ_name
                obj = self.pool.get('product.category')
                categ_name = obj.browse(self.cr, self.uid, form['category']).name                
                print "raul categ_name ",categ_name
                categ_in = form['category']
                if categ_in == 0:
                        categ_name = "Todas"
                print "raul categ name = ",categ_name
                return categ_name

	def lines(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)

		categ_in = form['category']		
                childs = self._get_child(categ_in)
                for i in childs:
                        parent = self._get_child(i)
                        if parent:
                                childs += parent
                childs += [categ_in]
                print 'childs=',childs   
                categ_in = form['category']
                self.cr.execute("SELECT l.date, j.code, l.ref, l.name, l.debit, l.credit, l.quantity "\
                        "FROM account_move_line l, account_journal j "\
			"WHERE l.name in (SELECT name from product_template q WHERE q.categ_id in (SELECT a.id from product_category a where a.parent_id = %d) ) AND l.journal_id = j.id "\
				"AND account_id = %d AND "+query+" "\
			"ORDER by l.id", (categ_in,account.id,))
                if categ_in == 0:
                        self.cr.execute("SELECT l.date, j.code, l.ref, l.name, l.debit, l.credit, l.quantity "\
                                "FROM account_move_line l, account_journal j "\
                                "WHERE l.journal_id = j.id "\
				"AND account_id = %d AND "+query+" "\
                                "ORDER by l.id", (account.id,))
		
		res = self.cr.dictfetchall()
		sum = 0.0
		for l in res:
			sum += (l['debit'] or 0.0) - (l['credit'] or 0.0)
			l['progress'] = sum
		return res

	def _sum_debit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		categ_in = form['category']	
#		self.cr.execute("SELECT sum(debit) "\
#				"FROM account_move_line l "\
#				"WHERE l.account_id = %d AND "+query, (account.id,))
		self.cr.execute("SELECT sum(l.debit) "\
                                "FROM account_move_line l, account_journal j "\
                                "WHERE l.name in (SELECT name from product_template q WHERE q.categ_id in (SELECT a.id from product_category a where a.parent_id = %d) ) AND l.journal_id = j.id "\
				"AND account_id = %d AND "+query, (categ_in,account.id,))
                if categ_in == 0:
                       	self.cr.execute("SELECT sum(debit) "\
                                "FROM account_move_line l "\
                                "WHERE l.account_id = %d AND "+query, (account.id,))                        
		return self.cr.fetchone()[0] or 0.0

	def _sum_credit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		categ_in = form['category']	
		self.cr.execute("SELECT sum(l.credit) "\
                                "FROM account_move_line l, account_journal j "\
                                "WHERE l.name in (SELECT name from product_template q WHERE q.categ_id in (SELECT a.id from product_category a where a.parent_id = %d) ) AND l.journal_id = j.id "\
				"AND account_id = %d AND "+query, (categ_in,account.id,))
                if categ_in == 0:
                       	self.cr.execute("SELECT sum(credit) "\
                                "FROM account_move_line l "\
                                "WHERE l.account_id = %d AND "+query, (account.id,))
		return self.cr.fetchone()[0] or 0.0

	def _sum_debit(self, form):
		if not self.ids:
			return 0.0
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(debit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id in ("+','.join(map(str, self.ids))+") AND "+query)
		return self.cr.fetchone()[0] or 0.0

	def _sum_credit(self, form):
		if not self.ids:
			return 0.0
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(credit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id in ("+','.join(map(str, self.ids))+") AND "+query)
		return self.cr.fetchone()[0] or 0.0

report_sxw.report_sxw('report.account.consumo.suc', 'account.account', 'addons/bias_account/report/consumo_suc.rml', parser=consumo_suc, header=False)

