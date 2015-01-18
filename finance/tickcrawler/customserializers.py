import datetime
import msgpack

def decode(obj):
    if '__datetime__' in obj and obj['__datetime__'] == True and 'as_str' in obj:
        obj = datetime.datetime.strptime(obj['as_str'], "%Y%m%dT%H:%M:%S.%f%z")
    return obj

def encode(obj):
    if isinstance(obj, datetime.datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f%z")}
    return obj
