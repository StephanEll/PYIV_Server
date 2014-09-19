from util import helper, base_classes
from google.appengine.ext import ndb
from models.user import User
from webapp2 import logging

class ScoreResult(base_classes.ModelBase):
    
    remainingVillageLifepoints = ndb.IntegerProperty()
    missedShotCount = ndb.IntegerProperty()
    killCount = ndb.IntegerProperty()
    hitCount = ndb.IntegerProperty()
    extraPoints = ndb.IntegerProperty()
    
    @classmethod
    def create_from_json(cls, json):
        scoreResult = ScoreResult()
        scoreResult.update_from_json(json)
        return scoreResult
    
    def update_from_json(self, json):
        self.remainingVillageLifepoints= json['RemainingVillageLifepoints']
        self.missedShotCount= json['MissedShotCount']
        self.killCount= json['KillCount']
        self.hitCount= json['HitCount']
        self.extraPoints= json['ExtraPoints']


class Round(base_classes.ModelBase):
    
    sentAttackerIds = ndb.StringProperty(repeated=True)
    scoreResult = ndb.StructuredProperty(ScoreResult)
    
    
    @classmethod
    def create_from_json(cls, json):
        logging.info("create from json:  test " + str(json))
        round = Round()
        round.sentAttackerIds = json['SentAttackerIds']
        if json["ScoreResult"] != None:
            round.scoreResult = ScoreResult.create_from_json(json['ScoreResult'])
        return round
        
        
class PlayerStatus(base_classes.ModelBase):
    
    player = ndb.KeyProperty(kind=User)
    isChallengeAccepted = ndb.BooleanProperty()
    gold = ndb.IntegerProperty()
    indianId = ndb.StringProperty()
    rounds = ndb.LocalStructuredProperty(Round, repeated=True)
    
    def is_latest_round_complete(self):
        return self.rounds[-1].scoreResult != None
    
    def has_lost(self):
        return self.is_latest_round_complete() and self.rounds[-1].scoreResult.remainingVillageLifepoints <= 0
         
    @classmethod
    def create_from_json(cls, json, parentKey):
        
        playerStatus = PlayerStatus(parent=parentKey)
        playerStatus.player = ndb.Key('User', int(json["Player"]["Id"]))
        
        playerStatus.update_from_json(json)
        
        return playerStatus
    
    
    def update_from_json(self, json):
        
        
        rounds = []
        for round in json['Rounds']:
            rounds.append(Round.create_from_json(round))
            
        self.indianId = json["IndianId"]
        self.isChallengeAccepted = json["IsChallengeAccepted"]
        self.gold = json["Gold"]
        self.rounds = rounds
    
    
    def _include_in_dict(self, results, exclude=None):
        
        if helper.valueNotInList('player', exclude):
            playerObj = self.player.get()
            results['player'] = playerObj.to_dict(exclude=['password'])
        
        return results
            
            
class GameData(base_classes.ModelBase):
    
    createdAt = ndb.DateTimeProperty(auto_now_add=True)
    updatedAt = ndb.DateTimeProperty(auto_now=True, indexed=True)
    
    @classmethod
    def get_all_by_user(cls, user):
        player_status_list = PlayerStatus.query(PlayerStatus.player == user.key).fetch()
        keys = map(lambda x: x.key.parent(), player_status_list)
        game_data_list = ndb.get_multi(keys)
        return sorted(game_data_list, key=lambda game: game.updatedAt, reverse=True)
    
    def has_ended(self):
        player_status = PlayerStatus.query(ancestor=self.key).fetch(2)
        
        rounds_complete = player_status[0].is_latest_round_complete() and player_status[1].is_latest_round_complete()
        logging.info('rounds complete?: '+str(rounds_complete))
        someone_lost = player_status[0].has_lost() or player_status[1].has_lost()
        logging.info('someone lost?: '+str(someone_lost))
        
        
        return rounds_complete and someone_lost

    
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

    
        
        
            
