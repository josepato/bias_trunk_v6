# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenBIAS S. de R.L. de C.V. (http://bias.com.mx)
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

MAKEINDEX = 0
MODELINDEX = 1
SUBMODELINDEX = 2
ENGINEINDEX = 3
NAMEINDEX = 4


OPENPREFIX = "aaia"
COMPLEXTYPES = ['one2many', 'many2many']
MAINTABLE = 'vehicle'
MAINMODEL = OPENPREFIX + "." + MAINTABLE
MAINMODELNAME = OPENPREFIX + "_" + MAINTABLE

UID = 1
PASSWD = 'exime497263'

### ORDER IS IMPORTANT !!!!
TableList = ['steeringtype',
             'steeringsystem',
             'steeringconfig',
             'brakesystem',
             'brakeabs',
             'braketype',
             'brakeconfig',
             'enginedesignation',
             'enginevin',
             'enginebase',
             'fueldeliverytype',
             'fueldeliverysubtype',
             'fuelsystemcontroltype',
             'fuelsystemdesign',
             'fueldeliveryconfig',
             'aspiration',
             'cylinderheadtype',
             'fueltype',
             'ignitionsystemtype',
             'mfr',
             'engineversion',
             'engineconfig',
             'bedlength',
             'bedtype',
             'bedconfig',
             'year',
             'make',
             'vehicletype',
             'model',
             'basevehicle',
             'submodel',
             'region',
             'bodynumdoors',
             'bodytype',
             'bodystyleconfig',
             'drivetype',
             'mfrbodycode',
             'springtype',
             'springtypeconfig',
             'transmissiontype',
             'transmissionnumspeeds',
             'transmissioncontroltype',
             'transmissionbase',
             'transmissionmfrcode',
             'transmission',
             'wheelbase',
             'vehicle']

Many2ManyList = ['vehicletobedconfig',
                 'vehicletobodystyleconfig',
                 'vehicletobrakeconfig',
                 'vehicletodrivetype',
                 'vehicletoengineconfig',
                 'vehicletomfrbodycode',
                 'vehicletospringtypeconfig',
                 'vehicletosteeringconfig',
                 'vehicletotransmission',
                 'vehicletowheelbase']

ExtraFields = {'vehicle': ['year_id', 'make_id', 'model_id']}


def getIntervals(ll):
    mylist = list(set(ll))  ## remove duplicates
    mylist.sort()
    retlist = []
    curlist = []
    for ix in range(len(mylist)-1):
        curlist.append(mylist[ix])
        if mylist[ix+1] - mylist[ix] != 1:
            retlist.append(curlist)
            curlist = []
    curlist.append(mylist[-1])
    retlist.append(curlist)
    return retlist

class product_product(osv.osv):
    def getProductImages(self, cr, uid, ids, context=None):
        import os
        res = self.read(cr, uid, ids, ['product_tmpl_id', 'image_ids'])
        for item in res:
            item['uris'] = []
            company_id = self.pool.get('product.template').read(cr, uid, item['product_tmpl_id'][0], ['company_id'])['company_id'][0]
            base_uri = self.pool.get('res.company').read(cr, uid, company_id, ['local_media_repository'])['local_media_repository']
            for image_id in item['image_ids'][:]:
                fname = base_uri + '/' + self.pool.get('product.images').read(cr, uid, image_id, ['filename'])['filename']
                item['uris'].append(fname)
            del item['image_ids']
        return res

    _inherit = "product.product"
    _columns = {'partcode': fields.text('EAN'),
                #'product_apply_line': fields.one2many('aaia.product.apply.line', 'product_id', 'Application'),
                'sale_ok': fields.boolean('Can be Sold', help="Determines if the product can be visible in the list of product within a selection from a sale order line.")
                }
product_product()

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {'product_apply_line': fields.one2many('aaia.product.apply.line', 'template_id', 'Application')}

product_template()


