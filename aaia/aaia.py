# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 OpenBIAS S de RL de CV (<http://www.bias.com.mx>). All Rights Reserved
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
#
#Bias Product / PriceList 
#
from osv import osv
from osv import fields
import string


def uniquify(mylist):
    set = {}
    map(set.__setitem__, mylist, [])
    return set.keys()

def make_tuple(ids):
    res = ()
    if len(ids) == 1:
        return '(%s)'%ids[0]
    elif len(ids) >1 :
        for i in ids:
            if i:
                res += (i,)
        return str(tuple(res))
    else:
        return ()



#----------------------------------------------------------
# Users
#----------------------------------------------------------


class aaia_steeringtype(osv.osv):
    _name = 'aaia.steeringtype'
    _columns = {
        'name': fields.text('Name'),
        'steeringconfig': fields.one2many('aaia.steeringconfig', 'steeringtypeid', 'steeringconfig'),
        'steeringtypeid': fields.integer('steeringtypeid'),
        'steeringtypename': fields.text('steeringtypename'),
    }
aaia_steeringtype()

class aaia_brakeabs(osv.osv):
    _name = 'aaia.brakeabs'
    _columns = {
        'name': fields.text('Name'),
        'brakeconfig': fields.one2many('aaia.brakeconfig', 'brakeabsid', 'brakeconfig'),
        'brakeabsid': fields.integer('brakeabsid'),
        'brakeabsname': fields.text('brakeabsname'),
    }
aaia_brakeabs()

class aaia_fuelsystemcontroltype(osv.osv):
    _name = 'aaia.fuelsystemcontroltype'
    _columns = {
        'name': fields.text('Name'),
        'fueldeliveryconfig': fields.one2many('aaia.fueldeliveryconfig', 'fuelsystemcontroltypeid', 'fueldeliveryconfig'),
        'fuelsystemcontroltypeid': fields.integer('fuelsystemcontroltypeid'),
        'fuelsystemcontroltypename': fields.text('fuelsystemcontroltypename'),
    }
aaia_fuelsystemcontroltype()

class aaia_cylinderheadtype(osv.osv):
    _name = 'aaia.cylinderheadtype'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'cylinderheadtypeid', 'engineconfig'),
        'cylinderheadtypeid': fields.integer('cylinderheadtypeid'),
        'cylinderheadtypename': fields.text('cylinderheadtypename'),
    }
aaia_cylinderheadtype()

class aaia_bedtype(osv.osv):
    _name = 'aaia.bedtype'
    _columns = {
        'name': fields.text('Name'),
        'bedconfig': fields.one2many('aaia.bedconfig', 'bedtypeid', 'bedconfig'),
        'bedtypeid': fields.integer('bedtypeid'),
        'bedtypename': fields.text('bedtypename'),
    }
aaia_bedtype()

class aaia_vehicletype(osv.osv):
    _name = 'aaia.vehicletype'
    _columns = {
        'name': fields.text('Name'),
        'model': fields.one2many('aaia.model', 'vehicletypeid', 'model'),
        'vehicletypeid': fields.integer('vehicletypeid'),
        'vehicletypename': fields.text('vehicletypename'),
        'vehicletypegroupid': fields.integer('vehicletypegroupid'),
    }
aaia_vehicletype()

class aaia_brakesystem(osv.osv):
    _name = 'aaia.brakesystem'
    _columns = {
        'name': fields.text('Name'),
        'brakeconfig': fields.one2many('aaia.brakeconfig', 'brakesystemid', 'brakeconfig'),
        'brakesystemid': fields.integer('brakesystemid'),
        'brakesystemname': fields.text('brakesystemname'),
    }
aaia_brakesystem()

