'''

'''
import os
import sys
sys.path.append(os.path.split(__file__)[0])
import vayu


locations = {"LA":
                {"short_name": "LA", 'id':0, 'name':"Los Angeles", 'timezone':"+5:00"},
             "NY":
                {"short_name": "NY", 'id':1, 'name':"New York City", 'timezone':"+3:00"}
            }


permissions = {
                "SysAdmin"
                }

class Tao():

    def listdir(self, path):
        return [i for i in os.listdir(path) if i not in ['.DS_Store', '_main']]



tao = Tao()






class ImageSequence():
    def __init__(self):
        #inherit/init PySeq
        pass

class Role():
    pass

class Person():
    def __init__(self, id):
        self.role = None
        self.full_name = None
        self.id = id
        self.login = None
        self.permissions = None
        self.activeProject = None #placeholder for project assignment per person
        self.activeProjects = [] #placeholder for projects person is assigned

    def updateName(self):
        pass

    def getProjects(self):
        #return associated Projects theyre currently working on, to self.activeProjects
        pass
    def logTime(self):
        #punch a specified amunt of time for self.activeProject
        pass
    def sendMessage(self):
        #send message to recipient from whatever host's account is being used.
        pass









class Facility(object):

    def __init__(self, ac):
        self.ac = ac
        self.type = 'Facility'
        self.locations = locations
        self.location = None
        self.filebase = "/jobs"
        self.projects = {}

        #elf.getProjects()

    def setLocation(self, location):
        self.location = location


    def getEmployees(self):
        return None

    def getProjects(self, ls=False):
        self.projects = dict((p, Project(self, p))  for p in tao.listdir(self.filebase))
        if ls is False: return self.projects
        else: return self.projects.keys()

    def getLicensing(self):
        return None




class Version(object):
    def __init__(self, name):
        self.name = name

        self.width = None
        self.height  = None
        self.extension = None
        self.par = None




class Playlist(object):
    '''
    An abstraction layer to utilize when processing multiple versions.
    '''
    def __init__(self):
        pass



class NukeScript(object):

    def __init__(self):
        self.name = None
        self.path = None
        




class Shot(object):
    def __init__(self, parent, name,  id=None, ):
        self.type = 'Shot'
        if parent.type:
            if parent.type=='Sequence':
                self.sequence = parent #This needs to be fleshed out.
                self.project = self.sequence.project
                self.ac = self.sequence.ac
            elif parent.type=='Project:':
                self.project = parent
                self.ac = self.project.ac
        self.name = name
        self.id = id
        self.base = self.ac.base[self.project.name]['Shot']



    def add_task(self, name, descr=None):
        return self.project.add_task(name, shot_id=self.id, descr=descr)

    def set_status(self, status):
        self.base.update(self.id, {"status": status})

    def set_description(self, descr):
        self.base.update(self.id, {"description": descr})

    def set_frame_range(self, fin, fout):
        return self.base.update(self.id, {"frame_in": fin, "frame_out": fout})

    def add_note(self, note, task=None):
        """
        If task is given the note will be at the task level, otherwise its visible at the shot level.
        :param note:
        :param task:
        :return:
        """




class Sequence(object):
    def __init__(self, project, name, id=None):
        self.type = 'Sequence'

        self.project = project
        self.ac = self.project.ac
        self.shots = {}
        self.name = name
        self.id = id
        self.filebase = "%s/%s" %(self.project.filebase, self.name)

        self.latestComps = {}



    def add_shot(self, name):
        self.project.add_shot(name, seq=self.name )

    def get_shots(self):
        try:
            return [f for f in self.ac.table[self.project.name]['Shot'] if f.get('fields') and f['fields']['sequence'] == [str(self.id)]]
        except:
            return None

