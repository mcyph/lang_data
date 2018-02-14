import os

from lang_data.langdata_classes.Languages import DLangs
from char_data.data.Langs.ISOCodes import ISOCodes
 
def get_L_lang_names():
    # DRtn -> {letter: [DLang, ...], ...}
    DRtn = {}
    for iso in DLangs:
        default, DVariants = DLangs[iso]
        LangName = DVariants[default]['name'] # HACK!
        letter = LangName[0].upper()
        if not letter in DRtn:
            DRtn[letter] = []
        DRtn[letter].append(DVariants[default])
    
    LRtn = []
    for letter in sorted(DRtn.keys(), key=lambda x: x.lower()):
        LLang = []
        for DLang in DRtn[letter]:
            iso = DLang['iso']
            DISO = ISOCodes.get_D_iso(iso, add_alternates=True) or {}
            
            # Add Primary name
            name = DLang['name']
            
            # Profile Names
            if 'LProfiles' in DLang:
                LProfiles = DLang['LProfiles']
            else: 
                LProfiles = [DLang['Profile']] # HACK!
            
            # Add The iso code
            iso = DLang['iso']  # The iso 639 code (for events)
            
            # Add flag (may not exist?)
            if DISO and os.path.exists('Web/Images/flags/png/%s.png'
                                       % DISO['LCountry'][0].lower()):
                flag = DISO['LCountry'][0].lower()
            else: 
                flag = None
            
            # Add alternate Names (for filtering)
            LAlt = []
            DIndex = DISO.get('DAlt')
            
            if DIndex:
                if 'language name' in DIndex:
                    LAlt.extend(list(DIndex['language name'].keys()))
                
                if 'alternate language name' in DIndex:
                    LAlt.extend(list(DIndex['alternate language name'].keys()))
            
            LLang.append([flag, name, iso, LAlt, LProfiles])
        LRtn.append([letter, LLang])
    return LRtn
LLangNames = get_L_lang_names()
