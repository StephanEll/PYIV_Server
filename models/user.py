'''
Created on 03.05.2014

@author: Henrik
'''

import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb
from util.base_classes import ModelBase
from util.helper import opponent_status_of_user


class GcmData(ModelBase):
    
    gcm_id = ndb.StringProperty()
    device_id = ndb.StringProperty()
    isActive = ndb.BooleanProperty()
    
    

class User(auth_models.User, ModelBase):
    
    mail = ndb.StringProperty()

    gcmIds = ndb.StructuredProperty(GcmData, repeated = True)
    wins = ndb.KeyProperty(kind='User', repeated= True)    
    defeats = ndb.KeyProperty(kind='User', repeated= True)
    validated = ndb.BooleanProperty(default = False)
    loggedIn = ndb.BooleanProperty(default = False)
    
    @property
    def name(self):
        return self.auth_ids[0]
    
    @property
    def authToken(self):
        return self._authToken

    @authToken.setter
    def authToken(self, value):
        self._authToken = value
        
    def opponent_in_game(self, game_json):
        opponent_status = opponent_status_of_user(game_json, self)
        opponent = User.get_by_id(int(opponent_status['Player']['Id'])) 
        return opponent

            