class aaia_year(osv.osv):
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_year, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_year, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            for item in args:
                if type(item) == tuple:
                    idlist = self.search(cr, uid, [item])
                    myargs.append(('year_id', 'in', idlist))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['year_id'])
                finalargs = [('id', 'in', uniquify([x['year_id'][0] for x in res]))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_year, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            return res

    
    _name = 'aaia.year'
    _columns = {
        'name': fields.char('Name', size=64),
#         'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'), 
        'basevehicle': fields.one2many('aaia.basevehicle', 'yearid', 'basevehicle'),
        'yearid': fields.integer('yearid'),
    }
aaia_year()

class aaia_drivetype(osv.osv):
    _name = 'aaia.drivetype'
    _columns = {
        'name': fields.text('Name'),
        'drivetypeid': fields.integer('drivetypeid'),
        'drivetypename': fields.text('drivetypename'),
    }
aaia_drivetype()

class aaia_wheelbase(osv.osv):
    _name = 'aaia.wheelbase'
    _columns = {
        'name': fields.text('Name'),
        'wheelbaseid': fields.integer('wheelbaseid'),
        'wheelbase': fields.text('wheelbase'),
        'wheelbasemetric': fields.text('wheelbasemetric'),
    }
aaia_wheelbase()

class aaia_transmissiontype(osv.osv):
    _name = 'aaia.transmissiontype'
    _columns = {
        'name': fields.text('Name'),
        'transmissionbase': fields.one2many('aaia.transmissionbase', 'transmissiontypeid', 'transmissionbase'),
        'transmissiontypeid': fields.integer('transmissiontypeid'),
        'transmissiontypename': fields.text('transmissiontypename'),
    }
aaia_transmissiontype()

class aaia_springtype(osv.osv):
    _name = 'aaia.springtype'
    _columns = {
        'name': fields.text('Name'),
        'springtypeconfig': fields.one2many('aaia.springtypeconfig', 'frontspringtypeid', 'springtypeconfig'),
        'springtypeconfig': fields.one2many('aaia.springtypeconfig', 'rearspringtypeid', 'springtypeconfig'),
        'springtypeid': fields.integer('springtypeid'),
        'springtypename': fields.text('springtypename'),
    }
aaia_springtype()

class aaia_ignitionsystemtype(osv.osv):
    _name = 'aaia.ignitionsystemtype'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'ignitionsystemtypeid', 'engineconfig'),
        'ignitionsystemtypeid': fields.integer('ignitionsystemtypeid'),
        'ignitionsystemtypename': fields.text('ignitionsystemtypename'),
    }
aaia_ignitionsystemtype()

class aaia_bedlength(osv.osv):
    _name = 'aaia.bedlength'
    _columns = {
        'name': fields.text('Name'),
        'bedconfig': fields.one2many('aaia.bedconfig', 'bedlengthid', 'bedconfig'),
        'bedlengthid': fields.integer('bedlengthid'),
        'bedlength': fields.char('bedlength', size=30),
        'bedlengthmetric': fields.char('bedlengthmetric', size=30),
    }
aaia_bedlength()

class aaia_enginevin(osv.osv):
    _name = 'aaia.enginevin'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'enginevinid', 'engineconfig'),
        'enginevinid': fields.integer('enginevinid'),
        'enginevinname': fields.text('enginevinname'),
    }
aaia_enginevin()

