def process_keys(D, fn):
    return dict([(fn(k), v) for k, v in list(D.items())])


def reverse_keys_values(D):
    return dict((v,k) for k, v in D.items())
