import logging, string
import webapp2_extras.appengine.auth.models as auth_models
from models.Error import Error, ErrorCode
from util.base_classes import BaseHandler


def user_required(handler):

    def check_login(self, *args, **kwargs):
        user_id = self.request.get('user_id') 
        token = self.request.get('token')
        user, timestamp = self.store().user_model().get_by_auth_token(int(user_id), token)
        if user:
            kwargs['user'] = user
            return handler(self, *args, **kwargs)
        else:
            self.sendError(Error(ErrorCode.ACCESS_DENIED, "Authentication failed"))
            

    return check_login

class AuthorizationBase(BaseHandler):
    def sendAuthorizedUser(self, user):
        """ Authtoken fuer User generieren und alles als Json senden """
        auth_token = self.store().user_model().create_auth_token(user.get_id())
        userDict = user.to_dict(exclude=['password'])
        userDict['authToken'] = auth_token
        userDict['id'] = user.get_id()
        
        self.sendJson(userDict)

class PlayerHandler(AuthorizationBase):
    
    def get(self, user):
        self.sendJson(user.auth_ids)
    
    def post(self):
        client_user = self.getJsonBody()
        
        name = client_user['Name']
        password = client_user['Password']
        mail = client_user['Mail']

        if mail != None: #optional mail was denoted
            mail = mail.lower()
            success, user = self.store().user_model().create_user(name, unique_properties=['mail'], mail=mail, password_raw=password)
        else: #store without mail
            success, user = self.store().user_model().create_user(name, password_raw=password)
        
        self._sendResponse(success, user)
        
    def _sendResponse(self, isSuccessfulCreated, user):
        if isSuccessfulCreated:
            self.sendAuthorizedUser(user)
        else:
            error = self._createNotUniqueError(user)
            self.sendError(error)
    
    def _createNotUniqueError(self, propertiesThatAreNotUnique):
        propertiesThatAreNotUnique = map(lambda x: "nickname" if x == "auth_id" else x, propertiesThatAreNotUnique)
        return Error(ErrorCode.NOT_UNIQUE, "The following fields are already in use: "+ string.join(propertiesThatAreNotUnique, ' and '))
        


        
class LoginHandler(AuthorizationBase):
    
    def post(self):
        login_data = self.getJsonBody()
        name = login_data['Name']
        password = login_data['Password']
        
        try:
            user = self.store().user_model().get_by_auth_password(name, password)
            self.sendAuthorizedUser(user)
        except (auth_models.auth.InvalidAuthIdError, auth_models.auth.InvalidPasswordError) as e:
            message = "Username or password is incorrect. Please try again."
            error = Error(ErrorCode.INVALID_LOGIN, message)
            self.sendError(error)
    