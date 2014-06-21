'''
Created on 03.05.2014

@author: Henrik
'''

import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb
from util import base_classes, helper


class GcmData(base_classes.ModelBase):
    
    gcm_id = ndb.StringProperty()
    device_id = ndb.StringProperty()
    isActive = ndb.BooleanProperty()
    

class User(auth_models.User, base_classes.ModelBase):
    
    mail = ndb.StringProperty()

    gcmIds = ndb.StructuredProperty(GcmData, repeated = True)
    wins = ndb.KeyProperty(kind='User', repeated= True)    
    defeats = ndb.KeyProperty(kind='User', repeated= True)
    validated = ndb.BooleanProperty(default = False)
    
    @property
    def name(self):
        return self.auth_ids[0]
    
    @property
    def authToken(self):
        return self._authToken

    @authToken.setter
    def authToken(self, value):
        self._authToken = value


            