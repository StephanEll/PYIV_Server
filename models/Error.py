'''
Created on 08.05.2014

@author: henrik
'''

class ErrorCode:
    NOT_UNIQUE = 11

class Error(object):
    '''
    classdocs
    '''


    def __init__(self, type, message):
        self.type = type
        self.message = message