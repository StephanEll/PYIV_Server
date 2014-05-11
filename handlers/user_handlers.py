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
    
    def sendError(self, error):
        self.sendJson(error.__dict__)
        self.response.set_status(BAD_REQUEST) 
        
    def getJsonBody(self):
        logging.critical(self.request.body)
        return json.decode(self.request.body)
    
    def createAuthorizationToken(self, user):
        id = user.get_id()
        auth_token = self.store().user_model().create_auth_token(id)
        return {'id': str(id), 'token': auth_token }

class PlayerHandler(BaseHandler):
    
    def get(self):
        self.response.out.write("Hallo Welt")
    
    def post(self):
        client_user = self.getJsonBody()
        
        name = client_user['Name']
        password = client_user['Password']
        mail = client_user['Mail']

        if mail == None: #optional mail was denoted
            success, user = self.store().user_model().create_user(name, unique_properties=['mail'], mail=mail, password_raw=password)
        else: #store without mail
            success, user = self.store().user_model().create_user(name, password_raw=password)
        
        self._sendResponse(success, user)
        
    def _sendResponse(self, isSuccessfulCreated, user):
        if isSuccessfulCreated:
            user_info = self.createAuthorizationToken(user)
            self.sendJson(user_info)
        else:
            error = self._createNotUniqueError(user)
            self.sendError(error)
    
    def _createNotUniqueError(self, propertiesThatAreNotUnique):
        propertiesThatAreNotUnique = map(lambda x: "nickname" if x == "auth_id" else x, propertiesThatAreNotUnique)
        return Error(ErrorCode.NOT_UNIQUE, "The following fields are already in use: "+ string.join(propertiesThatAreNotUnique, ' and '))
        


        
class LoginHandler(BaseHandler):
    
    def post(self):
        login_data = self.getJsonBody()
        name = login_data['Name']
        password = login_data['Password']
        
        
        try:
            user = self.store().user_model().get_by_auth_password(name, password)
            auth_data = self.createAuthorizationToken(user)
            self.sendJson(auth_data)
        except (auth_models.auth.InvalidAuthIdError, auth_models.auth.InvalidPasswordError) as e:
            message = "Username or password is incorrect. Please try again."
            error = Error(ErrorCode.INVALID_LOGIN, message)
            self.sendError(error)
    