from toolkit.json_tools import load
from toolkit.arrays.ArrayUtils import read_array
from lang_data.data_paths import data_path

DCompressed = {}

class LCompressed:
    def __init__(self, key):
        self.key = key

        DJSON = load(data_path('iso_codes', key+'.json'))
        
        with open(data_path('iso_codes', key+'.bin'), 'r+b') as f:
            self.LSeek = read_array(f, DJSON['LSeek'])
            self.LAmount = read_array(f, DJSON['LAmount'])
            self.LData = read_array(f, DJSON['LData'])

    def __getitem__(self, name):
        seek = self.LSeek[name]
        amount = self.LAmount[name]
        return self.LData[seek:seek+amount]
