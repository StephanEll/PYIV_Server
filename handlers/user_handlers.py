import webapp2
import cgi, logging

import time
import webapp2_extras.appengine.auth.models as auth_models

from webapp2_extras import security, json
import webapp2_extras


class BaseHandler(webapp2.RequestHandler):
    
    def auth(self):
        return auth_models.auth.get_auth()

    def store(self):
        return auth_models.auth.get_store()


class PlayerHandler(BaseHandler):
    
    def get(self):
        return
    def post(self):
        
        
        client_user = json.decode(self.request.body);
        logging.critical(str(client_user))
        
        name = client_user['Name']
        password = client_user['Password']
        mail = client_user['Mail']

        success, user = self.store().user_model().create_user(name, 
                                                              unique_properties=['mail'], 
                                                              mail=mail, 
                                                              raw_password=password
                                                              )
        
        
        if success:
            id = user.get_id()
            auth_token = self.store().user_model().create_auth_token(id)
        
        
            user_info = {'id': id, 
                         'auth_token': auth_token}
        
            self.response.write(json.encode(user_info))
        else:
            self.response.out.write(json.encode(user))
            self.response.set_status(409)
        
