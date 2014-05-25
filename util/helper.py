'''
Created on 24.05.2014

@author: Henrik
'''



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
    
    

    

