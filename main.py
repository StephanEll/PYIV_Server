import webapp2
from handlers.user_handlers import *

routes = [
          webapp2.Route(r'/player', handler=PlayerHandler, name='player', schemes=['http']), 
        ]


config = {
  'webapp2_extras.auth': {
    'user_model': 'models.user.User',
  }
}

application = webapp2.WSGIApplication(routes, debug=True)