class aaia_make(osv.osv):
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_make, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_make, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            for item in args:
                if type(item) == tuple:
                    idlist = self.search(cr, uid, [item])
                    myargs.append(('make_id', 'in', idlist))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['make_id'])
                finalargs = [('id', 'in', uniquify([x['make_id'][0] for x in res]))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_make, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            return res

    _name = 'aaia.make'
    _columns = {
        'name': fields.text('Name'),
        'basevehicle': fields.one2many('aaia.basevehicle', 'makeid', 'basevehicle'),
        'makeid': fields.integer('makeid'),
        'makename': fields.text('makename'),
    }
aaia_make()

class aaia_springtypeconfig(osv.osv):
    _name = 'aaia.springtypeconfig'
    _columns = {
        'name': fields.text('Name'),
        'springtypeconfigid': fields.integer('springtypeconfigid'),
        'frontspringtypeid': fields.many2one('aaia.springtype', 'frontspringtypeid'),
        'rearspringtypeid': fields.many2one('aaia.springtype', 'rearspringtypeid'),
    }
aaia_springtypeconfig()

class aaia_braketype(osv.osv):
    _name = 'aaia.braketype'
    _columns = {
        'name': fields.text('Name'),
        'brakeconfig': fields.one2many('aaia.brakeconfig', 'frontbraketypeid', 'brakeconfig'),
        'brakeconfig': fields.one2many('aaia.brakeconfig', 'rearbraketypeid', 'brakeconfig'),
        'braketypeid': fields.integer('braketypeid'),
        'braketypename': fields.text('braketypename'),
    }
aaia_braketype()

class aaia_fueldeliverytype(osv.osv):
    _name = 'aaia.fueldeliverytype'
    _columns = {
        'name': fields.text('Name'),
        'fueldeliveryconfig': fields.one2many('aaia.fueldeliveryconfig', 'fueldeliverytypeid', 'fueldeliveryconfig'),
        'fueldeliverytypeid': fields.integer('fueldeliverytypeid'),
        'fueldeliverytypename': fields.text('fueldeliverytypename'),
    }
aaia_fueldeliverytype()

class aaia_fueldeliverysubtype(osv.osv):
    _name = 'aaia.fueldeliverysubtype'
    _columns = {
        'name': fields.text('Name'),
        'fueldeliveryconfig': fields.one2many('aaia.fueldeliveryconfig', 'fueldeliverysubtypeid', 'fueldeliveryconfig'),
        'fueldeliverysubtypeid': fields.integer('fueldeliverysubtypeid'),
        'fueldeliverysubtypename': fields.text('fueldeliverysubtypename'),
    }
aaia_fueldeliverysubtype()

class aaia_fuelsystemdesign(osv.osv):
    _name = 'aaia.fuelsystemdesign'
    _columns = {
        'name': fields.text('Name'),
        'fueldeliveryconfig': fields.one2many('aaia.fueldeliveryconfig', 'fuelsystemdesignid', 'fueldeliveryconfig'),
        'fuelsystemdesignid': fields.integer('fuelsystemdesignid'),
        'fuelsystemdesignname': fields.text('fuelsystemdesignname'),
    }
aaia_fuelsystemdesign()

class aaia_fueldeliveryconfig(osv.osv):
    _name = 'aaia.fueldeliveryconfig'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'fueldeliveryconfigid', 'engineconfig'),
        'fueldeliveryconfigid': fields.integer('fueldeliveryconfigid'),
        'fueldeliverytypeid': fields.many2one('aaia.fueldeliverytype', 'fueldeliverytypeid'),
        'fueldeliverysubtypeid': fields.many2one('aaia.fueldeliverysubtype', 'fueldeliverysubtypeid'),
        'fuelsystemcontroltypeid': fields.many2one('aaia.fuelsystemcontroltype', 'fuelsystemcontroltypeid'),
        'fuelsystemdesignid': fields.many2one('aaia.fuelsystemdesign', 'fuelsystemdesignid'),
    }
aaia_fueldeliveryconfig()

class aaia_bedconfig(osv.osv):
    _name = 'aaia.bedconfig'
    _columns = {
        'name': fields.text('Name'),
        'bedconfigid': fields.integer('bedconfigid'),
        'bedlengthid': fields.many2one('aaia.bedlength', 'bedlengthid'),
        'bedtypeid': fields.many2one('aaia.bedtype', 'bedtypeid'),
    }
aaia_bedconfig()

