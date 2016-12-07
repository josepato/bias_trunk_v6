# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from osv import osv
import text
import pooler

# def _sum_trampas(self, form, ids={}, done = None, level=1):
# 		print ' aver si manda los ids', ids
# 		print 'form', form
# 		print 'done', done
# 		print 'level', level
# 		print 'self', self
	


class order(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(order, self).__init__(cr, uid, name, context)
		#trampas = self._sum_trampas(self,obj)
		self.localcontext.update({
			'time': time,
			'trampas': self._sum_trampas,
			'atribut': self._check_atribut,
			'metodo': self._method_name,
			'damage': self._damage_name,
			'evidence': self._evidence_name
			})

	def _sum_trampas(self,  obj, i):
		query =  'SELECT count(equipment_type_id) from contracts_equipment where equipment_type_id = %i and contract_id = %i'%(i,obj)
		self.cr.execute(query)
		total_eq = self.cr.fetchone()[0]
		return total_eq

	def _method_name(self,  obj, ):
		dirr = {'1':'Grietas y Hendiduras',
			'2':'Bandeo Interior',
			'3':'Bandeo Exterior',
			'4':'Nebulizacion',
			'5':'Aerosol',
			'6':'Inpeccion',
			'7':'Colocacion Gomas',
			'8':'Superficie General',
			'9':'Bomba a Motor',
			'10':'Cebado con Gel',
			'11':'Cebado con Granulos',
			'12':'Cebado para Roedores',
			'13':'Espolvoreo'}
		return dirr[str(obj)]

	def _check_atribut(self, obj, i):
		query = ('select atribut_checked,  atribut_value from service_order_equipment_inspection where name = %i and  equipment_atribut_id =%i;'%(obj, i))
		self.cr.execute(query)
		atribut = self.cr.fetchone()
		print 'atribut', atribut
		if atribut[1]:
			return atribut[1] 
		elif atribut[0] == 1:
			return "x"
		else:
			return "-"
			 

	def _damage_name(self,  obj, ):
		dirr = {'1':'Roeduras',
			'2':'Perforacion de Empaque',
			'3':'Contaminacion',
			'4':'Mal Aspecto'}
		
		return dirr[str(obj)]

	
	def _evidence_name(self,  obj, ):
		dirr = {'1':'Excretas',
			'2':'Manchas',
			'3':'Organismo Muerto',
			'4':'Organismo Vivo',
			'5':'Exoesqueleto'}
		
		return dirr[str(obj)]
			



report_sxw.report_sxw('report.service.order','service.order','addons/bias_contracts/report/order.rml',parser=order,header=False)

report_sxw.report_sxw('report.service.order.hand','service.order','addons/bias_contracts/report/order_by_hand.rml',parser=order,header=False)

report_sxw.report_sxw('report.equipment.report','service.order','addons/bias_contracts/report/equipment_report.rml',parser=order,header=False)

report_sxw.report_sxw('report.activity.report','contracts.order','addons/bias_contracts/report/activity__report.rml',parser=order,header=False)

report_sxw.report_sxw('report.aplication.report','contracts.order','addons/bias_contracts/report/aplication_report.rml',parser=order,header=False)


