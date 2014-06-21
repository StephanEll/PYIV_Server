import webapp2, urllib, logging
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb
from webapp2_extras import json
from httplib import BAD_REQUEST
from util.helper import default_json_serializer
from google.appengine.api import urlfetch
from urllib import urlencode


class BaseHandler(webapp2.RequestHandler):
    
    def auth(self):
        return auth_models.auth.get_auth()

    def store(self):
        return auth_models.auth.get_store()
    
    def send_json(self, obj):
        self.response.out.write(json.encode(obj, default=default_json_serializer))
    
    def send_error(self, error):
        self.send_json(error.__dict__)
        self.response.set_status(BAD_REQUEST) 
        
    def get_json_body(self):
        return json.decode(self.request.get('model'))
    
    def send_push_notification(self, user, ticker, content_title, content_text, data, collapse_key=None):
        url = "https://android.googleapis.com/gcm/send"
        header = {
                  'Content-Type': 'application/json',
                  'Authorization' : 'key=AIzaSyB89zmTa7ENXgKs-rbWY-wtqN7NzLWoDUI'
                  }
        
        if data == None:
            data = {}
        
        data['ticker'] = ticker
        data['content_title'] = content_title
        data['content_text'] = content_text
        
        payload = {
                   'registration_ids' : map(lambda data: data.gcm_id, filter(lambda data: data.isActive == True, user.gcmIds)),
                   'data' : data
                   }
        
        
        
        if collapse_key != None : payload['collapse_key'] = collapse_key
        
        logging.info('PAYLOAD::: '+ str(payload))
        
        if payload['registration_ids'] != []:
            result = urlfetch.fetch(url=url,
                                    payload=json.encode(payload),
                                    method=urlfetch.POST,
                                    headers=header)
            logging.info("RESULTSTATUS: " + str(result.status_code)+ " RESULT: " + str(result.content))
        
        return result

    

class ModelBase(ndb.Model):
    
    def to_dict(self, include=None, exclude=None):
        
        results = super(ModelBase, self).to_dict(include=include, exclude=exclude)
        results = self._include_in_dict(results, exclude)
        
        if self.key is not None:
            results["id"] = self.key.id()
            
        return {key: value for key, value in results.iteritems() if value != []}
        
        
        
    def _include_in_dict(self, results, exclude=None):
        return results
