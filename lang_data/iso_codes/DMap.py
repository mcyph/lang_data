import bisect

from toolkit.json_tools import load
from toolkit.arrays import read_array
from lang_data.data_paths import data_path

from LetterConv import letters_to_code, code_to_letters
from LCompressed import LCompressed, DCompressed

class DMap:
    def __init__(self, key_name):
        DArrays = self.DArrays = {}
        DInf = self.DInf = \
            load(data_path('iso_codes', key_name+'.json'))

        # Load the databases
        with open(data_path('iso_codes', key_name+'.bin'), 'r+b') as f:
            for key in DInf:
                DArrays[key] = read_array(f, DInf[key]['LType'])
        
        self.LKeys = DArrays['LKeys']
        #self.SKeys = set(code_to_letters(i) for i in self.LKeys)
        del DInf['LKeys']
        
    def __iter__(self):
        #print self.LKeys
        for key in self.LKeys:
            yield code_to_letters(key)
        
    def __contains__(self, name):
        #return name in self.SKeys

        name = letters_to_code(name)
        pos = bisect.bisect_left(self.LKeys, name)
        if pos > len(self.LKeys)-1:
            return False
        return self.LKeys[pos] == name
        
    def __getitem__(self, name):
        name = letters_to_code(name)
        
        # TODO: Sort the values properly!
        pos = bisect.bisect_left(self.LKeys, name)
        #pos = 0
        #for i in self.LKeys:
        #    if i == name: break
        #    pos += 1
        
        LRtn = []
        while 1:
            if pos > len(self.LKeys)-1:
                break
            elif self.LKeys[pos] != name:
                break
            
            D = {}
            for k in self.DInf:
                typ = self.DInf[k]['type']
                
                if typ == 'str':
                    # Link to a string index with a fixed number of bytes
                    LArray = self.DArrays[k]
                    len_ = self.DInf[k]['len']
                    default = self.DInf[k].get('default', None)
                    
                    xxx = pos * len_
                    value = LArray[xxx:xxx+len_]

                    #print 'STR:', k, xxx, len_, value
                    
                    if default != value: 
                        D[k] = value
                    
                elif typ == 'names':
                    # Link to a compressed "names" index above


                    key = 'LLangNames' #self.DInf[k]['key']
                    if not key in DCompressed:
                        DCompressed[key] = LCompressed(key)
                    
                    name_id = self.DArrays[k][pos]
                    D[k] = DCompressed[key][name_id]

                    #print 'NAMES:', k, name_id, D[k]

                else: 
                    raise Exception
            
            LRtn.append(D)
            pos += 1
        return LRtn
