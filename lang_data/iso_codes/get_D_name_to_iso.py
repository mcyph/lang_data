from ISOCodes import ISOCodes

def get_D_name_to_iso():
    D = {}

    for part3 in ISOCodes:
        DISO = ISOCodes.get_D_iso(part3, add_alternates=True)

        if 'part1' in DISO:
            part3 = DISO['part1'] # HACK: shorten the code!!!


        D[DISO['short_name'].lower()] = part3
        D[DISO['long_name'].lower()] = part3

        DAlt = DISO['DAlt']
        if 'language name' in DAlt:
            DLangNames = DAlt['language name']
            for k, v in DLangNames.items():
                D[k.lower()] = part3

                if 'alternate language name' in v:
                    DAltNames = v['alternate language name']
                    for k2 in DAltNames:
                        D[k2.lower()] = part3

    for k in list(D.keys()):
        # HACK: Always use the generic "zh"
        # Chinese code for Mandarin Chinese!
        if D[k] == 'cmn':
            D[k] = 'zh'

        # HACK: Fix e.g. "chinese, hakka" -> "hakka"
        if ', ' in k:
            _, _, lang = k.partition(', ')
            if not lang in D:
                D[lang] = D[k]


    D['cantonese'] ='yue'
    D['mandarin'] = 'zh' # HACK!
    D['translingual'] = 'mul'
    return D



if __name__ == '__main__':
    from pprint import pprint
    pprint(get_D_name_to_iso())

