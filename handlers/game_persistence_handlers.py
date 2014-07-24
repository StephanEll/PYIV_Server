from user_handlers import user_required
from util.base_classes import BaseHandler
from google.appengine.ext import ndb
from models.game_persistence import *
import logging
from models.Error import ErrorCode, Error
from util.helper import NotificationType, player_status_of_user, opponent_status_of_user
from util import messages

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
        
        logging.info(str(game_json))
        
        game = GameData.get_by_id(int(game_json['Id']))
        game.put()
        
        users_player_status_json = player_status_of_user(game_json, user)
        users_player_status = PlayerStatus.get_by_id(int(users_player_status_json['Id']), game.key)
        users_player_status.update_from_json(users_player_status_json)
        users_player_status.put()
        self.send_json(game.to_dict())
        
    @user_required
    def delete(self, user):
        game_json = self.get_json_body()
        game = GameData.get_by_id(int(game_json['Id']))
        game.key.delete()
        ndb.delete_multi(PlayerStatus.query(ancestor=game.key).iter(keys_only = True))
        
        opponent_status = opponent_status_of_user(game_json, user)
        opponent = User.get_by_id(int(opponent_status['Player']['Id']))
        
        self.send_push_notification(opponent, 
                                    messages.CHALLENGE_DECLINED_TITLE, 
                                    messages.CHALLENGE_DECLINED%opponent.name, 
                                    NotificationType.CHALLENGE_DENIED, 
                                    {})
        self.send_json({})
    
    
    @user_required
    def post(self, user):
        game_data_json = self.get_json_body()
        
        opponent = User.get_by_id(int(game_data_json['PlayerStatus'][1]['Player']['Id']))
        challenger_name = game_data_json['PlayerStatus'][0]['Player']['Name']
        self.send_push_notification(opponent, 
                                    challenger_name + " attacks your village", 
                                    "Defend yourself!", 
                                    NotificationType.SYNC,
                                    {}
                                    )

        if self._already_running_game_against_opponent(game_data_json):
            self.send_error(Error(ErrorCode.DUBLICATED, "You already entered combat against this player."))
            return
        
        gameData = GameData()
        gameDataKey = gameData.put()
        
        
        for playerStatusJson in game_data_json['PlayerStatus']:
            playerStatus = PlayerStatus.create_from_json(playerStatusJson, gameDataKey)
            playerStatusKey = playerStatus.put()
            
            
            
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
        
        logging.info("user: " + str(user))
        logging.info("unsynced games json: " + str(unsynced_games_json))
        
        for game_json in unsynced_games_json:
            game_key = ndb.Key(GameData, int(game_json['Id']))
            users_player_status_json = player_status_of_user(game_json, user)
            logging.info("users_player_status_json: " + str(users_player_status_json))
            player_status_key = ndb.Key(GameData, int(game_json['Id']), PlayerStatus, int(users_player_status_json['Id']))
            
            game, player_status = ndb.get_multi([game_key, player_status_key])
            
            update_list = []
            
            if player_status != None:
                player_status.update_from_json(users_player_status_json)
                update_list.append(player_status)
                logging.info("updated_player_status " + str(player_status))
            
            if game != None:
                update_list.append(game)
                
            ndb.put_multi(update_list)
        
        
        #send list
        self.get(user=user)
        
        
    
    
