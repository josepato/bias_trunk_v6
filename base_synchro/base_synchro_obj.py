from osv import fields,osv
import tools
import re
import time
import pickle
import threading
import pooler
import xmlrpclib
import os


class RPCProxyOne(object):
    def __init__(self, server, ressource):
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common'%(server.server_url,server.server_port)
        rpc = xmlrpclib.ServerProxy(local_url, allow_none=True)
        self.uid = rpc.login(server.server_db, server.login, server.password)
        local_url = 'http://%s:%d/xmlrpc/object'%(server.server_url,server.server_port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
    def __getattr__(self, name):
        try:
            return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.server.server_db, self.uid, self.server.password, self.ressource, name, *args, **kwargs)
        except:
            print cr.close()

    
class RPCProxy(object):
    def __init__(self, server):
        self.server = server
    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)

class base_synchro_server(osv.osv):
    '''Class to store the information regarding server'''
    _name = "base.synchro.server"
    _description = "Synchronized server"
    _columns = {
        'name': fields.char('Server name', size=64,required=True),
        'server_url': fields.char('Server URL', size=64,required=True),
        'server_port': fields.integer('Server Port', size=64,required=True),
        'server_db': fields.char('Server Database', size=64,required=True),
        'login': fields.char('User Name',size=50,required=True),
        'password': fields.char('Password',size=64,invisible=True,required=True),
        'obj_ids' : fields.one2many('base.synchro.obj','server_id','Models',ondelete='cascade')
    }
    _defaults = {
        'server_port': lambda *args: 8069
    }
base_synchro_server()

class base_synchro_obj(osv.osv):

    start_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
    report = []
    report_total = 0
    report_create = 0
    report_write = 0
    worflow_updates = []


    
    '''Class to store the operations done by wizart'''
    _name = "base.synchro.obj"
    _description = "Register Class"
    _columns = {
        'name':fields.char('Name', size=64, select=1, required=1),
        'domain':fields.char('Domain', size=64, select=1, required=1),
        'server_id':fields.many2one('base.synchro.server','Server', ondelete='cascade', select=1, required=1),
        'model_id': fields.many2one('ir.model', 'Object to synchronize',required=True),
        'action':fields.selection([('d','Download'),('u','Upload'),('b','Both')],'Synchronisation direction', required=True),
        'sequence': fields.integer('Sequence'),
        'active': fields.boolean('Active'),
        'initialize': fields.boolean('Initialize'),
        'synchronize_date':fields.datetime('Latest Synchronization', readonly=True),
        'line_id':fields.one2many('base.synchro.obj.line','obj_id','Ids Affected',ondelete='cascade'),
        'avoid_ids':fields.one2many('base.synchro.obj.avoid','obj_id','Fields Not Sync.'),
    }
    _defaults = {
        'active': lambda *args: True,
        'action': lambda *args: 'd',
        'domain': lambda *args: '[]'
    }
    _order = 'sequence'
    #
    # Return a list of changes: [ (date, id) ]
    #
    def _get_ids(self, cr, uid, object, dt, domain=[], context={}):
        result = []
        if dt:
            domain2 = domain+[('write_date','>=',dt)]
            domain3 = domain+[('create_date','>=',dt)]
        else:
            domain2 = domain3 = domain
        ids = self.pool.get(object).search(cr, uid, domain2, context=context)
        ids += self.pool.get(object).search(cr, uid, domain3, context=context)
        for r in self.pool.get(object).perm_read(cr, uid, ids, context, details=False):
            result.append( (r['write_date'] or r['create_date'], r['id'], context.get('action', 'd')))
        return result


    ### added by jpv
    def _get_init_ids(self, cr, uid, pickle_dir, object_id, model):
        result = []
        print 'initissssss'
        query = 'SELECT id, create_date, write_date from %s  order by id'%model
        print 'query',query
        cr.execute(query)
        res = cr.fetchall()
        new_obj_dir = {}
        object_dir = pickle.loads(pickle_dir)
        for rr in res:
            new_obj_dir[rr[0]]={'cd':rr[1],'wd':rr[2]}
        new_obj_ids =  new_obj_dir.keys()
        for obj_id in object_dir.keys():
            if obj_id in new_obj_ids:
                if object_dir[obj_id] == new_obj_dir[obj_id]:
                   result.append({'obj_id':object_id, 'local_id':obj_id, 'remote_id':obj_id})
        return result
                
    def db_update(self, cr, uid, query, context=''):
        res = True
        cr.commit()

        cr.execute(query)
        if context:
            res = eval('cr.%s()'%(context))
        if not res:
            res = 0
        return res

    def db_dict_fetchall(self, cr, uid, query):
        cr.execute(query)
        res = cr.dictfetchone()
        return res.keys()

    def get_wkf_workitem(self, cr, uid, query, context):
        cr.execute(query)
        instance = cr.fetchone()
        query = "SELECT act_id, inst_id, subflow_id, state FROM wkf_workitem where inst_id=%s"%(instance[0])
        cr.execute(query)
        res = cr.dictfetchall()
        pickle_dir = pickle.dumps(res)
        return pickle_dir

    def update_wkf_workitem(self, cr, uid,  wkf_workitems_pickle, context):
        wkf_workitems = pickle.loads(wkf_workitems_pickle)
        for wkf_items in wkf_workitems:
            wkf_ids = self.pool.get('workflow.workitem').search(cr, uid, [('inst_id','=',wkf_items['inst_id'])])
            query_set = ''
            if wkf_ids:
                self.pool.get('workflow.workitem').unlink(cr, uid, wkf_ids)
                n_id = self.pool.get('workflow.workitem').create(cr, uid, wkf_items)
        return True


