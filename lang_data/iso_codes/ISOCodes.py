from DMap import DMap

from toolkit.json_tools import load
from lang_data.data_paths import data_path

DCountries = load(data_path('iso_codes', 'CountryCodes.json'))

# The dict to uncompress the single letter DB into multiple
DNameCmp = {
    'A': 'LA',
    'B': 'DA',
    'C': 'LP',
    'E': 'DP'
}

DNameType = {
    'L': 'language name',
    'LA': 'alternate language name',
    'D': 'dialect name',
    'DA': 'alternate dialect name',
    'LP': 'discouraged language name',
    'DP': 'discouraged dialect name'
}

DScope = {
    'I': 'individual',
    'M': 'macrolanguage',
    'S': 'special'
}

DLangType = {
    'A': 'ancient',
    'C': 'constructed',
    'E': 'extinct',
    'H': 'historical',
    'L': 'living',
    'S': 'special'
}

DLangStatus = {
    'L': 'living',
    'N': 'nearly extinct',
    'X': 'extinct',
    'S': 'second language only'
}

class ISOCodes:
    """
    Combines the classes below into an easier-to-use interface 
    returning a combined dict, treating macrolanguages 
    like single languages as much as possible
    """
    
    def __init__(self):
        self.DAlternateNames = DMap('DAlternateNames')
        self.DISO639 = DMap('DISO639')
        self.DLangCodes = DMap('DLangCodes')
        self.DMacroLangs = DMap('DMacroLangs')
        self.DRevMacros = DMap('DRevMacros')
        self.DISO639_1 = DMap('DISO639_1')
        self.DISO639_2 = DMap('DISO639_2')
    
    def __iter__(self):
        for part3 in self.DMacroLangs: # FIXME! =====================================================
            yield part3
        
        for part3 in self.DISO639:
            yield part3
    
    def __contains__(self, part3):
        if len(part3) == 2:
            # Convert ISO 639-1 codes to ISO 639-3
            part3 = self.to_part3(part3)

        found = part3 in self.DISO639 or part3 in self.DMacroLangs or part3 in self.DLangCodes
        return found #and not not self.get_D_iso(part3)
    
    #===========================================================#
    #           ISO 639-1 and 639-2 (Compatibility)             #
    #===========================================================#
    
    def to_part3(self, part, default=KeyError):
        """
        Convert ISO 639-1 or 639-2 codes to 639-3
        """

        if part == 'mo':
            # HACK: It seems "mo" has been withdrawn for Moldovan
            part = 'ro'
        elif part == 'bh':
            part = 'bho'

        D = self.DISO639_1 if len(part)==2 else self.DISO639_2

        try:
            LRtn = D[part]
        except KeyError:
            LRtn = None
        
        if not LRtn and default==KeyError:
            raise KeyError(part)
        elif not LRtn:
            return default

        return LRtn[0]['part3']
    
    #===========================================================#
    #                   Combine Information                     #
    #===========================================================#
    
    def get_D_iso(self, part3, add_alternates=False, default=KeyError):
        """
        Returns a dict with the following keys:
        
        country: [2-letter country code, country name, continent] (OPTIONAL)
        country_guessed: True/False (True if guessed from macro languages)
        
        DAlt: See DAlternateNames for alternate language name 
              dict keys - a blank dict if not alternates
              
              NOTE: DAlt isn't added if add_alternates 
                    isn't `True` to save processing time
        
        LMacros/LRevMacros: [(ISO639 3 code, A[ctive]/R[etired]), ...]
        
        lang_status: See DLangStatus (OPTIONAL)
        language_type: See DLangType
        
        part1: ISO 639-1 two letter code (OPTIONAL)
        part2b: ISO 639-2 three letter code of the bibliographic 
                applications code set - OPTIONAL
        part2t: ISO 639-2 three letter code of the terminology 
                applications code set - OPTIONAL
        part3: ISO 639-3 three letter code
        
        short_name: Short name, e.g. "Mandarin Chinese" or "Catalan"
        long_name: Full "scientific" name, e.g. "Chinese, 
                   Mandarin" or "Catalan-Valencian-Balear"
        
        scope: See DScope
        """
        
        if len(part3) == 2:
            # Convert ISO 639-1 codes to ISO 639-3
            part3 = self.to_part3(part3)
        
        try:
            DISO = self.get_D_iso_639(part3)
        except KeyError:
            #raise
            DISO = None

        if not DISO and default==KeyError:
            raise KeyError(part3)
        elif not DISO:
            return default
        
        D = {}
        LMacros = D['LMacros'] = self.get_L_macros(part3)
        LRevMacros = D['LRevMacros'] = self.get_L_rev_macros(part3) # OPEN ISSUE: Change me? =============
        
        if LMacros:
            # A macrolanguage, e.g. zho (Chinese)
            # Try to fill me in with the most common values for country etc
            DLangCode = self.get_D_lang_codes(part3) or {}
            D.update(DISO)
            D.update(DLangCode)
            
            if add_alternates:
                D['DAlt'] = self.get_D_alternate_names(part3) or {}
            
            D['lang_status'] = 'living' # HACK!
            
            if not 'LCountry' in D:
                """
                HACK: Try to find the country by getting the most common 
                country in the children of this macrolanguage, if it isn't defined
                (in Malay it isn't, and Norwegian it is for some reason for example)
                """
                DCountry = {}
                for i_part3, status in self.get_L_macros(part3):
                    DLangCode = self.get_D_lang_codes(i_part3)
                    if not DLangCode: 
                        continue # WTF?
                    DCountry.setdefault(tuple(DLangCode['LCountry']), 0)
                    DCountry[tuple(DLangCode['LCountry'])] += 1
                
                L = [(DCountry[k], k) for k in DCountry]
                L.sort(reverse=True)
                
                if L: 
                    D['LCountry'] = list(L[0][1])
                    D['country_guessed'] = True
            
            D['name'] = D['ref_name'] # HACK!
        else:
            # A single language, e.g. cmn (Mandarin)
            if add_alternates:
                DAlt = self.get_D_alternate_names(part3) or {}
                #print DLangCode, DAlt, LRevMacros
                
                if not DAlt and LRevMacros: 
                    """
                    Some languages, e.g. norwegian nynorsk (nno) only have 
                    information in their parent (in this case Norwegian, nor)
                    """
                    DAlt = self.get_D_alternate_names(LRevMacros[0][0]) or {}

                D['DAlt'] = DAlt # Alternative names
            
            DLangCode = self.get_D_lang_codes(part3)
            if not DLangCode and LRevMacros: 
                DLangCode = self.get_D_lang_codes(LRevMacros[0][0]) or {}
                #print DLangCode
            
            D.update(DISO)
            if DLangCode: 
                D.update(DLangCode) # WARNING! ===================================================
        
        # Make the name/ref_name keys more clear what they do
        if D:
            D['short_name'] = D['ref_name'] if 'ref_name' in D else D['name']
            D['long_name'] = D['name'] if 'name' in D else D['ref_name']
            
            for key in ('name', 'ref_name'):
                if key in D: 
                    del D[key]
            
            D['part3'] = part3 # HACK
        return D
    
    #===========================================================#
    #                Alternative Language Names                 #
    #===========================================================#
    
    def get_D_alternate_names(self, part3):
        """
        Provides alternative language names for languages
        Returns {name_type: {LangName: [[CountryCode, country, Continent], ...], ...}, ...}
        
        lang_id[3L], 
        LCountry (country_id[2L] is replaced with [country code, region, country name]), 
        (and all the values in DNameType from name_type)
        """
        
        # DRtn -> {name_type: {name:  [...]}, ...}
        DRtn = {}
        
        for DAlt in self.DAlternateNames[part3]:
            # Uncompress single letter name 
            # types to two letters (if relevant)
            # and give the name type a more readable form
            name_type = DAlt['name_type']
            name_type = DNameCmp.get(name_type, name_type)
            name_type = DNameType.get(name_type, name_type)
            
            # Add the country
            DAlt['LCountry'] = [DAlt['country_id'], 
                                DCountries[DAlt['country_id']][0], 
                                DCountries[DAlt['country_id']][1]]
            del DAlt['country_id']
            
            LAlt = DRtn.setdefault(name_type, {}).setdefault(DAlt['name'], [])
            LAlt.append(DAlt['LCountry'])
            #del DAlt['name']
            #del DAlt['name_type']
        
        for k1 in DRtn:
            # Sort by country names
            for k2 in DRtn[k1]:
                DRtn[k1][k2].sort(key=lambda country: country[2].lower()) # CHECK ME! ==================
        return DRtn
    
    #===========================================================#
    #                      Basic Mappings                       #
    #===========================================================#
    
    def get_D_iso_639(self, part3):
        """
        Returns:
        
        id: [3L],
        part2b: [3L/0],
        part2t: [3L/0],
        part1: [2L/0],
        scope: [see DScope], 
        language_type: [see DLangType], 
        ref_name [the long form, primary language name e.g. "Chinese, Mandarin"], 
        comment [not used]
        """
        
        LItem = self.DISO639[part3]
        
        if LItem: 
            D = LItem[0]
        else: 
            return None
        
        # Convert the scope
        scope = D['scope']
        if scope in DScope: 
            D['scope'] = DScope[scope]
        
        # Convert the language type
        lang_type = D['language_type']
        if lang_type in DLangType:
            D['language_type'] = DLangType[lang_type]
        return D
    
    def get_D_lang_codes(self, part3):
        """
        lang_id[3L], 
        LCountry (country_id[2L] is replaced with [country code, region, country name]), 
        lang_status[1L], 
        name [the short form, primary language name e.g. "Mandarin Chinese"]
        """
        
        # NOTE: It seems that DISO639 is more complete for language status
        LItem = self.DLangCodes[part3]
        if LItem: 
            D = LItem[0]
        else: 
            return None
        
        # Convert the language status
        if D['lang_status'] in DLangStatus:
            D['lang_status'] = DLangStatus[D['lang_status']]
        
        # Convert the country code
        D['LCountry'] = [D['country_id'], 
                         DCountries[D['country_id']][0], 
                         DCountries[D['country_id']][1]]
        del D['country_id']
        return D
    
    #===========================================================#
    #                      Macrolanguages                       #
    #===========================================================#
    
    def get_L_macros(self, part3):
        """
        Get the macro languages of a parent language, 
        e.g. 'zho' finds 'cmn', 'yue' etc
        
        Returns [(ISO639 3 code, 
                  A[ctive]/R[etired] (all are "A" for now)), ...]
        """
        return [(D['i_id'], D['i_status']) for D in self.DMacroLangs[part3]]
    
    def get_L_rev_macros(self, part3):
        """
        Get the parent language of a macro language,
        e.g. 'cmn' finds 'zho'
        """
        return [(D['m_id'], D['i_status']) for D in self.DRevMacros[part3]]

ISOCodes = ISOCodes()

if __name__ == '__main__':
    for key in ISOCodes:
        print key, ISOCodes.get_D_iso(key, add_alternates=True)
        print

    from pprint import pformat
    for ISO in ['zho', 'cmn', 'cat', #'zz2',
                'nno', 'nor', 'msa', 'ltc']:
        print ISO, pformat(ISOCodes.get_D_iso(ISO))
        print
    