import logging, string, urllib
import webapp2_extras.appengine.auth.models as auth_models
from models.Error import Error, ErrorCode
from util.base_classes import BaseHandler
from models.user import User, GcmData


def user_required(handler):

    def check_login(self, *args, **kwargs):
        user_id = self.request.get('user_id') 
        token = self.request.get('token')
        user, timestamp = self.store().user_model().get_by_auth_token(int(user_id), token)
        if user:
            kwargs['user'] = user
            return handler(self, *args, **kwargs)
        else:
            self.send_error(Error(ErrorCode.ACCESS_DENIED, "Authentication failed"))
            

    return check_login

class AuthorizationBase(BaseHandler):
    def sendAuthorizedUser(self, user):
        """ Authtoken fuer User generieren und alles als Json senden """
        auth_token = self.store().user_model().create_auth_token(user.get_id())
        userDict = user.to_dict(exclude=['password'])
        userDict['authToken'] = auth_token
        userDict['id'] = user.get_id()
        
        self.send_json(userDict)

class PlayerHandler(AuthorizationBase):
    
    def get(self):
        logging.info("get")
        #self.send_json(user.auth_ids)
        
   
    
    def search(self, name):
        name = name.lower()
        user = self.store().user_model().get_by_auth_id(name)
        if user:
            self.send_json(user.to_dict(exclude=['password']))
        else:
            self.send_error(Error(ErrorCode.NOT_FOUND, "The requestest player was not found. Make sure you spelled the name correct."))
        
    def post(self):
        client_user = self.get_json_body()
        
        name = client_user['Name'].lower()
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
            self.send_error(error)
    
    def _createNotUniqueError(self, propertiesThatAreNotUnique):
        propertiesThatAreNotUnique = map(lambda x: "nickname" if x == "auth_id" else x, propertiesThatAreNotUnique)
        return Error(ErrorCode.NOT_UNIQUE, "The following fields are already in use: "+ string.join(propertiesThatAreNotUnique, ' and '))
        

        
    
        
        
        
class LoginHandler(AuthorizationBase):
    
    def get(self):
        auth_data = self.get_json_body()
        user_id = int(auth_data['Id']);
        token = auth_data['AuthToken'];
        
        user, timestamp = self.store().user_model().get_by_auth_token(user_id, token)
        if user:
            self.send_json(user.to_dict(exclude=['password']))
        else:
            self.send_error(Error(ErrorCode.ACCESS_DENIED, "The auth data isn't valid."))
    
    def post(self):
        login_data = self.get_json_body()
        name = login_data['Name'].lower()
        password = login_data['Password']
        
        try:
            user = self.store().user_model().get_by_auth_password(name, password)
            self.sendAuthorizedUser(user)
        except (auth_models.auth.InvalidAuthIdError, auth_models.auth.InvalidPasswordError) as e:
            message = "Username or password is incorrect. Please try again."
            error = Error(ErrorCode.INVALID_LOGIN, message)
            self.send_error(error)
    
    
class GcmHandler(BaseHandler):
    
    @user_required
    def post(self, user):
        gcm_data_json = self.get_json_body()
        device_id = gcm_data_json["DeviceId"]
        gcm_id = gcm_data_json["GcmId"]
        
        logging.info("GCM DATA RECEIVED: "+ device_id + ", " + gcm_id)
        
        existing_gcm_entries = filter(lambda data: data.gcm_id == gcm_id and data.device_id == device_id, user.gcmIds)
        
        if len(existing_gcm_entries) > 0:
            logging.info("Found fitting gcm data in database, go and update it")
            gcm_data = existing_gcm_entries[0]
            gcm_data.isActive = True
        else:
            logging.info("No gcm entry found. Create a new one")
            user.gcmIds.append(GcmData(device_id=device_id, gcm_id=gcm_id, isActive=True))
            
        user.put()
        logging.info("Update player model")


        
    