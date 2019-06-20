from json import dumps

from toolkit.json_tools import to_unicode
from .get_cldr_profiles import get_D_profile

if __name__ == '__main__':
    import os
    
    for path in os.listdir('src/main'):
        if '_' in path:
            print('OPENING:', path)
            profile = path.split('.')[0]
            D = get_D_profile(profile)
            out_path = 'output/%s.json' % profile
            f = open(out_path, 'wb')
            f.write(to_unicode(dumps(D, indent=2, encoding='utf-8')))
            f.close()