class aaia_model(osv.osv):
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_model, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_model, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            for item in args:
                if type(item) == tuple:
                    idlist = self.search(cr, uid, [item])
                    myargs.append(('model_id', 'in', uniquify(idlist)))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['model_id'])
                finalargs = [('id', 'in', uniquify([x['model_id'][0] for x in res]))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_model, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            return res


    _name = 'aaia.model'
    _columns = {
        'name': fields.text('Name'),
        'basevehicle': fields.one2many('aaia.basevehicle', 'modelid', 'basevehicle'),
        'modelid': fields.integer('modelid'),
        'modelname': fields.text('modelname'),
        'vehicletypeid': fields.many2one('aaia.vehicletype', 'vehicletypeid'),
    }
aaia_model()

class aaia_basevehicle(osv.osv):
    _name = 'aaia.basevehicle'
    _columns = {
        'name': fields.text('Name'),
        'vehicle': fields.one2many('aaia.vehicle', 'basevehicleid', 'vehicle'),
        'basevehicleid': fields.integer('basevehicleid'),
        'yearid': fields.many2one('aaia.year', 'yearid'),
        'makeid': fields.many2one('aaia.make', 'makeid'),
        'modelid': fields.many2one('aaia.model', 'modelid'),
    }
aaia_basevehicle()

class aaia_submodel(osv.osv):
    ##### _search will be called twice: once from the view where args include only dictionaries (from the view)
    #####                               and once from the "super..." invoked from the first call
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        print "entra al search submodel"
        print "args", args
        print "context", context
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_submodel, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_submodel, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            for item in args:
                if type(item) == tuple:
                    idlist = self.search(cr, uid, [item])
                    myargs.append(('submodel_id', 'in', idlist))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['submodel_id'])
                finalargs = [('id', 'in', uniquify([x['submodel_id'][0] for x in res]))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_submodel, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            print "res", res
            return res

    _name = 'aaia.submodel'
    _columns = {
        'name': fields.text('Name'),
        'vehicle': fields.one2many('aaia.vehicle', 'submodelid', 'vehicle'),
        'submodelid': fields.integer('submodelid'),
        'submodelname': fields.text('submodelname'),
    }
aaia_submodel()

class aaia_region(osv.osv):
    _name = 'aaia.region'
    _columns = {
        'name': fields.text('Name'),
        'vehicle': fields.one2many('aaia.vehicle', 'regionid', 'vehicle'),
        'regionid': fields.integer('regionid'),
        'parentid': fields.integer('parentid'),
        'regionabbr': fields.char('regionabbr', size=30),
        'regionname': fields.text('regionname'),
    }
aaia_region()

class aaia_bodynumdoors(osv.osv):
    _name = 'aaia.bodynumdoors'
    _columns = {
        'name': fields.text('Name'),
        'bodystyleconfig': fields.one2many('aaia.bodystyleconfig', 'bodynumdoorsid', 'bodystyleconfig'),
        'bodynumdoorsid': fields.integer('bodynumdoorsid'),
        'bodynumdoors': fields.char('bodynumdoors', size=30),
    }
aaia_bodynumdoors()

class aaia_bodytype(osv.osv):
    _name = 'aaia.bodytype'
    _columns = {
        'name': fields.text('Name'),
        'bodystyleconfig': fields.one2many('aaia.bodystyleconfig', 'bodytypeid', 'bodystyleconfig'),
        'bodytypeid': fields.integer('bodytypeid'),
        'bodytypename': fields.text('bodytypename'),
    }
aaia_bodytype()

class aaia_bodystyleconfig(osv.osv):
    _name = 'aaia.bodystyleconfig'
    _columns = {
        'name': fields.text('Name'),
        'bodystyleconfigid': fields.integer('bodystyleconfigid'),
        'bodynumdoorsid': fields.many2one('aaia.bodynumdoors', 'bodynumdoorsid'),
        'bodytypeid': fields.many2one('aaia.bodytype', 'bodytypeid'),
    }
aaia_bodystyleconfig()

class aaia_brakeconfig(osv.osv):
    _name = 'aaia.brakeconfig'
    _columns = {
        'name': fields.text('Name'),
        'brakeconfigid': fields.integer('brakeconfigid'),
        'brakesystemid': fields.many2one('aaia.brakesystem', 'brakesystemid'),
        'brakeabsid': fields.many2one('aaia.brakeabs', 'brakeabsid'),
        'frontbraketypeid': fields.many2one('aaia.braketype', 'frontbraketypeid'),
        'rearbraketypeid': fields.many2one('aaia.braketype', 'rearbraketypeid'),
    }
aaia_brakeconfig()

class aaia_enginedesignation(osv.osv):
    _name = 'aaia.enginedesignation'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'enginedesignationid', 'engineconfig'),
        'enginedesignationid': fields.integer('enginedesignationid'),
        'enginedesignationname': fields.text('enginedesignationname'),
    }
aaia_enginedesignation()

class aaia_enginebase(osv.osv):

    _name = 'aaia.enginebase'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'enginebaseid', 'engineconfig'),
        'enginebaseid': fields.integer('enginebaseid'),
        'liter': fields.char('liter', size=30),
        'cc': fields.char('cc', size=30),
        'cid': fields.char('cid', size=30),
        'cylinders': fields.char('cylinders', size=30),
        'blocktype': fields.char('blocktype', size=30),
        'engborein': fields.char('engborein', size=30),
        'engboremetric': fields.char('engboremetric', size=30),
        'engstrokein': fields.char('engstrokein', size=30),
        'engstrokemetric': fields.char('engstrokemetric', size=30),
    }
