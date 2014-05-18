import webapp2
from user_handlers import BaseHandler
from google.appengine.ext import ndb
from models.game_persistence import *
import logging

class RoundHandler(BaseHandler):
    
    def get(self, round_id):
        logging.critical("RoundId: "+str(round_id))
        requestedRound = Round.get_by_id(int(round_id))
        self.sendJson(requestedRound.to_dict())
        
    def post(self):
        roundJson = self.getJsonBody()
        roundObj = Round.create_from_json(roundJson)
        round_key = roundObj.put()
        
        roundDict = roundObj.to_dict()
        roundDict['id'] = round_key.id()
        self.sendJson(roundDict)
        
        
class PlayerStatusHandler(BaseHandler):
    
    def get(self, id):
        return
    
    def post(self):
        playerStatusJson = self.getJsonBody()
        logging.critical(playerStatusJson)
        PlayerStatus.create_from_json(playerStatusJson)