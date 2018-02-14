from toolkit.json_tools import dumps
from toolkit.arrays import write_array
from toolkit.arrays import get_uni_array, get_int_array
from toolkit.file_tools import file_write
from lang_data.data_paths import data_path

from lang_data.iso_codes.LetterConv import letters_to_code

def write(path, DData, DKeys):
    LKeys = get_int_array()
    
    for in_key, LItem in DKeys.items():
        # First, create the array objects
        if LItem[1] == 'str':
            DItem = {'array': get_uni_array()}
            
            if len(LItem) == 4:
                DItem['key'], DItem['type'], DItem['len'], extra = LItem
                
                if isinstance(extra, dict):
                    DItem['DMap'] = extra
                else:
                    DItem['default'] = extra
            else:
                DItem['key'], DItem['type'], DItem['len'] = LItem
        
        elif LItem[1] == 'names':
            # An int array pointing to LCompressed indexes above
            out_key, typ, LNames = LItem
            DItem = {
                'key': out_key,
                 'type': typ,
                 'LNames': LNames,
                 'array': get_int_array()
            }
        else:
            raise Exception("unknown type %s" % LItem[1])
        
        DKeys[in_key] = DItem
    
    # Sort the key by the converted code for bisect
    LCodes = sorted(DData.keys(), key=lambda key: letters_to_code(key))
    
    for key in LCodes:
        # Second, append the values
        LIter = DData[key] if isinstance(DData[key], (list, tuple)) else [DData[key]]
        
        for DDataItem in LIter:
            # write the key
            LKeys.append(letters_to_code(key))
            
            for in_key, DItem in DKeys.items():
                if DItem['type'] == 'str':
                    value = DDataItem[in_key]
                    
                    if 'DMap' in DItem and value in DItem['DMap']: 
                        # If a value map is provided and 
                        # a map found, transform it
                        value = DItem['DMap'][value]

                    elif 'default' in DItem and not value: # CHECK ME! ====================================
                        # Default to the provided value if 
                        # value blank (and a default supplied)
                        assert not value, in_key
                        value = DItem['default']
                    
                    assert len(value) == DItem['len']
                    DItem['array'].extend(str(value))
                    
                elif DItem['type'] == 'names':
                    # Append the seek position of 
                    # this name in `LNames` to `array`
                    id = DItem['LNames'].append(DDataItem[in_key])
                    DItem['array'].append(id)
    
    # write the keys to disk
    with open(data_path('iso_codes', '%s.bin' % path), 'wb') as f:
        DOut = {}
        DOut['LKeys'] = {'LType': write_array(f, LKeys)}
        print path, len(LKeys), LKeys[30:50]
        
        # write the values to disk
        for in_key, DItem in DKeys.items():
            DItem['LType'] = write_array(f, DItem['array'])
            DOut[DItem['key']] = DItem
            
            # Delete various keys so that the JSON can be written
            for key in ('array', 'key', 'LNames'):
                if key in DItem:
                    del DItem[key]
    
    # write the JSON read info
    file_write(data_path('iso_codes', '%s.json' % path), dumps(DOut))
    