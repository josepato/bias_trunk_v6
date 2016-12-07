##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import datetime
from mx.DateTime import *
import re
from osv import osv
import pooler

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'

def _get_lang_dict(cr, uid, lang_dict):
	pool = pooler.get_pool(cr.dbname)
        pool_lang = pool.get('res.lang')
	lang = pool.get('res.users').browse(cr, uid, uid).context_lang
	print 'lang=',lang
#        lang = localcontext.get('lang', 'en_US') or 'en_US'
        lang_ids = pool_lang.search(cr, uid, [('code','=',lang)])[0]
        lang_obj = pool_lang.browse(cr, uid, lang_ids)
        lang_dict.update({'lang_obj':lang_obj,'date_format':lang_obj.date_format,'time_format':lang_obj.time_format})
#        default_lang[lang] = lang_dict.copy()
#	lang_dict['date_format'] = '%m-%d-%Y'
        return lang_dict

def formatLang(cr, uid, value, digits=2, date=False,date_time=False, grouping=True, monetary=False, currency=None):
	lang_dict_called = False
	lang_dict = {}
        if isinstance(value, (str, unicode)) and not value:
	    print 'return antes'
            return ''
        if not lang_dict_called:
            lang_dict = _get_lang_dict(cr, uid, lang_dict)
            lang_dict_called = True

        if date or date_time:
            if not str(value):
                return ''
            date_format = lang_dict['date_format']
            parse_format = DT_FORMAT
            if date_time:
                date_format = date_format + " " + lang_dict['time_format']
                parse_format = DHM_FORMAT

            # filtering time.strftime('%Y-%m-%d')
            if type(value) == type(''):
                if date_time:
	            parse_format = DHM_FORMAT
#                    return str(value)
            if not isinstance(value, time.struct_time):
                try:
                    date = strptime(str(value),parse_format)
                except:# sometimes it takes converted values into value, so we dont need conversion.
                    return str(value)
            else:
                date = DateTime(*(value.timetuple()[:6]))
            return date.strftime(date_format)
	return lang_dict['lang_obj'].format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)

def salto(i):
        return ". " * i

def moneyfmt(amount, places=2, curr='$', sep=',', dp='.', pos='', neg=''):
        if amount == '':
                return ''
	amount = '%.2f' % float(amount)
        decimal = ((amount))[-3:]
        digits = ((amount))[0:-3]
        result = ''
        l = len(digits)
        if digits[0] == '-':
                l -= 1
                neg = '-'
                digits = digits[1:]
        i = 0
        d = l
        while d > 3:
                d -= 3
        while i < l:
                i += 1
                d -= 1
                result = result + digits[(i-1):i]
                if d == 0 and i < l:
                        d = 3
                        result = result + sep
        return neg + result + decimal

def date_sp(date, completo=0):
        en = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        SP = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        sp = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        spc = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	date_hora = time.strftime('%d-%b-%Y %H:%M:%S', time.strptime(date,'%Y-%m-%d %H:%M:%S'))
	date = (date.split(' ').pop(0))
        date_es = time.strftime('%d-%b-%Y', time.strptime(date,'%Y-%m-%d'))
	try:
        	mes = en.index(date_es[3:6])
	except:
		try:
        		mes = sp.index(date_es[3:6])
		except:
			try:
				mes = SP.index(date_es[3:6])
			except:
				pass
        if completo == 1:
                return date_es[0:2] + ' de ' + spc[mes] + ' de ' + date_es[7:]
	elif completo == 2:
		return date_hora[0:2] + ' de ' + spc[mes] + ' de ' + date_hora[7:]

        return date_es[0:2] + '-' + SP[mes] + '-' + date_es[7:]

def phone(num):
        reemplazables = [' ',',','.',':',';','-','_','#','"','<','>','(','[','{','}',']',')','=']
        for x in reemplazables:
                num = num.replace(x,'')
        if num[0:2] == '01':
                num = num.replace('01','',1)
        if len(num) == 8:
                phonePattern = re.compile(r'''(\d{4})\D*(\d{4})$''')
                num = phonePattern.search(num).groups()
                return '(  ) '+num[0]+'-'+num[1]
        if len(num) == 10:
                phonePattern = re.compile(r'''(\d{2})\D*(\d{4})\D*(\d{4})$''')
                num = phonePattern.search(num).groups()
                return '('+num[0]+') '+num[1]+'-'+num[2]
        if len(num) > 10:
                phonePattern = re.compile(r'''(\d{2})\D*(\d{4})\D*(\d{4})\D*(\d*)$''')
                num = phonePattern.search(num).groups()
                return '('+num[0]+') '+num[1]+'-'+num[2]+' Ext.'+num[3]

unites = {
	0: '', 1:'UN', 2:'DOS', 3:'TRES', 4:'CUATRO', 5:'CINCO', 6:'SEIS', 7:'SIETE', 8:'OCHO', 9:'NUEVE',
	11:'ONCE', 12:'DOCE', 13:'TRECE', 14:'CATORCE', 15:'QUINCE', 16:'DIECISEIS', 17:'DIECISIETE',
        18:'DIECIOCHO', 19:'DIECINUEVE', 21:'VEINTIUN', 22:'VEINTIDOS', 23:'VEINTITRES', 24:'VEINTICUATRO', 25:'VEINTICINCO',
        26:'VEINTISEIS', 27:'VEINTISIETE', 28:'VEINTIOCHO', 29:'VEINTINUEVE'
}

dizaine = {
	1: 'DIEZ', 2:'VEINTE', 3:'TREINTA',4:'CUARENTA', 5:'CINCUENTA', 6:'SESENTA', 7:'SETENTA', 8:'OCHENTA', 9:'NOVENTA'
}

centaine = {
	0:'', 1: 'CIEN', 2:'DOSCIENTOS', 3:'TRECIENTOS',4:'CUATROCIENTOS', 5:'QUINIENTOS', 6:'SEISCIENTOS', 7:'SETECIENTOS',
        8:'OCHOCIENTOS', 9:'NOVECIENTOS'
}

mille = {
	0:'', 1:'MIL'
}


    
def _100_to_text(chiffre):
	if chiffre in unites:
		return unites[chiffre]
	else:
		if chiffre%10>0:
			return dizaine[chiffre / 10]+' Y '+unites[chiffre % 10]
		else:
			return dizaine[chiffre / 10]

def _1000_to_text(chiffre):
	d = _100_to_text(chiffre % 100)
	d2 = chiffre/100
        if d2>0 and d2<2 and d:
		return centaine[d2]+'TO '+d
	elif d2>1 and (d):
		return centaine[d2]+' '+d
	elif d2>1 and not(d):
		return centaine[d2]
	else:
		return centaine[d2] or d

def _10000_to_text(chiffre):
	if chiffre==0:
		return ''
	part1 = _1000_to_text(chiffre % 1000)
	part2 = mille.get(chiffre / 1000,  _1000_to_text(chiffre / 1000)+' MIL')
	if part2 and part1:
		part1 = ' '+part1
	return part2+part1

def text(number):
    	millions = number / 1000000
	if millions: 
		millions = _10000_to_text(number / 1000000) + (millions==1 and ' MILLON ' or ' MILLONES ')
	else:
	    	millions = ''
	return millions + _10000_to_text(number % 1000000)



if __name__=='__main__':
	for i in range(1,999999,139):
		print int_to_text(i)


