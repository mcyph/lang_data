# TODO: Update me for the new language data!

import sys, os
os.chdir('../../')
import dtaLanguages
from input.VirtualKeyboard import DKeys
LLangs = dtaLanguages.GetPossibleLanguages()

LRtn = []
for DLang in LLangs:
    #print DLang['EngLangName'].encode('utf-8'), DLang['Alphabet']
    if 'Alphabet' in DLang and DLang['Alphabet']:
        L = []
        for KeyLayout in DKeys:
            LFound = []
            LNotFound = []
            iDKeys = {}
            
            try: 
                Keys = DKeys[KeyLayout]
            except: 
                continue # HACK!
            
            for DRow in Keys['Layout']:
                for k in DRow:
                    for xx in DRow[k]:
                        iDKeys[xx] = None
            
            for Key in DLang['Alphabet']:
                # Figure out which keys are or aren't in the 
                # keyboard and which are in the alphabet
                # TODO: Should the keys be 'broken up' here?
                if Key in iDKeys:
                    LFound.append(Key)
                else: 
                    LNotFound.append(Key)
            
            LAlphaNotFound = []
            LAlphaFound = []
            for Key in iDKeys:
                # TODO: Should the keys be 'broken up' here?
                if Key in DLang['Alphabet']:
                    LAlphaFound.append(Key)
                else: 
                    LAlphaNotFound.append(Key)
            
            # Add a sort key to find the least not found 
            # keys in every language alphabet
            L.append(((len(LNotFound), len(LAlphaNotFound), 
                       -len(LFound) -len(LAlphaFound)), 
                      KeyLayout, LNotFound, LFound))
        L.sort()
        LRtn.append((DLang['EngLangName'], L))
LRtn.sort()

print
for EngLangName, L in LRtn:
    print (EngLangName.strip()+' (').encode('utf-8'),
    iL = [(i[1], ' '.join(i[2])) for i in L[:6]]
    for i1, i2 in iL:
        i2 = [xx.strip() for xx in i2] # HACK!
        
        if len(i2) > 25: 
            i2 = '%s...' % ' '.join(i2[:30])
        else: 
            i2 = ' '.join(i2)
        
        i2 += ';'
        print i1.encode('utf-8'), i2.encode('utf-8'),
    print ')'
sys.exit()
