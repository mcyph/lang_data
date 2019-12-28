#===========================================================#
#                         Get Keys                          #
#===========================================================#


def get_D_keys(D):
    return _recurse(D)


def _recurse(o, D=None, LKeys=None):
    D = {} if D is None else D
    LKeys = () if LKeys is None else LKeys

    if isinstance(o, dict):
        for k, v in list(o.items()):
            D.setdefault(LKeys+(k,), []).append(v)
            _recurse(v, D, LKeys+(k,))

    elif isinstance(o, (list, tuple)) and True:
        for k, v in enumerate(o):
            D.setdefault(LKeys+(k,), []).append(v)
            _recurse(v, D, LKeys+(k,))

    return D