class aaia_product_apply_line(osv.osv):
    ## Method needed to speed things up
    def getYears(self, cr, uid, context=None):
        ## Try a search to check permissions, etc...
        test = self.search(cr, uid, [], limit=1, context=context)
        query = "SELECT DISTINCT(year_id) from aaia_product_apply_line"
        cr.execute(query)
        res = cr.fetchall()
        return [x[0] for x in res]

    ## Method needed to speed things up
    def getMakeIds(self, cr, uid, yearid, context=None):
        ## Try a search to check permissions, etc...
        test = self.search(cr, uid, [], limit=1, context=context)
        innerquery = "SELECT id from aaia_product_apply_line WHERE year_id = %i" %(yearid, )
        query = "SELECT DISTINCT(make_id) FROM aaia_product_apply_line WHERE id IN (%s)" %(innerquery, )
        cr.execute(query)
        res = cr.fetchall()
        return [x[0] for x in res]

    def getXml(self, cr, uid, ids, context=None):
        from lxml import etree
        import time
        if type(ids) != list:
            ids = [ids]
        aces = etree.Element("ACES")
        aces.set("version", "3.0")
        header = etree.SubElement(aces, "Header")
        company = etree.SubElement(header, "Company")
        company.text = "Pioneer Automotive Industries LLC"
        doctitle = etree.SubElement(header, "DocumentTitle")
        doctitle.text = "Pioneer Parts Catalog"
        effdate = etree.SubElement(header, "EffectiveDate")
        effdate.text = "{tt[0]}-{tt[1]:02}-{tt[2]:02}".format(tt=time.localtime())
        qdbverdate = etree.SubElement(header, "QdbVersionDate")
        qdbverdate.text = "2011-04-29"
        submissiontype = etree.SubElement(header, "SubmissionType")
        submissiontype.text = "FULL"
        transfdate = etree.SubElement(header, "TransferDate")
        transfdate.text = effdate.text
        vcdbverdate = etree.SubElement(header, "VcdbVersionDate")
        vcdbverdate.text = "2011-04-29"
        app_brw = self.browse(cr, uid, ids)
        appcount = 0
        tmpdict = {}
        for appline in app_brw:
            mykey = (appline.make_id.id, appline.model_id.id, appline.submodel_id.id, appline.engine_id.enginebaseid.id, appline.product_id.name)
            if mykey in tmpdict.keys():
                tmpdict[mykey].append(appline.year_id.id)
            else:
                tmpdict[mykey] = [appline.year_id.id]
        for mykey in tmpdict.keys():
            for yearlist in getIntervals(tmpdict[mykey]):
                appcount += 1
                myapp = etree.SubElement(aces, "App")
                myapp.set("id", str(appcount))
                myapp.set("action", "A")
                myyear = etree.SubElement(myapp, "Years")
                myyear.set("from", str(yearlist[0]))
                myyear.set("to", str(yearlist[-1]))
                mymake = etree.SubElement(myapp, "Make")
                mymake.set("id", str(mykey[MAKEINDEX]))
                mymodel = etree.SubElement(myapp, "Model")
                mymodel.set("id", str(mykey[MODELINDEX]))
                mysubmodel = etree.SubElement(myapp, "Submodel")
                mysubmodel.set("id", str(mykey[SUBMODELINDEX]))
                myenginebase = etree.SubElement(myapp, "EngineBase")
                myenginebase.set("id", str(mykey[ENGINEINDEX]))
                mypart = etree.SubElement(myapp, "Part")
                mypart.text = mykey[NAMEINDEX]
        return etree.tostring(aces, pretty_print=True, encoding="iso-8859-1", xml_declaration=True)


    _name = 'aaia.product.apply.line'
    _inherits = {'product.template': 'template_id'}
    #_inherits = {'product.product': 'product_id'}
    _columns = {#'product_id': fields.many2one('product.product', 'Product Template'),
                'template_id': fields.many2one('product.template', 'Product Template'),
                'name': fields.text('Name'),
                'year_id': fields.many2one('aaia.year', 'Year'),
                'make_id': fields.many2one('aaia.make', 'Make'),
                'model_id': fields.many2one('aaia.model', 'Model'),
                'submodel_id': fields.many2one('aaia.submodel', 'Submodel'),
                'engine_id': fields.many2one('aaia.engineconfig', 'Engine'),
                'drivetype_id': fields.many2one('aaia.drivetype', 'Drive type'),
                'transmission_ids': fields.many2one('aaia.transmission', 'Transmission')
                }
    _sql_constraints = [
        ('aaia_product_apply_line_uniq', 'unique(template_id, year_id, make_id, model_id, submodel_id, engine_id, drivetype_id, transmission_ids)', 'The combination of template, year, make, model, submodel, engine, drivetype and transmission must be unique !')
    ]

    _order = 'product_id'
aaia_product_apply_line()


