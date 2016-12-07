import pooler
import time
from report import report_sxw
import text

class stock(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(stock, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'process':self.process,
                        'date_sp': self.date_sp,
		})

	def process(self,location_id):
		res = {}
		location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
		product_obj = pooler.get_pool(self.cr.dbname).get('product.product')

		res['location_name'] = pooler.get_pool(self.cr.dbname).get('stock.location').read(self.cr, self.uid, [location_id],['name'])[0]['name']

		prod_info = location_obj._product_get(self.cr, self.uid, location_id)
		res['product'] = []
		for prod in product_obj.browse(self.cr, self.uid, prod_info.keys()):
			if prod_info[prod.id]:
                                res['product'].append({'prod_code': prod.code,'prod_name': prod.name, 'prod_qty': prod_info[prod.id]})
                        else:
                                res['product'].append({'prod_code': prod.code,'prod_name': prod.name, 'prod_qty': '0'})
#		if not res['product']:
#			res['product'].append({'prod_code': prod.code,'prod_name': prod.name, 'prod_qty': '0'})
		location_child = location_obj.read(self.cr, self.uid, [location_id], ['child_ids'])
                sort_on="prod_name"
                undecorated=res['product']
                decorated = [(dict_[sort_on], dict_) for dict_ in undecorated]
                decorated.sort()
                result = [dict_ for (key, dict_) in decorated]
                res['product']=result
		list=[]
		list.append(res)
		for child_id in location_child[0]['child_ids']:
				list.extend(self.process(child_id))
		return list

	def date_sp(date, completo=0):
		en = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
		sp = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
		spc = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		date = (date.split(' ').pop(0))
		date_es = time.strftime('%d-%b-%Y', time.strptime(date,'%Y-%m-%d'))
		mes = en.index(date_es[3:6])
		if completo == 1:
			return date_es[0:2] + ' de ' + spc[mes] + ' de ' + date_es[7:]
		return date_es[0:2] + '-' + sp[mes] + '-' + date_es[7:]

report_sxw.report_sxw('report.stock.inventory.bias','stock.location','addons/bias_print_forms/stock/report/stock.rml',parser=stock,header=True)

