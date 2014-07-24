'''
Created on 08.05.2014

@author: henrik
'''

class ErrorCode:
    NOT_UNIQUE = 11
    INVALID_LOGIN = 12
    ACCESS_DENIED = 13
    NOT_FOUND = 14
    DUBLICATED = 15
    LOGGED_IN_ON_OTHER_DEVICE = 16

class Error(object):
    '''
    classdocs
    '''
    MESSAGE_LOGGED_IN_ON_OTHER_DEVICE = "You are already active on another device. Please log out there first."
    MESSAGE_AUTH_DATA_NOT_VALID = "The auth data isn't valid."
    MESSAGE_INCORRECT = "Username or password is incorrect. Please try again."
    MESSAGE_PLAYER_NOT_FOUND = "The requestest player was not found. Make sure you spelled the name correct."
    MESSAGE_IN_USE = "The following fields are already in use: "

    def __init__(self, type, message):
        self.type = type
        self.message = message