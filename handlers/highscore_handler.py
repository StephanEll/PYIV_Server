from user_handlers import user_required
from util.base_classes import BaseHandler
from google.appengine.ext import ndb
from models.game_persistence import *
import logging, time, datetime
from models.Error import ErrorCode, Error
from util.helper import NotificationType, player_status_of_user, opponent_status_of_user
from util import messages
from models.user import User


class HighscoreHandler(BaseHandler):
    
    @user_required
    def get(self, user):
        
        
        
        top5 = User.query().order(-User.score).fetch(5)
        
        highscore = []
        
        for index, top_user in enumerate(top5):
            highscore_entry = self._create_highscore_model(top_user.name, top_user.score, index+1)
            highscore.append(highscore_entry)
        
        if user not in top5:
            user_rank = User.query(User.score >= user.score).count()
            highscore[-1] = self._create_highscore_model(user.name, user.score, user_rank)
            
        self.send_json(highscore)
            
            
        
    def _create_highscore_model(self, name, score, position):
        return { 
                'playerName' : name, 
                'score' : score, 
                'position' : position  
                }
        