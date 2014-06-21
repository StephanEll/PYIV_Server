from util import helper, base_classes
from google.appengine.ext import ndb
from models.user import User
from webapp2 import logging

class Round(ndb.Model):
    
    sentAttackerIds = ndb.StringProperty(repeated=True)
    remainingVillageLifepoints = ndb.IntegerProperty()
    
    @classmethod
    def create_from_json(cls, json):
        round = Round()
        round.sentAttackerIds = json['SentAttackerIds']
        round.remainingVillageLifepoints = json['RemainingVillageLifepoints']
        return round
        
        
        
class PlayerStatus(base_classes.ModelBase):
    
    player = ndb.KeyProperty(kind=User)
    isChallengeAccepted = ndb.BooleanProperty()
    indianId = ndb.StringProperty()
    rounds = ndb.LocalStructuredProperty(Round, repeated=True)
    
    @classmethod
    def create_from_json(cls, json, parentKey):
        
        playerStatus = PlayerStatus(parent=parentKey)
        playerStatus.player = ndb.Key('User', int(json["Player"]["Id"]))
        rounds = []
        for round in json['Rounds']:
            rounds.append(Round.create_from_json(round))
            
        playerStatus.indianId = json["IndianId"]
        playerStatus.isChallengeAccepted = json["IsChallengeAccepted"]
        playerStatus.rounds = rounds
        return playerStatus
    
    
    def _include_in_dict(self, results, exclude=None):
        
        if helper.valueNotInList('player', exclude):
            playerObj = self.player.get()
            results['player'] = playerObj.to_dict(exclude=['password'])
        
        return results
            
            
class GameData(base_classes.ModelBase):
    
    createdAt = ndb.DateTimeProperty(auto_now_add=True)
    updatedAt = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def get_all_by_user(cls, user):
        player_status_list = PlayerStatus.query(PlayerStatus.player == user.key).fetch()
        keys = map(lambda x: x.key.parent(), player_status_list)
        game_data_list = ndb.get_multi(keys)
        return game_data_list
    
    def _get_player_status(self):
        playerStatus = PlayerStatus.query(ancestor=self.key).fetch(2)
        return map(lambda x: x.to_dict(), playerStatus)
    
    def _include_in_dict(self, results, exclude=None):
        
        if helper.valueNotInList('playerStatus', exclude):
            results['playerStatus'] = self.playerStatus
        return results
    
    playerStatus = property(_get_player_status)
    #challengerStatus through parent/ancestor machanism
    #defenderStatus through parent/ancestor machanism

    
        
        
            