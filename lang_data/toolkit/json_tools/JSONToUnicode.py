# A HACK module to convert \u codes into Unicode by using eval()!


def to_unicode(s, dec_hex=0):
    # TODO: What about CONTROL CODES?
    t_s = s.replace('"""', '') # FIXME!
    try: 
        if dec_hex: 
            return eval('"""%s"""' % t_s.replace('"', '\\"'))
        else: 
            return eval(('r""" %s """' % t_s).strip())
    except UnicodeDecodeError: 
        print('WIDE WARNING in JSONToUnicode!')
        return s # HACK!