aaia_enginebase()

class aaia_aspiration(osv.osv):
    _name = 'aaia.aspiration'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'aspirationid', 'engineconfig'),
        'aspirationid': fields.integer('aspirationid'),
        'aspirationname': fields.text('aspirationname'),
    }
aaia_aspiration()

class aaia_fueltype(osv.osv):
    _name = 'aaia.fueltype'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'fueltypeid', 'engineconfig'),
        'fueltypeid': fields.integer('fueltypeid'),
        'fueltypename': fields.text('fueltypename'),
    }
aaia_fueltype()

class aaia_mfr(osv.osv):
    _name = 'aaia.mfr'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'enginemfrid', 'engineconfig'),
        'transmission': fields.one2many('aaia.transmission', 'transmissionmfrid', 'transmission'),
        'mfrid': fields.integer('mfrid'),
        'mfrname': fields.text('mfrname'),
    }
aaia_mfr()

class aaia_engineversion(osv.osv):
    _name = 'aaia.engineversion'
    _columns = {
        'name': fields.text('Name'),
        'engineconfig': fields.one2many('aaia.engineconfig', 'engineversionid', 'engineconfig'),
        'engineversionid': fields.integer('engineversionid'),
        'engineversion': fields.text('engineversion'),
    }
aaia_engineversion()

