from user_handlers import user_required
from util.base_classes import BaseHandler
from google.appengine.ext import ndb
from models.game_persistence import *
import logging

class RoundHandler(BaseHandler):
    
    def get(self, round_id):
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
        playerStatus = PlayerStatus.get_by_id(int(id));
        self.sendJson(playerStatus.to_dict())
    
class GameDataHandler(BaseHandler):
    
    def get(self, id, user=None):
        gameData = GameData.get_by_id(int(id))
        self.sendJson(gameData.to_dict())
    
    def post(self, user=None):
        gameDataJson = self.getJsonBody()
        
        gameData = GameData()
        gameDataKey = gameData.put()
        
        
        for playerStatusJson in gameDataJson['PlayerStatus']:
            playerStatus = PlayerStatus.create_from_json(playerStatusJson, gameDataKey)
            playerStatusKey = playerStatus.put()
            
        self.sendJson(gameDataKey.get().to_dict())
        
        
        
    
    