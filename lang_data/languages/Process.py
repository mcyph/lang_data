from Accents import get_D_accents as conv_D_accents

from toolkit.DIPA import DIPA
#from Chars.Ranges.Accents import get_D_accents
from char_data.data.Fonts.GetSFontClasses import get_S_font_classes
from keyboards.GetLayouts import get_S_layouts
from multi_translit.translit.TranslitLoad import DSingleISOToISO, DStrToISO
SFontClasses = get_S_font_classes()
SKbdLayouts = get_S_layouts()

# Define the rtl scripts
# REMEMBER TO KEEP ME UPDATED!
SRTL = set(['Hebrew', 
            'NKo',  # CHECK ME!
            'Cypriot', 
            'Phoenician', 
            'Lydian', 
            'Kharoshthi', 
            'Arabic', 
            'Syriac', 
            'Thaana'])

# TODO: Implement ipa in the font data!
SFontClasses.add('IPA')# HACK HACK HACK! <-----
SFontClasses.add('Chinese (Unified)')# HACK!

class LangProcess:
    def __init__(self, DLang, iso, profile, name, default, DVariants):
        self.DLang = DLang
        self.iso = iso
        self.profile = profile
        self.name = name
        self.default = default
        self.DVariants = DVariants
        
        #self.check_name_eq(DLang, name)
        self.validate_fonts(DLang, iso)
        #self.special(DLang) # FIXME! =====================================================
        self.variants(DLang, iso, profile)
        self.index(DLang, iso)
        self.alphabets(DLang)
        self.inputs(DLang, iso)
    
    #===========================================================#
    #                  Add language alphabet                    #
    #===========================================================#
    
    def alphabets(self, DLang):
        # Check LAlpha
        LAllAlpha = self.LAllAlpha = []
        LAlpha = []
        
        if not 'LAlpha' in DLang:
            DLang['LAlpha'] = []
        
        for header, LChars in DLang['LAlpha']:
            # TODO: Should LAllAlpha be sorted 
            # into common/uncommon characters?
            LAllAlpha.extend(LChars)
            
            if LChars:
                # HACK: Ignore blank headers!
                LAlpha.append([header, LChars])
            
            #assert LChars, "header %s doesn't have any chars in iso %s" % (header, iso)
        DLang['LAlpha'] = LAlpha
    
    #===========================================================#
    #                     Language inputs                       #
    #===========================================================#
    
    def inputs(self, DLang, iso):
        # Check/output LInputs
        assert 'LInputs' in DLang, "iso %s doesn't have LInputs" % iso
        assert DLang['LInputs'], "iso %s doesn't have inputs" % iso
        
        n_LInputs = [{'type': 'direct'}]
        for typ in DLang['LInputs']:
            if typ == 'direct': 
                continue # Direct input (no processing)
            else: 
                fn = getattr(self, typ)
                fn(DLang, n_LInputs)
        DLang['LInputs'] = n_LInputs
        
        # Clean up various values
        if 'DChinese' in DLang: 
            del DLang['DChinese']
        
        if 'LKeyLayouts' in DLang: 
            del DLang['LKeyLayouts']
        
        # Set the default input index
        direct_default = 'direct' in DLang['LInputs']
        DLang['input_default'] = 0 if direct_default else 1
    
    #===========================================================#
    #                     Onscreen Keyboard                     #
    #===========================================================#
    
    def keyboard(self, DLang, LInputs):
        for key_layout, LAccents in DLang['LKeyLayouts']:
            # TODO: Should TYPE CHECKING be enforced for LAccents?
            assert key_layout in SKbdLayouts, "layout %s not found for iso %s" % (key_layout, self.iso)
            
            LInputs.append({'type': 'keyboard', 
                            'layout': key_layout, 
                            'LAccents': LAccents})
    
    #===========================================================#
    #               Chinese Pinyin/Jyutping etc                 #
    #===========================================================#
    
    def chinese(self, DLang, LInputs):
        'Chinese IME (Derived from keyboards for Cangjie/Bopomofo)'
        DChinese = DLang['DChinese']
        typ = DChinese['Type']
        
        for i_type in DChinese['LOrder']:
            LPossible = ['PinYin', 
                         'Jyutping', 
                         'Bopomofo', 
                         'Cangjie', 
                         'FourCorners']
            
            assert i_type in LPossible, "iso %s has invalid chinese type %s" % (self.iso, i_type)
            
            LInputs.append({'type': 'chinese', 
                            'profile': typ, 
                            'sub_type': i_type})
    
    #===========================================================#
    #                       Japanese IME                        #
    #===========================================================#
    
    def japanese(self, DLang, LInputs):
        '''
        In the main SELECT:
           Romaji
           Natural layouts
        
        In a custom SELECT:
           Hiragana IME mode            (-> IME Hiragana)
           Katakana/Half-Width Katakana (-> Katakana keyboard)
           Hiragana/Half-Width Hiragana (-> Hiragana keyboard)
           Names                        (-> IME Hiragana)
           Place Names                  (-> IME Hiragana)
           Fullwidth ASCII              (-> Fullwidth keyboard)
        '''
        
        # japanese "Romaji" with candidates mode toggleable
        LInputs.append({'type': 'japanese', 
                        'mode': 'Romaji'})
        
        # japanese "Natural" layout 
        LInputs.append({'type': 'japanese', 
                        'mode': 'Natural'})
    
    #===========================================================#
    #                      Korean Hangul                        #
    #===========================================================#
    
    def korean(self, DLang, LInputs):
        'korean Hangul joiner-based input'
        LInputs.append({'type': 'korean'})
    
    #===========================================================#
    #                         Accents                           #
    #===========================================================#
    
    def accents(self, DLang, LInputs):
        '''
        # Accent inputs
        # See also accents.py for info on the format of DAccents
        '''
        import warnings
        warnings.warn('FIX LangProcess ACCENTS!')
        
        if 'DAccents' in DLang: 
            DAccents = DLang['DAccents']
        else: 
            DAccents = {} # get_D_accents(self.LAllAlpha) WARNING! =================================
        
        DAccents = conv_D_accents(DAccents) # CHECK ME!
        LInputs.append({'type': 'accents', 
                        'DAccents': DAccents})
    
    #===========================================================#
    #                          IPA                              #
    #===========================================================#
    
    def ipa(self, DLang, LInputs):
        'Redirect to accents with the IPAData mappings'
        DAccents = conv_D_accents(DIPA)
        LInputs.append({'type': 'accents', 'DAccents': DAccents})
    IPA = ipa # HACK! ================================================================================
    
    #===========================================================#
    #                     Vietnamese IME                        #
    #===========================================================#
    
    def vietnamese(self, DLang, LInputs):
        'Create one for each vietnamese input method type'
        LInputs.extend(({'type': 'vietnamese', 'method': 'Auto'},
                        {'type': 'vietnamese', 'method': 'Telex'},
                        {'type': 'vietnamese', 'method': 'VNI'},
                        {'type': 'vietnamese', 'method': 'VIQR'},
                        {'type': 'vietnamese', 'method': 'VIQR*'}))