class aaia_engineconfig(osv.osv):
    ##### _search will be called twice: once from the view where args include only dictionaries (from the view)
    #####                               and once from the "super..." invoked from the first call
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_engineconfig, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_engineconfig, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            for item in args:
                if type(item) == tuple:
                    idlist = self.search(cr, uid, [item])
                    myargs.append(('engine_id', 'in', idlist))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['engine_id'])
                finalargs = [('id', 'in', uniquify([x['engine_id'][0] for x in res]))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_engineconfig, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            return res

    _name = 'aaia.engineconfig'
    _columns = {
        'name': fields.text('Name'),
        'engineconfigid': fields.integer('engineconfigid'),
        'enginedesignationid': fields.many2one('aaia.enginedesignation', 'enginedesignationid'),
        'enginevinid': fields.many2one('aaia.enginevin', 'enginevinid'),
        'enginebaseid': fields.many2one('aaia.enginebase', 'enginebaseid'),
        'fueldeliveryconfigid': fields.many2one('aaia.fueldeliveryconfig', 'fueldeliveryconfigid'),
        'aspirationid': fields.many2one('aaia.aspiration', 'aspirationid'),
        'cylinderheadtypeid': fields.many2one('aaia.cylinderheadtype', 'cylinderheadtypeid'),
        'fueltypeid': fields.many2one('aaia.fueltype', 'fueltypeid'),
        'ignitionsystemtypeid': fields.many2one('aaia.ignitionsystemtype', 'ignitionsystemtypeid'),
        'enginemfrid': fields.many2one('aaia.mfr', 'enginemfrid'),
        'engineversionid': fields.many2one('aaia.engineversion', 'engineversionid'),
        'valvesid': fields.integer('valvesid'),
        'poweroutputid': fields.integer('poweroutputid'),
    }
aaia_engineconfig()

class aaia_mfrbodycode(osv.osv):
    _name = 'aaia.mfrbodycode'
    _columns = {
        'name': fields.text('Name'),
        'mfrbodycodeid': fields.integer('mfrbodycodeid'),
        'mfrbodycodename': fields.text('mfrbodycodename'),
    }
aaia_mfrbodycode()

class aaia_steeringsystem(osv.osv):
    _name = 'aaia.steeringsystem'
    _columns = {
        'name': fields.text('Name'),
        'steeringconfig': fields.one2many('aaia.steeringconfig', 'steeringsystemid', 'steeringconfig'),
        'steeringsystemid': fields.integer('steeringsystemid'),
        'steeringsystemname': fields.text('steeringsystemname'),
    }
aaia_steeringsystem()

class aaia_steeringconfig(osv.osv):
    _name = 'aaia.steeringconfig'
    _columns = {
        'name': fields.text('Name'),
        'steeringconfigid': fields.integer('steeringconfigid'),
        'steeringtypeid': fields.many2one('aaia.steeringtype', 'steeringtypeid'),
        'steeringsystemid': fields.many2one('aaia.steeringsystem', 'steeringsystemid'),
    }
aaia_steeringconfig()

class aaia_transmissionnumspeeds(osv.osv):
    _name = 'aaia.transmissionnumspeeds'
    _columns = {
        'name': fields.text('Name'),
        'transmissionbase': fields.one2many('aaia.transmissionbase', 'transmissionnumspeedsid', 'transmissionbase'),
        'transmissionnumspeedsid': fields.integer('transmissionnumspeedsid'),
        'transmissionnumspeeds': fields.char('transmissionnumspeeds', size=30),
    }
aaia_transmissionnumspeeds()

class aaia_transmissioncontroltype(osv.osv):
    _name = 'aaia.transmissioncontroltype'
    _columns = {
        'name': fields.text('Name'),
        'transmissionbase': fields.one2many('aaia.transmissionbase', 'transmissioncontroltypeid', 'transmissionbase'),
        'transmissioncontroltypeid': fields.integer('transmissioncontroltypeid'),
        'transmissioncontroltypename': fields.text('transmissioncontroltypename'),
    }
aaia_transmissioncontroltype()

class aaia_transmissionbase(osv.osv):
    _name = 'aaia.transmissionbase'
    _columns = {
        'name': fields.text('Name'),
        'transmission': fields.one2many('aaia.transmission', 'transmissionbaseid', 'transmission'),
        'transmissionbaseid': fields.integer('transmissionbaseid'),
        'transmissiontypeid': fields.many2one('aaia.transmissiontype', 'transmissiontypeid'),
        'transmissionnumspeedsid': fields.many2one('aaia.transmissionnumspeeds', 'transmissionnumspeedsid'),
        'transmissioncontroltypeid': fields.many2one('aaia.transmissioncontroltype', 'transmissioncontroltypeid'),
    }
aaia_transmissionbase()

class aaia_transmissionmfrcode(osv.osv):
    _name = 'aaia.transmissionmfrcode'
    _columns = {
        'name': fields.text('Name'),
        'transmission': fields.one2many('aaia.transmission', 'transmissionmfrcodeid', 'transmission'),
        'transmissionmfrcodeid': fields.integer('transmissionmfrcodeid'),
        'transmissionmfrcode': fields.text('transmissionmfrcode'),
    }
aaia_transmissionmfrcode()

class aaia_transmission(osv.osv):
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        typelist = [type(x) for x in args]
        ##### If there is no dict, then it doesn't come from our view
        if not dict in typelist:
            return super(aaia_transmission, self)._search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        ##### If this call includes a tuple ('id', 'in', [....]), it is only to take care of offset, limit, etc...
        elif tuple in typelist and args[typelist.index(tuple)][0] == 'id':
            return super(aaia_transmission, self)._search(cr, uid, [args[typelist.index(tuple)]], offset=offset, limit=limit, order=order, context=context, count=count, access_rights_uid=access_rights_uid)
        else:
            ##### If not, we show only the engineconfig's which correspond to year, make, model already selected
            myargs = []
            transidlist = []
            for item in args:
                if type(item) == tuple:
                    transidlist = self.search(cr, uid, [item])
                    myargs.append(('transmission_ids', 'in', transidlist))
                elif item['value']:
                    myargs.append((item['column'], '=', item['value']))
            if myargs:
                idlist = self.pool.get('aaia.vehicleengine').search(cr, uid, myargs)
                res = self.pool.get('aaia.vehicleengine').read(cr, uid, idlist, ['transmission_ids'])
                idlist = []
                for transitem in res:
                    if transidlist:
                        for myid in transitem['transmission_ids']:
                            if myid in transidlist:
                                idlist.append(myid)
                    else:
                        idlist += transitem['transmission_ids']
                finalargs = [('id', 'in', uniquify(idlist))]
            else:
                finalargs = []
            ##### We finally call the super to take care of offset, limit, etc...
            res =  super(aaia_transmission, self)._search(cr, uid, finalargs, offset, limit, order, context, count, access_rights_uid)
            return res

    _name = 'aaia.transmission'
    _columns = {
        'name': fields.text('Name'),
        'transmissionid': fields.integer('transmissionid'),
        'transmissionbaseid': fields.many2one('aaia.transmissionbase', 'transmissionbaseid'),
        'transmissionmfrcodeid': fields.many2one('aaia.transmissionmfrcode', 'transmissionmfrcodeid'),
        'transmissionmfrid': fields.many2one('aaia.mfr', 'transmissionmfrid'),
        'transmissioneleccontrolledid': fields.integer('transmissioneleccontrolledid'),
    }
aaia_transmission()

class aaia_vehicle(osv.osv):
    _name = 'aaia.vehicle'
    _columns = {
        'name': fields.text('Name'),
        'vehicleid': fields.integer('vehicleid'),
        'basevehicleid': fields.many2one('aaia.basevehicle', 'basevehicleid'),
        'submodelid': fields.many2one('aaia.submodel', 'submodelid'),
        'source': fields.text('source'),
        'regionid': fields.many2one('aaia.region', 'regionid'),
        'bedconfig': fields.many2many('aaia.bedconfig', 'vehicletobedconfig', 'vehicleid', 'bedconfigid', 'bedconfig'),
        'bodystyleconfig': fields.many2many('aaia.bodystyleconfig', 'vehicletobodystyleconfig', 'vehicleid', 'bodystyleconfigid', 'bodystyleconfig'),
        'brakeconfig': fields.many2many('aaia.brakeconfig', 'vehicletobrakeconfig', 'vehicleid', 'brakeconfigid', 'brakeconfig'),
        'drivetype': fields.many2many('aaia.drivetype', 'vehicletodrivetype', 'vehicleid', 'drivetypeid', 'drivetype'),
        'engineconfig': fields.many2many('aaia.engineconfig', 'vehicletoengineconfig', 'vehicleid', 'engineconfigid', 'engineconfig'),
        'mfrbodycode': fields.many2many('aaia.mfrbodycode', 'vehicletomfrbodycode', 'vehicleid', 'mfrbodycodeid', 'mfrbodycode'),
        'springtypeconfig': fields.many2many('aaia.springtypeconfig', 'vehicletospringtypeconfig', 'vehicleid', 'springtypeconfigid', 'springtypeconfig'),
        'steeringconfig': fields.many2many('aaia.steeringconfig', 'vehicletosteeringconfig', 'vehicleid', 'steeringconfigid', 'steeringconfig'),
        'transmission': fields.many2many('aaia.transmission', 'vehicletotransmission', 'vehicleid', 'transmissionid', 'transmission'),
        'wheelbase': fields.many2many('aaia.wheelbase', 'vehicletowheelbase', 'vehicleid', 'wheelbaseid', 'wheelbase'),
    }
aaia_vehicle()


###### Added 2011-06-13 (not in metamodulo.py)

class aaia_vehicleconfig(osv.osv):
    _name = 'aaia.vehicleconfig'
    _columns = {
        'name': fields.text('Name'),
        'vehicleconfigid': fields.integer('vehicleconfigid'),
        'vehicleid': fields.many2one('aaia.vehicle', 'vehicleid'),
        'bedconfigid': fields.many2one('aaia.bedconfig', 'bedconfigid'),
        'bodystyleconfigid': fields.many2one('aaia.bodystyleconfig', 'bodystyleconfigid'),
        'brakeconfigid': fields.many2one('aaia.brakeconfig', 'brakeconfigid'),
        'drivetypeid': fields.many2one('aaia.drivetype', 'drivetypeid'),
        'engineconfigid': fields.many2one('aaia.engineconfig', 'engineconfigid'),
        'mfrbodycodeid': fields.many2one('aaia.mfrbodycode', 'mfrbodycodeid'),
        'springtypeconfigid': fields.many2one('aaia.springtypeconfig', 'springtypeconfigid'),
        'steeringconfigid': fields.many2one('aaia.steeringconfig', 'steeringconfigid'),
        'transmissionid': fields.many2one('aaia.transmission', 'transmissionid'),
        'wheelbaseid': fields.many2one('aaia.wheelbase', 'wheelbaseid')
    }
aaia_vehicleconfig()

