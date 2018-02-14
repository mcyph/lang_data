from toolkit.file_tools import file_iter

def open_tsv(path, multi=False, encoding='utf-8'):
    """
    Open a tab-separated file, reading the first line for 
    a list of keys and using the first key as a primary lookup
    e.g. {FirstKey: {...}, ...}
    """
    xx = 0
    DRtn = {}
    for line in file_iter(path, encoding=encoding):
        line = line.strip('\r\n')
        LSplit = line.split('\t')
        
        if xx == 0:
            LKeys = LSplit
        else: 
            yy = 0
            DItem = {}
            for key in LKeys:
                DItem[key] = LSplit[yy]
                yy += 1
            
            key = DItem[LKeys[0]]
            if not multi:
                # A single primary key
                assert not key in DRtn, key
                DRtn[key] = DItem
            elif multi == -1:
                # Country codes HACK!
                if key in DRtn: 
                    continue
                DRtn[key] = DItem
            else: 
                # Can have multiple primary keys
                # (e.g. language index info)
                if not key in DRtn: 
                    DRtn[key] = []
                DRtn[key].append(DItem)
            del DItem[LKeys[0]]
        xx += 1
    return DRtn