class Project(object):
    def __init__(self, facility, name, id=None):
        self.type = 'Project'
        self.facility = facility
        self.ac = self.facility.ac
        self.name = name
        self.id = id
        self.full_name = None
        self.filebase = "%s/%s" %(self.facility.filebase, self.name)
        self.id_seq = {}
        self.seq_id = {}



        self.episodes = {}

        self.map_id()
        #self.get_sequences()



    def get_shots(self):
        shots = self.ac.table[self.name]['Shot']
        return [Shot(Sequence(self, self.ac._rec[self.name][s['fields']['sequence'][0]]['fields']['name'], id=s['fields']['sequence'][0]), s['fields']['name']  , id=s['id']) for s in shots]


    def get_tasks(self):
        tasks = self.ac.table[self.name]['Task']
        return tasks

    def add_shot(self, name, seq=None):
        '''
        :param name: str to name the shot
        :param seq: option
        :return:
        '''
        payload = {'name': name}
        if seq:
            if seq in self.seq_id.keys():
                seqid = self.seq_id[seq]
                print seqid
            else:
                sequence = self.add_sequence( seq )
                seqid = sequence.id
            payload['sequence'] = [seqid]
        shot =  self.ac.base[self.name]['Shot'].insert( payload )
        if shot:
            if not seq:
                return Shot(self, shot['id'])

    def add_task(self, name, shot_id=None, descr=None):
        payload = {'name': name}
        if shot_id:
            payload['shot'] = [shot_id]
        if descr:
            payload['descr'] = descr
        return self.ac.base[self.name]['Task'].insert( payload )

    def add_note(self, message, shot_id=None, task_id=None):

        payload = {'message': message}

        if task_id:
            payload['task'] = [task_id]
            if shot_id:
                payload['shot'] = [shot_id]
            else:
                payload['shot'] = self.ac._rec[self.name][task_id]['fields']['shot']

        return self.ac.base[self.name]['Note'].insert( payload )


    def add_sequence(self, name):
        ret =  self.ac.base[self.name]['Sequence'].insert({'name': name})
        s = Sequence(self, name, ret['id'])
        return s

    def get_sequences(self):
        self.seq_id = dict(( i['fields']['name'], i['id'] ) for i in self.ac.table[self.name]['Sequence'])
        self.id_seq = dict((v, k) for k,v in self.seq_id.iteritems())
        self._seq_dict = dict((k, Sequence(self, k, id=v ) ) for k,v in self.seq_id.iteritems() )
        return self._seq_dict


    def get_notes(self):
        notes = self.ac.table[self.name]['Note']
        return notes

    def get(self, entity, fields=None, formula=None):
        pass


    def get_all_projects(self):
        return self.facility.ac.session_mapping.keys()

    def map_id(self):
        self.id = self.facility.ac.session_mapping[self.name]
        print self.id

    def status(self):
        rec = self.facility.ac.config['BASE'].get_all(fields=['status'], formula="{project_code}='%s'" %self.name)
        if len(rec)>0:
            return rec[0]['fields']['status']


    def shot(self, name):
        try:
            return [Shot(Sequence(self, self.ac._rec[self.name][s['fields']['sequence'][0]]['fields']['name'], id=s['fields']['sequence'][0]), s['fields']['name'], id=s['id']) for s in self.ac.table[self.name]['Shot'] if name==str(s['fields']['name'])][0]
        except Exception as e:
            print e

    def sequence(self, name):
        try:
            return [Sequence(self,  name, id=s['id']) for s in self.ac.table[self.name]['Sequence'] if name==str(s['fields']['name'])][0]
        except Exception as e:
            print e


class SGCacheWrap():
    pass





class Multivac(vayu.SessionManager):
    '''
    context driver for each class instance. Can limit and communicate between the classes.
    Inherits the facility as main object class
    '''
    def __init__(self):
        #vayu.SessionManager.__init__(self)
        super(Multivac, self).__init__()

        self.get_sessions()





    def ss(self, proj, seq, shot, verify=False ):
        self.project = Project(self.facility, proj )
        self.sequence = Sequence(self.project, seq)
        self.shot = Shot(self.sequence, shot)

    def connect_projects(self):
        for name in self.session_mapping.keys():
            self.project[name] = Project(self.facility, name)

    def setup(self):
        self.build_all_sessions()
        self.facility = Facility(self)
        self.project = {}

        self.connect_projects()

        self.setup_complete.emit()
