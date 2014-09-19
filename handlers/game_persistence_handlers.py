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
        logging.info("update game json: "+str(json))
        game = GameData.get_by_id(int(json['Id']))
        game.put()
        
        users_player_status_json = player_status_of_user(json, user)
        users_player_status = PlayerStatus.get_by_id(int(users_player_status_json['Id']), game.key)
        users_player_status.update_from_json(users_player_status_json)
        
        
        opponent = user.opponent_in_game(json)
        
        opponent_player_status_json = opponent_status_of_user(json, user)
        opponent_player_status = PlayerStatus.get_by_id(int(opponent_player_status_json['Id']), game.key)
        
        #check if rounds are finished and add new round
        
        rounds_complete = users_player_status.is_latest_round_complete() and opponent_player_status.is_latest_round_complete()
        game_is_over = users_player_status.has_lost() or opponent_player_status.has_lost()
        
        if rounds_complete and not game_is_over:
                        
            users_player_status.rounds.append(Round())
            opponent_player_status.rounds.append(Round())
            opponent_player_status.put()
            logging.info("add new round")
        
        users_player_status.put()
        
        if rounds_complete and game_is_over:
            GameDataHandler._game_is_over(users_player_status, opponent_player_status, user, opponent)
        else:
            BaseHandler.send_push_notification(opponent, 
                                        messages.OPPONENT_MADE_MOVE_TITLE, 
                                        messages.OPPONENT_MADE_MOVE%user.name, 
                                        NotificationType.CONTINUE, 
                                        {})
        
        return game.key.get()
    
    @classmethod    
    def _game_is_over(self, users_player_status, opponent_player_status, user, opponent):
        message = ""
            
        if users_player_status.has_lost() and opponent_player_status.has_lost():
            message = messages.GAME_DRAW
            user.draws.append(opponent.key)
            opponent.draws.append(user.key)
            logging.info("Game ended in a draw")
        elif opponent_player_status.has_lost():
            message = messages.GAME_LOST
            user.wins.append(opponent.key)
            opponent.defeats.append(user.key)
            logging.info("Game won")
        else:
            message = messages.GAME_WON
            user.defeats.append(opponent.key)
            opponent.wins.append(user.key)
            logging.info("Game lost")
            
        user.put()
        opponent.put()
        BaseHandler.send_push_notification(opponent, 
                                messages.GAME_ENDED, 
                                message%user.name, 
                                NotificationType.SYNC, 
                                {})
        
    @user_required
    def delete(self, user):
        game_json = self.get_json_body()
        game = GameData.get_by_id(int(game_json['Id']))
        
        has_ended = game.has_ended()
        
        ndb.delete_multi(PlayerStatus.query(ancestor=game.key).iter(keys_only = True))
        game.key.delete()
        
        
        
        if not has_ended:
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
                game = key.get()
                if not game.has_ended():
                    return True
        
        return False
        
class GameDataCollectionHandler(BaseHandler):
    
    def get_games_and_delete_old(self, user):
        game_data_list = GameData.get_all_by_user(user)
        
        delete_keys = []
        active_games = []
        
        for game in game_data_list:
            delta_time = datetime.datetime.now() - game.updatedAt
            two_days_in_seconds = 2 * 24 * 60 * 60
            if delta_time.total_seconds() > two_days_in_seconds and game.has_ended():
                delete_keys.append(game.key)
            else:
                active_games.append(game)
                
        for game_key in delete_keys:
            ndb.delete_multi(PlayerStatus.query(ancestor=game_key).iter(keys_only = True))
            game_key.delete()
        
        return active_games
    
    @user_required
    def get(self, user):
        
        self.send_json({'modelList':map(lambda x: x.to_dict(), self.get_games_and_delete_old(user))})
        
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
                        'modelList': map(lambda x: x.to_dict(), self.get_games_and_delete_old(user)),
                        'Timestamp': timestamp
                        })
        
        
    
    
