from copy import deepcopy, copy

SIgnore = set([str, str, int, None])


def copy_(obj):
    if type(obj) in (list, tuple): 
        is_tuple = type(obj) == tuple
        rtn = []
        for i in obj:
            rtn.append(copy_(i))
        
        if is_tuple: 
            obj = tuple(rtn)
        else: 
            obj = rtn
    
    elif type(obj) == dict: 
        rtn = {}
        for k in obj:
            rtn[k] = copy_(obj[k])
        obj = rtn
    
    elif type(obj) in SIgnore: 
        # Numeric or string/unicode? 
        # It's immutable, so ignore it!
        pass 
    
    else: 
        obj = deepcopy(obj)
    return obj
