from .JSONToUnicode import to_unicode

#try: import simplejson as json
import json


def dumps(data):
    return json.dumps(data)


def loads(data):
    return json.loads(data)


def dump(f, data, indent=4):
    if isinstance(f, str):
        with open(f, 'wb') as f:
            f.write(encode(data).encode('utf-8'))
    else:
        json.dump(data, f, indent=indent)


def load(f):
    if isinstance(f, str):
        with open(f, 'rb') as f:
            return decode(f.read().decode('utf-8'))
    else:
        return json.load(f.read())


def encode(JSON):
    """
    Encode the data "JSON" as JSON, converting to
    Unicode (instead of a string with Unicode backslash escapes)
    for storing in a database, keeping the sizes down
    """
    return str(to_unicode(dumps(JSON)))


def decode(JSON):
    rtn = loads(JSON)
    if type(rtn) == str: 
        rtn = str(rtn)
    return rtn
