'''
Created on 03.05.2014

@author: Henrik
'''

import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb

class User(auth_models.User):
    
    mail = ndb.StringProperty()
    cgm_ids = ndb.StringProperty(repeated = True)
    wins = ndb.KeyProperty(kind='User', repeated= True)    
    defeats = ndb.KeyProperty(kind='User', repeated= True)
    validated = ndb.BooleanProperty(default = False)    