from toolkit.json_tools import dumps
from toolkit.file_tools import file_write
from lang_data.data_paths import data_path
from toolkit.arrays import write_array
from toolkit.arrays import get_uni_array, get_int_array

class LCompressed:
    def __init__(self, key):
        """
        Compress together common names to save space in memory
        """
        self.id = -1
        self.D = {}
        self.key = key
    
    def write(self):
        LSeek = get_int_array()
        LAmount = get_int_array()
        LData = get_uni_array()
        
        x = 0
        while 1:
            if not x in self.D:
                break

            LSeek.append(len(LData))
            amount = LData.extend(self.D[x])
            LAmount.append(amount)

            x += 1
        
        D = {}
        with open(data_path('iso_codes', '%s.bin' % self.key), 'wb') as f:
            D['LSeek'] = write_array(f, LSeek)
            D['LAmount'] = write_array(f, LAmount)
            D['LData'] = write_array(f, LData)
        
        file_write(data_path('iso_codes', '%s.json' % self.key), dumps(D))
    
    def append(self, name):
        if name in self.D:
            return self.D[name]
        else:
            self.id += 1
            id = self.id
            self.D[id] = name
            return id
