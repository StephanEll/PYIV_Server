import webapp2
import cgi, logging

import time
import string
import webapp2_extras.appengine.auth.models as auth_models

from webapp2_extras import security, json
import webapp2_extras
from httplib import BAD_REQUEST
from models.Error import Error, ErrorCode

class BaseHandler(webapp2.RequestHandler):
    
    def auth(self):
        return auth_models.auth.get_auth()

    def store(self):
        return auth_models.auth.get_store()
    
    def sendJson(self, obj):
        self.response.out.write(json.encode(obj))


class PlayerHandler(BaseHandler):
    
    def get(self):
        self.response.out.write("Hallo Welt")
    
    def post(self):
        client_user = json.decode(self.request.body);
        
        name = client_user['Name']
        password = client_user['Password']
        mail = client_user['Mail']

        success, user = self.store().user_model().create_user(name, 
                                                              unique_properties=['mail'], 
                                                              mail=mail, 
                                                              raw_password=password
                                                              )
        if success:
            user_info = self._createUserInfo(user)
            self.sendJson(user_info)
        else:
            error = Error(ErrorCode.NOT_UNIQUE, "The following fields are already in use: "+ string.join(user, ','))
            self.response.out.write(json.encode(error.__dict__))
            self.response.set_status(BAD_REQUEST)
        
    def _createUserInfo(self, user):
        id = user.get_id()
        auth_token = self.store().user_model().create_auth_token(id)
        return {'id': str(id), 'auth_token': auth_token }
    
    def _createNotUniqueError(self, propertiesThatAreNotUnique):
        
        error = Error(ErrorCode.NOT_UNIQUE, "The following fields are already in use: "+ string.join(user, ','))
        
        
        