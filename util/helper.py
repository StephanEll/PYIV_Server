'''
Created on 24.05.2014

@author: Henrik
'''

class NotificationType:
    SYNC = 1
    CHALLENGE_DENIED = 6



def default_json_serializer(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return (millis/1000)
    
def valueNotInList(strValue, list):
    return not(list != None and strValue in list)
    
    
def player_status_of_user(game_json, user):
    if int(game_json['PlayerStatus'][0]['Player']['Id']) == user.get_id():
        return game_json['PlayerStatus'][0]
    else:
        return game_json['PlayerStatus'][1]
    
def opponent_status_of_user(game_json, user):
    if int(game_json['PlayerStatus'][0]['Player']['Id']) != user.get_id():
        return game_json['PlayerStatus'][0]
    else:
        return game_json['PlayerStatus'][1]
    