class aaia_vehicleengine(osv.osv):
    def _getAllValues(self, cur, tablename, colname):
        query = "SELECT %s FROM %s" %(colname, tablename)
        cur.execute(query)
        return tuple([x[0] for x in cur.fetchall()])

    def _getPrimaryKey(self, cr, uid, tablename):
        olap_obj = self.pool.get("olap.database.tables")
        idlist = olap_obj.search(cr, uid, [('name', '=' , tablename)])
        olap_obj = self.pool.get("olap.database.columns")
        idlist = olap_obj.search(cr, uid, [('table_id', '=', idlist[0]), ('primary_key', '=', True)])
        return olap_obj.read(cr, uid, idlist, ['name'])[0]['name']

    def _getFieldNamesAndTypesFromModel(self, cur, modelname):
        query = "SELECT name, ttype FROM ir_model_fields WHERE model='%s'" %(modelname, )
        cur.execute(query)
        return tuple([tuple([x[0], x[1]]) for x in cur.fetchall()])

    def _getSingleValueFromColValue(self, cur, tablename, colname, valuecol, value):
        if type(value) == str:
            query = "SELECT %s FROM %s where %s='%s'" %(colname, tablename, valuecol, value)
        else:
            query = "SELECT %s FROM %s where %s=%s" %(colname, tablename, valuecol, value)
        cur.execute(query)
        return cur.fetchall()[0][0]

    def _setIdValue(self, cur, tablename, refcolname, refcolvalue, value):
        indexname = tablename + '_id_seq'
        query = "ALTER SEQUENCE %s RESTART %i" %(indexname, value+1)
        cur.execute(query)
        cur.execute('commit')
        if type(refcolvalue) == str:
            query = "UPDATE %s SET id=%s WHERE %s='%s'" %(tablename, value, refcolname, refcolvalue)
        else:
            query = "UPDATE %s SET id=%s WHERE %s=%s" %(tablename, value, refcolname, refcolvalue)
        cur.execute(query)
        cur.execute('commit')

    def createDB(self, cr, uid, attach_id, dbname):
        import base64, tempfile
        from subprocess import Popen, PIPE
        attach_obj = self.pool.get("ir.attachment")
        mydata = base64.standard_b64decode(attach_obj.read(cr, uid, attach_id, ['datas'])['datas'])
        basefname = tempfile.mktemp()
        gzfname = basefname + '.gz'
        open(gzfname, 'w').write(mydata)
        cmdstr = "gunzip %s" %(gzfname, )
        pp = Popen(cmdstr.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        (outdata, errdata) = pp.communicate()
        if pp.returncode:
            raise osv.except_osv(('Error !'), ('Error en la creacion de archivo temporal\n' + errdata))
        cmdstr = "createdb %s" %(dbname, )
        pp = Popen(cmdstr.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        (outdata, errdata) = pp.communicate()
        if pp.returncode:
            raise osv.except_osv(('Error !'), ('Error en la creacion de base de datos\n' + errdata))
        cmdstr = "psql -d %s -f %s" %(dbname, basefname)
        pp = Popen(cmdstr.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        (outdata, errdata) = pp.communicate()
        if pp.returncode:
            raise osv.except_osv(('Error !'), ('Error en la creacion de base de datos\n' + errdata))
        else:
            return True

    def _getNewItems(self, oldcur, newcur, oldtable, newtable, oldcols, newcols):
        query = "select %s from %s" %(', '.join(oldcols), oldtable)
        oldcur.execute(query)
        oldlist = oldcur.fetchall()
        query = "select %s from %s" %(', '.join(newcols), newtable)
        newcur.execute(query)
        newlist = newcur.fetchall()
        return list(set(newlist).difference(oldlist))

    def _getColNames(self, cur, tablename):
            query = "SELECT * FROM %s LIMIT 1" %(tablename, )
            cur.execute(query)
            xxx = cur.fetchall()
            return tuple([x[0] for x in cur.description])

    def _insertValues(self, cur, tablename, cols):
        for i in range(len(cols[0])):
            query = "INSERT INTO %s VALUES %s" %(tablename, cols[i])
            cur.execute(query)
            cur.execute("commit")

    def updateFromDataBase(self, cr, uid, dbname):
        import psycopg2
        newcur = psycopg2.connect(database=dbname).cursor()
        gonelist = self._getNewItems(oldcur=newcur, newcur=cr,
                                oldtable='vehicle', newtable='aaia_vehicle',
                                oldcols=('vehicleid', ), newcols=('id', ))
        addlist = self._getNewItems(oldcur=cr, newcur=newcur,
                               oldtable='aaia_vehicle', newtable='vehicle',
                               oldcols=('id', ), newcols=('vehicleid', ))
        vehicledir = {'gonelist': gonelist, 'addlist': addlist}
        #return vehicledir
        addlist = self._getNewItems(oldcur=cr, newcur=newcur,
                               oldtable='aaia_vehicle', newtable='vehicle',
                               oldcols=('id', ), newcols=('vehicleid', ))
        for table in TableList:
            print "Processing", table
            opentablename = OPENPREFIX + "_" + table
            openmodelname = OPENPREFIX + "." + table
            primarykey = self._getPrimaryKey(cr, uid, table)
            mylist = self._getNewItems(oldcur=cr, newcur=newcur,
                                  oldtable=opentablename, newtable=table,
                                  oldcols=('id', ), newcols=(primarykey, ))
            idlist = [x[0] for x in mylist]
            print "Adding %i elements to table %s" %(len(idlist), opentablename)
            fieldlist = self._getFieldNamesAndTypesFromModel(cr, openmodelname)
            idlist.sort()  #### IMPORTANT !!!
            for itemid in idlist:
                mydict = {primarykey: itemid}
                if table + 'name' in [x[0] for x in fieldlist]:
                    fieldname = table + 'name'
                    mydict['name'] = self._getSingleValueFromColValue(newcur, table, fieldname, primarykey, itemid)
                for fieldname, fieldtype in fieldlist:
                    if fieldname == 'name':
                        continue
                    if table in ExtraFields.keys() and fieldname in ExtraFields[table]:
                        continue
                    if not fieldtype in COMPLEXTYPES:
                        ### select fieldname from table where primarykey=itemid
                        myval = self._getSingleValueFromColValue(newcur, table, fieldname, primarykey, itemid)
                        if myval != None:
                            mydict[fieldname] = myval
                myid = self.pool.get(openmodelname).create(cr, uid, mydict)
                if myid != itemid:
                    self._setIdValue(cr, opentablename, primarykey, itemid, itemid)   # MUST BE ORDERED !!!
        for table in Many2ManyList:
            colname1, colname2 = self._getColNames(cr, table)
            col1 = self._getAllValues(newcur, table, colname1)
            col2 = self._getAllValues(newcur, table, colname2)
            newlist = self._getNewItems(oldcur=cr, newcur=newcur,
                                        oldtable=table, newtable=table,
                                        oldcols=(colname1, colname2), newcols=(colname1, colname2))
            print "Processing %s.    Inserting %i new rows." %(table, len(newlist))
            self._insertValues(cr, table, newlist)
        res = self.pool.get('aaia.vehicle').read(cr, uid, addlist, ['engineconfig',
                                                                    'basevehicleid',
                                                                    'submodelid',
                                                                    'drivetype',
                                                                    'transmission'])
        print "Adding %i new lines." %(len(res), )
        for item in res:
            myres = self.pool.get('aaia.basevehicle').read(cr, uid, item['basevehicleid'][0], ['yearid', 'makeid', 'modelid'])
            for ii in item['engineconfig']:
                for jj in item['drivetype']:
                    newid = self.pool.get('aaia.vehicleengine').create(cr, uid, {'vehicle_id': item['id'],
                                                                                 'engine_id': ii,
                                                                                 'drivetype_id': jj,
                                                                                 'year_id': myres['yearid'][0],
                                                                                 'make_id': myres['makeid'][0],
                                                                                 'model_id': myres['modelid'][0],
                                                                                 'submodel_id': item['submodelid'][0],
                                                                                 'transmission_ids': [(6, 0, item['transmission'])]})

        return True

    _name = 'aaia.vehicleengine'
    _columns = {'product_id': fields.many2many('product.product',
                                               'product_vehicleengine_rel',
                                               'productid',
                                               'vehicleid',
                                               'Product'),
                'name': fields.text('Name'),
                'vehicle_id': fields.many2one('aaia.vehicle', 'Vehicle'),
                'engine_id': fields.many2one('aaia.engineconfig', 'Engine'),
                'year_id': fields.many2one('aaia.year', 'Year'),
                'make_id': fields.many2one('aaia.make', 'Make'),
                'model_id': fields.many2one('aaia.model', 'Model'),
                'submodel_id': fields.many2one('aaia.submodel', 'Submodel'),
                'drivetype_id': fields.many2one('aaia.drivetype', 'Drive type'),
                'transmission_ids': fields.many2many('aaia.transmission',
                                                     'vehicleengine_transmission_rel',
                                                     'vehicleengineid',
                                                     'transmissionid',
                                                     'Transmission')
                }
aaia_vehicleengine()


