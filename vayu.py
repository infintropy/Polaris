import airtable
import json
import base64
import os
import six
import copy
from Queue import Queue
from threading import Thread

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtCore


'''
#
###
#######
##############
#################################
#################################
 __     ___ __   ___   _    #####
 \ \   / / \\ \ / / | | |   #######
  \ \ / / _ \\ V /| | | |   ###########
   \ V / ___ \| | | |_| |   ###################
    \_/_/   \_\_|  \___/                 ######
                                         ######
- Airtable connection module for BRAHMA. ######
- Used with the <name> caching module.   ######
                                         ######  
###############################################
###############################################
############## 
#######
###
#                   



Vayu is a communication module for AirTable connecting with Brahma entities. 

Ideas:
    Will probably need to configure a simpler artist paradigm, (not officially USER based (with credentialing)) so that people can just use the front end 
    For this, would be easy to keep the login front-end within Brahma and then register account information as info on a specific base. 
        - This way, a site only has to maintain $20 a momth record keeping, and exploit having multiple users accessing 50,000 records/base



'''

API_KEY = 'keyyeOyrgbQQ9qvLh'
CONFIG_BASE_KEY = 'appZS0IqdlNPJszXv'
os.environ['AIRTABLE_API_KEY'] = API_KEY





class SessionManager(QObject):
    '''
    This will let me know easier.
    It is assumed that entities are limited to the preconfigured tables.

    We must
        1) Define the sessions: storing the key for the project and its tables.
        2) Define if a project has a default configuration, or if it has entities that can be extended.
           Extending and integrating new entities is quite easy as long as you register them.
           For speed and unlike Shotgun, you can define custom entities at will and not have to enable them site wide.
    '''

    retrieving_sessions = Signal(str)
    this_project = Signal(str)
    project_table_count = Signal(int)
    table_increment = Signal(int)
    setup_complete = Signal()

    def __init__(self):
        '''
        store session information in a configuration table, retrieve that information and then build a session dict which we will wrap and use to call different projects
        '''
        super(SessionManager, self).__init__()
        self.session_mapping = None
        self.session_info = None
        self.base = {}
        self._rec = {}
        self.table = {}
        self.team = {}
        self.default_entities = None
        # builds the session obj
        self.config = {}
        for s in ['BASE', 'ENTITY']:
            self.config[s] = airtable.Airtable(CONFIG_BASE_KEY, s)

        self.c = 0
        #self.get_sessions()


    def get_sessions(self, all=None):
        self.retrieving_sessions.emit('starting to retrieve the sessssssssions')
        opt = ['active']
        if all:
            opt.append('archived')
        self.session_info = self.config['BASE'].get_all(fields=['project_code', 'session_id', 'session_type', 'extra_entities'],
                                                        formula="{status}='active'")
        self.session_mapping = dict((i['fields']['project_code'], i['fields']['session_id']) for i in self.session_info if i['fields'].get('session_type') and i['fields']['session_type']=="Project")
        self.team_mapping= [i['fields']['session_id'] for i in self.session_info if i['fields'].get('session_type') and i['fields']['session_type'] == "Team"][0]
        return self.session_mapping

    def get_base(self, base):
        self._rec[base] = {}
        self.table[base] = {}
        for n in self.base[base].keys():
            self.c += 1
            self.table_increment.emit( self.c )
            print("Adding records into main record container for {} in {}".format( base, n ))
            self.table[base][n] = self.base[base][n].get_all()
            for r in self.table[base][n]:
                self._rec[base][r['id']] = r

        return self._rec[base]


    def build_all_sessions(self):
        '''
        This is the main session object.
        '''

        entities = self.default_project_entities()
        extra_entities = dict((v['id'], v) for v in self.session_info )

        if self.session_mapping:
            for k, v in six.iteritems(self.session_mapping):
                session_entities = entities
                if k in self.base.keys():
                    print("INFO:: ALREADY FOUND:: {}:: SKIPPING".format(k) )
                    pass
                else:
                    self.base[k] = {}
                    print(k)
                    kbase = [i for i in self.session_info if i['fields'].get('project_code') and i['fields']['project_code'] == k]

                    if len(kbase)>0:
                        if kbase[0]['fields'].get('extra_entities'):
                            for r in kbase[0]['fields']['extra_entities']:
                                try:
                                    session_entities.append( self.project_entity_ext[r]  )
                                except Exception:
                                    pass

                    self.project_table_count.emit( len( session_entities )  )
                    self.c = 0
                    for e in session_entities:
                        if e in self.base[k].keys():
                            print("INFO:: ALREADY FOUND:: {} >> TABLE:: {} into main session object.".format(k, e) )

                        else:
                            try:
                                self.c += 1
                                self.base[k][e] = airtable.Airtable(v, e)
                                print("INFO:: MAPPED BASE:: {} >> TABLE:: {} into main session object.".format(k, e) )
                                self.table_increment.emit( self.c )
                                self.this_project.emit("%s - %s" %(k, e))
                            except:
                                print("ERROR:: Couldnt establish base {}:{}".format(k, e) )
                    try:
                        self.base[k]["People"] = airtable.Airtable(v, "#People")
                    except:
                        pass

                    self.get_base(k)

        if self.team_mapping:
            self.team['People'] = airtable.Airtable(self.team_mapping, "People")


    def refresh_people_table(self):
        # this is the recipe: ac.base['avt2']['People'].batch_delete([i['id'] for i in ac.table['avt2']['People']])
        people_table = [i['fields'] for i in self.team['People'].get_all()]
        pt = []
        for i in people_table:
            #pic = i['picture'][0]['thumbnails']['large']['url']
            person = dict((k, v  ) for k,v in i.iteritems() if k in ['first_name', 'last_name', 'email', 'latest_activity'])

            pt.append(person)

            # people_table[i]['picture'] =
        for b in self.base.keys():
            if "People" in self.base[b].keys():
                print "refreshing all entries from base {} #People".format(b)
                self.base[b]['People'].batch_delete([i['id'] for i in self.base[b]['People'].get_all()])


                #self.base[b]['People']
                #return pt
                return self.base[b]["People"].batch_insert(pt)


    def default_project_entities(self):
        '''
        These are the default entities that each project will contain.
        If you would like to add more entities, make
        '''
        self.entities = self.config['ENTITY'].get_all(fields=["name", 'type'])
        self.default_entities = [i['fields']['name'] for i in self.entities if i['fields'].get('type') and i['fields']['type'] == "DEFAULT"]
        self.project_entity_ext = dict((i['id'], i['fields']['name']) for i in self.entities if i['fields'].get('type') and i['fields']['type'] == "EXT")
        return self.default_entities

    def remove_session(self, name):
        if name in self.session_mapping.keys():
            self.base.pop(name)

    def build_entity_sessions(self):
        pass

    def find(self, entity_name, fields=None, formula=None, project=None, view=None, id=None):
        #TODO:: go for something else here
        res = []
        keys = self.base.keys()
        if project:
            keys = [project]
        for b in keys:
            if id:
                formula = "RECORD_ID='{}'".format(id)
            if fields:
                res.extend(self.base[b][entity_name].get_all(fields=fields, formula=formula, view=view))
            else:
                res.extend(self.base[b][entity_name].get_all(formula=formula))
        return res

    def find_one(self, entity_name, fields=None, formula=None, project=None, view=None):
        return self.find(entity_name, fields=fields, formula=formula, project=project, view=view)[0]

    def update(self, entity_name, where=None, id=None, fields=None, project=None):
        record = {}
        if where and type(where) == dict:
            records = self.find_one(entity_name, formula="{{{field}}}='{value}'".format(field=where.items()[0][0],
                                                                                        value=where.items()[0][1]))
            record['id'] = records['id']
        else:
            if id:
                record['id'] = id
            else:
                raise ValueError("Need to supply an ID to update.")
        if not fields:
            raise ValueError("Need to supply a dict describing column/values to update")
        else:
            if project and project in self.base.keys():
                print('populating proper project' )
                print(project )
                print(id )
                try:
                    return self.base[project][entity_name].update(id, fields=fields)
                except:
                    pass
            else:
                for b in self.base.keys():
                    try:
                        self.base[b][entity_name].update(id, fields=fields)
                    except:
                        pass


    def rec(self, record_id):
        if "." in record_id:
            base,id = record_id.split('.')
            return self._rec[base][id]

class Persona(SessionManager):

    def _init__(self):
        SessionManager.__init__(self)
        self.build_all_sessions()

        self.project = None
        self.entity = None
        self.shot = None
        self.sequence = None
        self.note = None
        self.version = None




class Base(object):
    def __init__(self, sm, name):
        self.name = name

    def init_tables(self):
        pass


class Project(object):
    def __init__(self, name, sessionmanager):
        self.base = sessionmanager.base[name]

    def initialize_entities(self):
        pass



class CacheWrap():
    pass

