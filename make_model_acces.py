##############################################################################
#
# Copyright (c) 2007 TINYERP SA DE CV (http://tinyerp.mx) All Rights Reserved.
#                    Jose Patricio Villarreal  <josepato@bias.com.mx>
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

import os, csv, re


readFiel = os.popen('zenity --info --text="Seleccione Archivo al cual se va a hacer el security."','r')

readFiel = readFiel.read()

readFiel = os.popen('zenity --file-selection','r')
filefid = readFiel.read().rstrip('\n')


path = filefid[:filefid.rfind('/')]
w_file = filefid[filefid.rfind('/'):][1:]

has_securty = os.popen('ls %s'%path)
has_securty =  has_securty.read().split('/')
if 'security' not in has_securty:
    os.popen('mkdir %s/security'%path)


group_name = os.popen('zenity --entry --text="Introduca el nombre del grupo" --entry-text="group_"')
group_name = group_name.read().strip('\n')

permitions = {group_name +'_user':[1,1,0,0],
              group_name +'_manager':[1,1,1,1],
              }


groups = permitions.keys()

models  = os.popen('grep class %s/%s'%(path,w_file))

classes = models.read()
classes = classes.split('\n')

model_file = csv.writer(open('%s/security/ir.model.access.csv'%(path), 'wb'), delimiter=',', quotechar ='"')
title = ['id','name','model_id:id','group_id:id','perm_read','perm_write','perm_create','perm_unlink']
model_file.writerow(title)


for group in groups:
    for table in classes:
        line = re.sub('class','model_',table)
        line_access = re.sub('class','access_',table)
        line_access = re.sub(' ','',line_access)[:-10]
        line = re.sub(' ','',line)[:-10]
        line_id = re.sub('_','.', line)[6:]
        row = [line_access ,
               line_id,
               line,
               w_file.split('.')[0] +'.' + group,
               permitions[group][0],
               permitions[group][1],
               permitions[group][2],
               permitions[group][3],
               ]
        model_file.writerow(row)
    

readFiel = os.popen('zenity --info --text="Listo!!!"','r')

os.popen('ooffice %s/security/ir.model.access.csv'%path)
