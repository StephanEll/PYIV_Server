import webapp2
from handlers.user_handlers import *
from handlers.game_persistence_handlers import *

routes = [
          #Register
          webapp2.Route(r'/player', handler=PlayerHandler, name='player', schemes=['http']), 
          #Login
          webapp2.Route(r'/player/login', handler=LoginHandler, name='login', schemes=['http']), 

          #Rounds
          webapp2.Route(r'/rounds/<round_id:\d+>', handler=RoundHandler, name='round', schemes=['http']), 
          webapp2.Route(r'/rounds', handler=RoundHandler, name='round', schemes=['http']),
          
          #PlayerStatus
          webapp2.Route(r'/playerStatus', handler=PlayerStatusHandler, name='playerStatus', schemes=['http']),
          
          #GameData
          webapp2.Route(r'/gameData', handler=GameDataHandler, name='gameData', schemes=['http']),
          
           
        ]


config = {
  'webapp2_extras.auth': {
    'user_model': 'models.user.User',
  }
}

application = webapp2.WSGIApplication(routes, debug=True)
