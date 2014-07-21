from user_handlers import user_required
from util.base_classes import BaseHandler
from google.appengine.ext import ndb
from models.game_persistence import *
import logging, time, datetime
from models.Error import ErrorCode, Error
from util.helper import NotificationType, player_status_of_user, opponent_status_of_user
from util import messages
from models.user import User

class RoundHandler(BaseHandler):
    
    def get(self, round_id):
        requestedRound = Round.get_by_id(int(round_id))
        self.send_json(requestedRound.to_dict())
        
    def post(self):
        roundJson = self.get_json_body()
        roundObj = Round.create_from_json(roundJson)
        round_key = roundObj.put()
        
        roundDict = roundObj.to_dict()
        roundDict['id'] = round_key.id()
        self.send_json(roundDict)
        
        
class PlayerStatusHandler(BaseHandler):
    
    def get(self, id):
        playerStatus = PlayerStatus.get_by_id(int(id));
        self.send_json(playerStatus.to_dict())
    
class GameDataHandler(BaseHandler):
    
    def get(self, id, user=None):
        gameData = GameData.get_by_id(int(id))
        self.send_json(gameData.to_dict())
    
    @user_required
    def put(self, user):
        game_json = self.get_json_body()
        game = GameDataHandler.update_game(game_json, user)
        self.send_json(game.to_dict())
        
    @classmethod
    def update_game(cls, json, user):
        game = GameData.get_by_id(int(json['Id']))
        game.put()
        
        users_player_status_json = player_status_of_user(json, user)
        users_player_status = PlayerStatus.get_by_id(int(users_player_status_json['Id']), game.key)
        users_player_status.update_from_json(users_player_status_json)
        users_player_status.put()
        
        
        opponent = user.opponent_in_game(json)
        
        BaseHandler.send_push_notification(opponent, 
                                    messages.OPPONENT_MADE_MOVE_TITLE, 
                                    messages.OPPONENT_MADE_MOVE%user.name, 
                                    NotificationType.CONTINUE, 
                                    {})
        
        return game
        
        
    @user_required
    def delete(self, user):
        game_json = self.get_json_body()
        game = GameData.get_by_id(int(game_json['Id']))
        game.key.delete()
        ndb.delete_multi(PlayerStatus.query(ancestor=game.key).iter(keys_only = True))
        
        
        opponent = user.opponent_in_game(game_json)
               
        BaseHandler.send_push_notification(opponent, 
                                    messages.CHALLENGE_DECLINED_TITLE, 
                                    messages.CHALLENGE_DECLINED%user.name, 
                                    NotificationType.CHALLENGE_DENIED, 
                                    {})
        self.send_json({})
    
    
    @user_required
    def post(self, user):
        game_data_json = self.get_json_body()
        
        opponent = user.opponent_in_game(game_data_json)
        challenger_name = user.name

        if self._already_running_game_against_opponent(game_data_json):
            self.send_error(Error(ErrorCode.DUBLICATED, "You already entered combat against this player."))
            return
        
        gameData = GameData()
        gameDataKey = gameData.put()
        
        
        for playerStatusJson in game_data_json['PlayerStatus']:
            playerStatus = PlayerStatus.create_from_json(playerStatusJson, gameDataKey)
            playerStatusKey = playerStatus.put()
            
            
        BaseHandler.send_push_notification(opponent, 
                                    challenger_name + " attacks your village", 
                                    "Defend yourself!", 
                                    NotificationType.SYNC,
                                    {}
                                    )
            
        self.send_json(gameDataKey.get().to_dict())
        
    def _already_running_game_against_opponent(self, game_data_json):
        player1_key = ndb.Key('User', int(game_data_json['PlayerStatus'][0]['Player']['Id']))
        player2_key = ndb.Key('User', int(game_data_json['PlayerStatus'][1]['Player']['Id']))
        player1_status_list = PlayerStatus.query(PlayerStatus.player == player1_key).fetch()
        player1_game_keys = map(lambda status: status.key.parent(), player1_status_list)
        player2_status_list = PlayerStatus.query(PlayerStatus.player == player2_key).fetch()
        player2_game_keys = map(lambda status: status.key.parent(), player2_status_list)
        
        for key in player1_game_keys:
            if key in player2_game_keys:
                return True
        
        return False
        
class GameDataCollectionHandler(BaseHandler):
    
    @user_required
    def get(self, user):
        
        game_data_list = GameData.get_all_by_user(user)
        self.send_json({'modelList':map(lambda x: x.to_dict(), game_data_list)})
        
    @user_required
    def put(self, user):
        
        #Update users player_status
        unsynced_games_json = self.get_json_body()
        
        for game_json in unsynced_games_json:
            GameDataHandler.update_game(game_json, user)
        
        #send list
        timestamp = datetime.datetime.now()
        game_data_list = GameData.get_all_by_user(user)
        self.send_json(
                       {
                        'modelList': map(lambda x: x.to_dict(), game_data_list),
                        'Timestamp': timestamp
                        })
        
        
    
    
