import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.ext import ndb
from webapp2_extras import json
from httplib import BAD_REQUEST
from util.helper import default_json_serializer

class BaseHandler(webapp2.RequestHandler):
    
    def auth(self):
        return auth_models.auth.get_auth()

    def store(self):
        return auth_models.auth.get_store()
    
    def sendJson(self, obj):
        self.response.out.write(json.encode(obj, default=default_json_serializer))
    
    def sendError(self, error):
        self.sendJson(error.__dict__)
        self.response.set_status(BAD_REQUEST) 
        
    def getJsonBody(self):
        return json.decode(self.request.get('model'))
    

class ModelBase(ndb.Model):
    
    def to_dict(self, include = None, exclude = None):
        
        results = super(ModelBase, self).to_dict(include=include, exclude=exclude)
        results = self._include_in_dict(results, exclude)
        
        if self.key is not None:
            results["id"] = self.key.id()
            
        return {key: value for key, value in results.iteritems() if value != []}
        
        
        
    def _include_in_dict(self, results, exclude = None):
        return results