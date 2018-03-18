import airtable
import json
import base64
import os
import six
from Queue import Queue
from threading import Thread



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


import time
def queueRunner():

    def do_stuff(q):
      while True:

        print q.get()
        time.sleep(5)
        q.task_done()

    q = Queue(maxsize=0)
    num_threads = 10

    for i in range(10):
      worker = Thread(target=do_stuff, args=(q,))
      worker.setDaemon(True)
      worker.start()

    for x in range(100):
      q.put(x)

    q.join()


# !/usr/bin/env python
import Queue
import threading
import urllib2
import time

hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
         "http://ibm.com", "http://apple.com"]

queue = Queue.Queue()


class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""


def __init__(self, queue):
    threading.Thread.__init__(self)
    self.queue = queue


def run(self):
    while True:
        # grabs host from queue
        host = self.queue.get()

        # grabs urls of hosts and prints first 1024 bytes of page
        url = urllib2.urlopen(host)
        print url.read(1024)

        # signals to queue job is done
        self.queue.task_done()


start = time.time()


def main():
    # spawn a pool of threads, and pass them queue instance
    for i in range(5):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

        # populate queue with data
        for host in hosts:
            queue.put(host)

    # wait on the queue until everything has been processed


queue.join()

main()
print "Elapsed Time: %s" % (time.time() - start)


class SessionManager():
    '''
    This will let me know easier.
    It is assumed that entities are limited to the preconfigured tables.

    We must
        1) Define the sessions: storing the key for the project and its tables.
        2) Define if a project has a default configuration, or if it has entities that can be extended.
           Extending and integrating new entities is quite easy as long as you register them.
           For speed and unlike Shotgun, you can define custom entities at will and not have to enable them site wide.
    '''

    def __init__(self):
        '''
        store session information in a configuration table, retrieve that information and then build a session dict which we will wrap and use to call different projects
        '''
        self.session_mapping = None
        self.session_info = None
        self.base = {}
        self.rec = {}
        self.table = {}
        self.default_entities = None
        # builds the session obj
        self.config = {}
        for s in ['BASE', 'ENTITY']:
            self.config[s] = airtable.Airtable(CONFIG_BASE_KEY, s)
        self.get_sessions()

    def get_sessions(self, all=None):
        opt = ['active']
        if all:
            opt.append('archived')
        self.session_info = self.config['BASE'].get_all(fields=['project_code', 'session_id', 'session_type', 'extra_entities'],
                                                        formula="{status}='active'")
        self.session_mapping = dict((i['fields']['project_code'], i['fields']['session_id']) for i in self.session_info if i['fields'].get('session_type') and i['fields']['session_type']=="Project")
        return self.session_mapping

    def get_project_entities(self):
        pass


    def get_base(self, base):
        self.rec[base] = {}
        for n in self.base[base].keys():
            print "Adding records into main record container for {} in {}".format( base, n )
            b = self.base[base][n].get_all()
            for r in b:
                self.rec[base][r['id']] = r
        return self.rec[base]


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
                    print k
                    kbase = [i for i in self.session_info if i['fields'].get('project_code') and i['fields']['project_code'] == k]

                    if len(kbase)>0:
                        if kbase[0]['fields'].get('extra_entities'):
                            for r in kbase[0]['fields']['extra_entities']:
                                try:
                                    session_entities.append( self.project_entity_ext[r]  )
                                except Exception, e:
                                    pass



                    for e in session_entities:
                        if e in self.base[k].keys():
                            print("INFO:: ALREADY FOUND:: {} >> TABLE:: {} into main session object.".format(k, e) )

                        else:
                            try:
                                self.base[k][e] = airtable.Airtable(v, e)
                                print("INFO:: MAPPED BASE:: {} >> TABLE:: {} into main session object.".format(k, e) )
                            except:
                                print("ERROR:: Couldnt establish base {}:{}".format(k, e) )
                    self.get_base(k)


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



class Entity(object):
    def __init__(self, sm):
        pass


class Project(object):
    def __init__(self, name, sessionmanager):
        self.base = sessionmanager.base[name]

    def get_sequences(self):
        return self.base['Sequence'].get_all()




class CacheWrap():
    pass

