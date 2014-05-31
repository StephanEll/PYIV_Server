'''
Created on 03.05.2014

@author: Henrik
'''

import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb
from util import base_classes, helper

class User(auth_models.User, base_classes.ModelBase):
    
    mail = ndb.StringProperty()
    cgm_ids = ndb.StringProperty(repeated = True)
    wins = ndb.KeyProperty(kind='User', repeated= True)    
    defeats = ndb.KeyProperty(kind='User', repeated= True)
    validated = ndb.BooleanProperty(default = False)
    
    @property
    def authToken(self):
        return self._authToken

    @authToken.setter
    def authToken(self, value):
        self._authToken = value


            