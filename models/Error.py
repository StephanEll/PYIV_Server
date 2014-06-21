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

class Error(object):
    '''
    classdocs
    '''


    def __init__(self, type, message):
        self.type = type
        self.message = message