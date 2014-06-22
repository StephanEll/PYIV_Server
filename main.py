import webapp2
from handlers.user_handlers import *
from handlers.game_persistence_handlers import *

class TestHandler(BaseHandler):
    def get(self):
        self.response.out.write("Hello World, App Engine is running!")


routes = [
          #Register
          webapp2.Route(r'/player', handler=PlayerHandler, name='player', schemes=['http', 'https']), 
          #Login
          webapp2.Route(r'/player/login', handler=LoginHandler, name='login', schemes=['http', 'https']), 
          #Search
          webapp2.Route(r'/player/search/<name:\w+>', handler=PlayerHandler, handler_method='search', name='player_search', schemes=['http', 'https']), 
          #By Auth Data

          #Rounds
          webapp2.Route(r'/rounds/<round_id:\d+>', handler=RoundHandler, name='round', schemes=['http', 'https']), 
          webapp2.Route(r'/rounds', handler=RoundHandler, name='round', schemes=['http', 'https']),
          
          #PlayerStatus
          webapp2.Route(r'/playerStatus/<id:\d+>', handler=PlayerStatusHandler, name='playerStatus', schemes=['http', 'https']),
          webapp2.Route(r'/playerStatus', handler=PlayerStatusHandler, name='playerStatus', schemes=['http', 'https']),
          
          #GameData
          webapp2.Route(r'/gameData/<id:\d+>', handler=GameDataHandler, name='gameData', schemes=['http', 'https']),
          webapp2.Route(r'/gameData', handler=GameDataHandler, name='gameData', schemes=['http', 'https']),

          #GameCollection
          webapp2.Route(r'/gameDataCollection', handler=GameDataCollectionHandler, name='gameDataCollection', schemes=['http', 'https']),

          #Google Cloud Messaging
          webapp2.Route(r'/gcm', handler=GcmHandler, name='gcm', schemes=['http', 'https']),

          #test
          webapp2.Route(r'/', handler=TestHandler, name='test', schemes=['http', 'https']),
          
        ]




config = {
  'webapp2_extras.auth': {
    'user_model': 'models.user.User',
  }
}

application = webapp2.WSGIApplication(routes, debug=True)