######################################################
######################################################
######################################################


    def _set_update_query(self, values, db_fields):
        print '_set_upate_query'
        res = ''
        for field in values.keys():
            if field in db_fields:
                if type(values[field]).__name__ in ("bool", "int", "float"):
                    if not values[field]:
                        res += field +'=' + 'Null' + ' , '
                    else:
                        res += field +'=' + str(values[field]) + ' , '
                else:
                    res += "%s='%s' , "%(field, values[field])
        return res[:-2]





    def _synchronize(self, cr, uid, server, object, context):
        pool = pooler.get_pool(cr.dbname)
        self.meta = {}
        ids = []
        pool1 = RPCProxy(server)
        pool2 = pool
        #try:
        if object.action in ('d','b'):
            ids = pool1.get('base.synchro.obj')._get_ids(cr, uid,
                object.model_id.model,
                object.synchronize_date,
                eval(object.domain),
                {'action':'d'}
            )
        if object.action in ('u','b'):
            ids += pool2.get('base.synchro.obj')._get_ids(cr, uid,
                object.model_id.model,
                object.synchronize_date,
                eval(object.domain),
                {'action':'u'}
            )
        ids.sort()
        iii = 0
        #self.worflow_updates = []
        for dt, id, action in ids:
            print 'Process', dt, id, action
            iii +=1
            if action=='u':
                pool_src = pool2
                pool_dest = pool1
            else:
                pool_src = pool1
                pool_dest = pool2
            print 'Read', object.model_id.model, id
            fields = False
            if object.model_id.model=='crm.case.history':
                fields = ['email','description','log_id']
            value = pool_src.get(object.model_id.model).read(cr, uid, [id], fields)[0]
            value = self._data_transform(cr, uid, pool_src, pool_dest, object.model_id.model, value, action)
            id2 = self.get_id(cr, uid, object.id, id, action, context)
            #
            # Transform value
            #
            #tid=pool_dest.get(object.model_id.model).name_search(cr, uid, value['name'],[],'=',)
            if not (iii%50):
                print 'Record', iii
            # Filter fields to not sync
            for field in object.avoid_ids:
                if field.name in value:

                    del value[field.name]
            print 'id2', id2
            if id2:
                idnew = False
                try:
                    pool_dest.get(object.model_id.model).write(cr, uid, [id2], value)
                except Exception, e:
                    query = 'SELECT * FROM  %s WHERE id=%s'%(re.sub('\.','_', object.model_id.model),  id)
                    campos = pool_src.get('base.synchro.obj').db_dict_fetchall(cr, uid, query)
                    update_query = self._set_update_query(value, campos)
                    query = 'UPDATE %s SET %s WHERE id=%s'%(re.sub('\.','_', object.model_id.model), update_query, id2)
                    pool_dest.get('base.synchro.obj').db_update(cr, uid, query)

                self.report_total+=1
                self.report_write+=1
            else:
                #idnew = pool_dest.get('base.synchro.obj').pickle_craete(cr, uid, object.model_id.model, [value,])
                try:
                    idnew = pool_dest.get(object.model_id.model).create(cr, uid, value, {'no_chek':True})
                    if value.has_key('state'):
                        state_val = pool_dest.get(object.model_id.model).read(cr, uid, idnew, ['state'])
                        if state_val != value['state']:
                            pool_dest.get(object.model_id.model).write(cr, uid, [idnew], {'state':value['state']}, {'no_chek':True})
                    synid = pool.get('base.synchro.obj.line').create(cr, uid, {
                        'obj_id': object.id,
                        'local_id': (action=='u') and id or idnew,
                        'remote_id': (action=='d') and id or idnew
                        })
                except:
                    self.report.append('ERROR: Unable to update record ['+str(id2)+']: ON MODEL: ' + object.model_id.model + ' ID:' + str(id) )
                    idnew = ''

                self.report_total+=1
                self.report_create+=1
            model_query = "select id from wkf where osv='%s'"%(object.model_id.model)
            #cr.execute("select id from wkf where osv='%s'"%(object.model_id.model))
            #has_wkf = cr.fetchone()
            cr.commit()
            has_wkf = pool.get('base.synchro.obj').db_update(cr, uid, model_query, 'fetchone')
            if has_wkf and (idnew or id2):
                self.worflow_updates.append({'server':server,
                                             'module_brw':object.model_id,
                                             'id_org':id,
                                             'id_dest':idnew or id2,
                                             'action':action,
                                             'pool_dest':pool_dest,
                                             'pool_org':pool})
                #self.check_wkf(cr, uid, server, object.model_id, id, idnew or id2, action, pool_dest, pool)    
        self.meta = {}

        
        return 'finish'

    #
    # IN: object and ID
    # OUT: ID of the remote object computed:
    #        If object is synchronised, read the sync database
    #        Otherwise, use the name_search method
    #

    def _get_instance(self, cr, uid, res_id, res_type):
        query = "SELECT id from wkf_instance where res_id=%s and res_type='%s'"%(res_id, res_type)
        return query


    #def check_wkf(self, cr, uid, server, module_brw, id_org, id_dest, action, pool_dest, pool_org):
    def check_wkf(self,cr, uid ):
        for wkf in self.worflow_updates:
            server = wkf['server']
            module_brw = wkf['module_brw']
            id_org = wkf['id_org']
            id_dest =wkf['id_dest']
            action = wkf['action']
            pool_dest = wkf['pool_dest']
            pool_org = wkf['pool_org']
            local_id = 'local_id'
            remote_id = 'remote_id'
            if action == 'd':
                local_id = 'remote_id'
                remote_id = 'local_id'
                pool = RPCProxy(server)
            else:
                pool = pool_org
            query = self._get_instance(cr, uid, id_org, module_brw.model)
            wkf_workitems_pickle = pool.get('base.synchro.obj').get_wkf_workitem(cr, uid, query, 'origendelcambio')
            wkf_workitems = pickle.loads(wkf_workitems_pickle)
            query = self._get_instance(cr, uid, id_dest, module_brw.model)
            act_obj_id = 'workflow.activity'
            for wkf_items in wkf_workitems:
                act_id = self._relation_transform(cr, uid, pool, pool_dest, act_obj_id, wkf_items['act_id'], action)
                wkf_items.update({'act_id':act_id})
                if wkf_items['inst_id']:
                    query = 'SELECT res_id, res_type from wkf_instance where id=%s'%(wkf_items['inst_id'])
                    rel_object_id = pool.get('base.synchro.obj').db_update(cr, uid, query, 'fetchone')
                    obj_id = self._relation_transform(cr, uid, pool, pool_dest, rel_object_id[1], rel_object_id[0], action)
                    query = self._get_instance(cr, uid, obj_id, rel_object_id[1])
                    inst_id = pool_dest.get('base.synchro.obj').db_update(cr, uid, query, 'fetchone')
                    if inst_id:
                        inst_id = inst_id[0]
                    wkf_items.update({'inst_id':inst_id})
                if wkf_items['subflow_id']:
                    query = 'SELECT res_id, res_type from wkf_instance where id=%s'%(wkf_items['subflow_id'])
                    rel_object_id = pool.get('base.synchro.obj').db_update(cr, uid, query, 'fetchone')
                    obj_id = self._relation_transform(cr, uid, pool, pool_dest, rel_object_id[1], rel_object_id[0], action)
                    if obj_id:
                        query = self._get_instance(cr, uid, obj_id, module_brw.model)
                        #cr.execute(query)
                        #subflow_id =  cr.fetchone()
                        subflow_id = pool_dest.get('base.synchro.obj').db_update(cr, uid, query, 'fetchone')
                    else:
                        subflow_id = False
                    if subflow_id:
                        subflow_id = subflow_id[0]
                    wkf_items.update({'subflow_id':subflow_id})
            wkf_workitems_pickle = pickle.dumps(wkf_workitems)
            pool_dest.get('base.synchro.obj').update_wkf_workitem(cr, uid,  wkf_workitems_pickle, 'base destino del cambio')
            #wkf_workitems = pool_dest.get('base.synchro.obj').get_wkf_workitem(cr, uid, query, 'destino del cambio')

            #cr.execute(query)
            #instance = cr.fetchone()
        return True

    def get_id(self, cr, uid, object_id, id, action, context={}):
        pool = pooler.get_pool(cr.dbname)
        field_src = (action=='u') and 'local_id' or 'remote_id'
        field_dest = (action=='d') and 'local_id' or 'remote_id'
        
        rid = pool.get('base.synchro.obj.line').search(cr, uid, [('obj_id','=',object_id), (field_src,'=',id)], context=context)
        result = False
        if rid:
            result  = pool.get('base.synchro.obj.line').read(cr, uid, rid, [field_dest], context=context)[0][field_dest]
        return result




    def initialize_tables(self, cr, uid, server, object, context):
        if object.initialize:
            self.report.append('Table %s already initialize'%object.model_id.model)
            return 'finish'
        pool = pooler.get_pool(cr.dbname)
        model = object.model_id.model
        model = re.sub('\.','_',model)
        if model[:8] == 'workflow':
            model = re.sub('workflow','wkf',model)
        query = 'SELECT id, create_date, write_date from %s  order by id'%model
        cr.execute(query)
        res = cr.fetchall()
        res_dir = {}
        for rr in res:
            res_dir[rr[0]]={'cd':rr[1],'wd':rr[2]}
        pool = pooler.get_pool(cr.dbname)
        #self.meta = {}
        ids = []
        pool1 = RPCProxy(server)
        pool2 = pool
        dt = time.strftime('%Y-%m-%d %H:%M:%S')
        pickle_dir = pickle.dumps(res_dir)
        value = pool1.get('base.synchro.obj')._get_init_ids(cr, uid, pickle_dir, object.id, model)
        for new_id in value:
            pool.get('base.synchro.obj.line').create(cr, uid, new_id)
            self.report_create += 1
        return 'finish'



    def _relation_transform(self, cr, uid, pool_src, pool_dest, object, id, action, context={}):
        if not id:
            return False
        pool = pooler.get_pool(cr.dbname)
        cr.execute("select o.id from base_synchro_obj o left join ir_model m on (o.model_id =m.id) where m.model='%s' and o.active=True"%(object))
        obj = cr.fetchone()
        result = False
        if obj:
            #
            # If the object is synchronised and found, set it
            #
            result = self.get_id(cr, uid, obj[0], id, action, context)
        else:
            #
            # If not synchronized, try to find it with name_get/name_search
            #
            names = pool_src.get(object).name_get(cr, uid, [id], context)[0][1]
            res = pool_dest.get(object).name_search(cr, uid, names, [], 'like')
            if res:
                result = res[0][0]
            else:
                # LOG this in the report, better message.
                print self.report.append('WARNING: Record "%s" on relation %s not found, set to null.' % (names,object))
        return result

    def _data_transform(self, cr, uid, pool_src, pool_dest, object, data, action='u', context={}):
        print 'transform'
        self.meta.setdefault(pool_src, {})
        if not object in self.meta[pool_src]:
            self.meta[pool_src][object] = pool_src.get(object).fields_get(cr, uid, context)
        fields = self.meta[pool_src][object]

        for f in fields:
            if f not in data:
                continue
            ftype = fields[f]['type']

            if ftype in ('function', 'one2many', 'one2one'):
                del data[f]
            elif ftype == 'many2one':
                if data[f]:
                    df = self._relation_transform(cr, uid, pool_src, pool_dest, fields[f]['relation'], data[f][0], action, context)
                    data[f] = df
                    if not data[f]:
                        del data[f]
            elif ftype == 'many2many':
                res = map(lambda x: self._relation_transform(cr, uid, pool_src, pool_dest, fields[f]['relation'], x, action, context), data[f])
                data[f] = [(6, 0, res)]
        del data['id']
        return data

    #
    # Find all objects that are created or modified after the synchronize_date
    # Synchronize these obejcts
    #
    def _upload_download(self, db_name,  uid, server_id, context):
        try:
            cr = pooler.get_db(db_name).cursor()
        except:
            return False
        start_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
        #pool = pooler.get_pool(cr.dbname)
        #server = self.pool.get('base.synchro.server').browse(cr, uid, data['form']['server_url'], context)
        server = self.pool.get('base.synchro.server').browse(cr, uid, server_id, context)
        for object in server.obj_ids:
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            if context['initialize']:
                init_id = self.initialize_tables(cr, uid, server, object, context)
                #return 'finish'
            else:
                self._synchronize(cr, uid, server, object, context)
            if object.action=='b':
                time.sleep(1)
                dt = time.strftime('%Y-%m-%d %H:%M:%S')
            if context['initialize']:
                self.pool.get('base.synchro.obj').write(cr, uid, [object.id], {'initialize': True})
            else:
                self.pool.get('base.synchro.obj').write(cr, uid, [object.id], {'synchronize_date': dt})
            cr.commit()
        end_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
        if 'user_id' in context and context['user_id']:
            #request = pooler.get_pool(cr.dbname).get('res.request')
            request = self.pool.get('res.request')
            if not self.report:
                self.report.append('No exception.')
            summary = '''Here is the synchronization report:

Synchronization started: %s
Synchronization finnished: %s

Synchronized records: %d
Records updated: %d
Records created: %d

Exceptions:
            '''% (start_date,end_date,self.report_total, self.report_write,self.report_create)
            summary += '\n'.join(self.report)
            request.create(cr, uid, {
                'name' : "Synchronization report",
                'act_from' : uid,
                'act_to' : context['user_id'],
                'body': summary,
            })
        if self.worflow_updates:
            self.check_wkf(cr, uid)
        cr.commit()
        cr.close()
        return True


    def _upload_download_multi_thread(self, cr, uid, server_id, context):

        threaded_synchronization = threading.Thread(target=self._upload_download, args=(cr.dbname, uid, server_id, context))
        threaded_synchronization.start()
        return 'finish'




    
base_synchro_obj()

class base_synchro_obj_avoid(osv.osv):
    _name = "base.synchro.obj.avoid"
    _description = "Fields to not synchronize"
    _columns = {
        'name':fields.char('Field Name', size=64, select=1, required=1),
        'obj_id':fields.many2one('base.synchro.obj', 'Object', required=1,ondelete='cascade'),
    }
base_synchro_obj_avoid()


class base_synchro_obj_line(osv.osv):
    '''Class to store the operations done by wizard'''
    _name = "base.synchro.obj.line"
    _description = "Synchronized instances"
    _columns = {
        'name': fields.datetime('Date', required=True),
        'obj_id': fields.many2one('base.synchro.obj', 'Object', ondelete='cascade', select=True),
        'local_id': fields.integer('Local Id',readonly=True),
        'remote_id':fields.integer('Remote Id',readonly=True),
    }
    _defaults = {
        'name': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S')
    }
base_synchro_obj_line()




