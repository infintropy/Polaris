'''

'''
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
    def __init__(self):
        self.role = None
        self.full_name = None
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
    def __init__(self, sequence, name):
        self.type = 'Shot'
        self.sequence = sequence
        self.name = name
        self.filebase = "%s/%s" %(self.sequence.filebase, self.name)
        self.filebaseCompRender = "%s/img/renders" %self.filebase
        self.filebaseCGRender = "%s/img/comp" %self.filebase
        self.filebase2DScripts = "%s/2D/nk/" %self.filebase


        self.nukeScripts = {}
        self.cgScenes = {}
        self.nukeRenders = {}
        self.cgRenders = {}





    def get2DScripts(self):
        self.nukeScripts = dict((d, sorted([f for f in tao.listdir( "%s/%s" %(self.filebase2DScripts, d))])) for d in tao.listdir(self.filebase2DScripts) )
        return self.nukeScripts

    def getLatestComps(self):
        return Version("%s_%s_%s_v001" %(self.sequence.project.name, self.sequence.name, self.name) )


class Sequence(object):
    def __init__(self, project, name):
        self.type = 'Sequence'
        self.project = project
        self.shots = {}
        self.name = name
        self.filebase = "%s/%s" %(self.project.filebase, self.name)

        self.latestComps = {}

    def getShots(self, ls=False):
        self.shots = dict((s, Shot(self, s))  for s in sorted(tao.listdir(self.filebase)))
        if ls is False: return self.shots
        else: return self.shots.keys()

    def getLatestComps(self, mod=None):
        self.getShots()
        for shotname,shot in self.shots.iteritems():
            self.latestComps[shotname] = shot.getLatestComps()
        return self.latestComps

class Project(object):
    def __init__(self, facility, name):
        self.type = 'Project'
        self.facility = facility
        self.ac = self.facility.ac
        self.name = name
        self.id = None
        self.full_name = None
        self.filebase = "%s/%s" %(self.facility.filebase, self.name)
        self.sequences = {}
        self.episodes = {}

        self.map_id()


        #diagnostic
        self.isEpisodic = False

    def setName(self, name):
        self.name = name

    def getSequences(self, ls=False):
        self.sequences = dict((s, Sequence(self, s))  for s in sorted(tao.listdir(self.filebase)))
        if ls is False: return self.sequences
        else: return sorted(self.sequences.keys())

    def get_shots(self):
        shots = self.ac.table[self.name]['Shot']
        #
        #return shots
        for i in shots:
            print i['fields']['name']

    def get_tasks(self):
        tasks = self.ac.table[self.name]['Task']
        return tasks

    def get_notes(self):
        notes = self.ac.table[self.name]['Note']
        return notes

    def get(self, entity, fields=None, formula=None):
        pass

    def getEpisodes(self, ls=False):
        #use descriptor logic to deduce episodes, then builds an episode dict that contain sequences
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







class SGCacheWrap():
    pass








class Multivac(vayu.SessionManager):
    '''
    context driver for each class instance. Can limit and communicate between the classes.
    Inherits the facility as main object class
    '''
    def __init__(self):
        vayu.SessionManager.__init__(self)
        self.build_all_sessions()
        self.facility = Facility(self)
        self.project = {}

        self.connect_projects()



    def ss(self, proj, seq, shot, verify=False ):
        self.project = Project(self.facility, proj )
        self.sequence = Sequence(self.project, seq)
        self.shot = Shot(self.sequence, shot)

    def connect_projects(self):
        for name in self.session_mapping.keys():
            self.project[name] = Project(self.facility, name)
