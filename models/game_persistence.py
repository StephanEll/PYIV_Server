import webapp2, logging
from google.appengine.ext import ndb

class Round(ndb.Model):
    
    sentAttackerIds = ndb.IntegerProperty(repeated=True)
    remainingVillageLifepoints = ndb.IntegerProperty()
    
    @classmethod
    def create_from_json(cls, json):
        round = Round()
        round.sentAttackerIds = json['SentAttackerIds']
        round.remainingVillageLifepoints = json['RemainingVillageLifepoints']
        return round
        
        
        
class PlayerStatus(ndb.Model):
    
    player = ndb.KeyProperty(kind='User')
    rounds = ndb.LocalStructuredProperty(Round, repeated=True)
    
    @classmethod
    def create_from_json(cls, json, parentKey):
        
        rounds = []
        for round in json['Rounds']:
            rounds.append(Round.create_from_json(round))
            
        
        
            