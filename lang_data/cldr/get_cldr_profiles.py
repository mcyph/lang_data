from os import listdir

from lang_data.toolkit.copying.fast_copy import copy_
from lang_data.data_paths import data_path
from lang_data.toolkit.dict_operations.get_D_keys import get_D_keys
from iso_tools import SCRIPT, TERRITORY, VARIANT, NONE

from .get_D_cldr import get_D_cldr


DRoot = get_D_cldr('root.xml')

class CLDRProfiles:
    def __init__(self):
        self.DProfiles, self.DISOToProfiles = self.get_D_profiles()

    def _ensure_isotools(self):
        try:
            global ISOTools
            ISOTools
        except:
            from iso_tools import ISOTools

    #===========================================================#
    #                   ISO 639-3 Integration                   #
    #===========================================================#

    def get_closest_profile(self, iso, default=KeyError):
        """
        Find the closest profile available,
        e.g. "ja-Japn_JP" doesn't exist, so this can fallback to "ja_JP"
        """
        self._ensure_isotools()

        for i_iso in ISOTools.get_L_removed(
            iso,
            [
                NONE, TERRITORY, VARIANT, SCRIPT,
                VARIANT|TERRITORY, SCRIPT|TERRITORY, SCRIPT|VARIANT,
                SCRIPT|TERRITORY|VARIANT
            ],
            rem_dupes=True
        ):
            if i_iso in self.DISOToProfiles:
                return i_iso


        if default == KeyError:
            raise KeyError(iso)
        return default

    def get_D_profile_by_iso(self, iso, allow_fallbacks=True):
        """
        Get the CLDR profile dict by ISO 639-3 code
        and two-letter country code (optional)
        """
        if iso in self.DISOToProfiles:
            i_profile = self.DISOToProfiles[iso]
        elif allow_fallbacks:
            iso = self.get_closest_profile(iso)
            i_profile = self.DISOToProfiles[iso]
        else:
            raise KeyError(iso)

        return self.get_D_profile(i_profile)

    def get_D_profiles(self):
        """
        Get a map of possible CLDR language profiles
        """
        self._ensure_isotools()

        DRtn = {}
        DISOToProfiles = {}

        for fnam in listdir(data_path('cldr', 'main')):
            if fnam.split('.')[-1]!='xml' or fnam=='base.xml':
                continue
            fnam = fnam.replace('.xml', '')

            if fnam in ('in', 'iw', 'mo', 'root'):
                # HACK!
                continue


            script = None
            territory = None
            variant = None

            if '_' in fnam:
                iso = fnam.split('_')[0]
                L = fnam.split('_')[1:]
                for i in L:
                    if i.isupper() and len(i) == 2:
                        # A two-letter territory, e.g. AU
                        territory = i

                    elif i.istitle() and len(i) == 4:
                        # A four-letter script name, e.g. Latn
                        script = i

                    else:
                        # A variant, e.g. "POLYTON" for polytonic Greek
                        variant = i
            else:
                iso = fnam


            # Convert to the standard LanguageLynx ISO string format
            iso_string = ISOTools.join(
                part3=iso, script=script,
                territory=territory, variant=variant
            )
            assert not iso_string in DISOToProfiles
            DISOToProfiles[iso_string] = fnam

            DRtn.setdefault(iso, []).append((
                script, territory, variant
            ))

        # Chinese is referenced like e.g. "zh_Hans_CN",
        # but "zh_CN" is a common way of referencing
        # the same thing, so alias them
        for alias, fnam in (
            ('zh-CN', 'zh_Hans_CN'),
            ('zh-SG', 'zh_Hans_SG'),

            # Macau/Hong Kong also have simplified profiles,
            # but I assume they're traditional here
            ('zh-HK', 'zh_Hant_HK'),
            ('zh-MO', 'zh_Hant_MO'), # Macau
            ('zh-TW', 'zh_Hant_TW')
        ):
            DISOToProfiles[alias] = fnam

        return DRtn, DISOToProfiles

    #===========================================================#
    #                 Open and Combine Profiles                 #
    #===========================================================#

    def get_D_profile(self, fnam):
        # Start with `root.xml`
        fnam = fnam.replace('.xml', '')
        DRtn = copy_(DRoot)

        # Add the language-specific base (e.g. `en.xml`)
        iso = fnam.split('_')[0]
        DRtn = self.combine(DRtn, get_D_cldr('%s.xml' % iso))

        # Add the script "base" if one exists,
        # e.g. "aze_Cyrl_AZ"'s base is "aze_Cyrl"
        if fnam.count('_') == 2:
            _, country, _ = fnam.split('_')
            DRtn = self.combine(DRtn, get_D_cldr('%s_%s.xml' % (iso, country)))

        # Add the language (e.g. `en_AU.xml`)
        if '_' in fnam:
            DRtn = self.combine(DRtn, get_D_cldr('%s.xml' % fnam))

        return DRtn

    def combine(self, x, y):
        same_type = type(x) == type(y)
        both_strings = isinstance(x, str) and isinstance(y, str)
        one_none = x is None or y is None

        assert same_type or both_strings or one_none, \
            'incompatible types: %s %s' % (type(x), type(y))

        if isinstance(y, dict):
            for key in y:
                if key in x:
                    x[key] = self.combine(x[key], y[key])
                else:
                    x[key] = y[key]
            return x
        else:
            return y


CLDRProfiles = CLDRProfiles()


#===========================================================#
#                          Tests                            #
#===========================================================#

if __name__ == '__main__':
    from pprint import pprint
    
    pprint(CLDRProfiles.DProfiles)
    pprint(CLDRProfiles.get_D_profile_by_iso('en_AU-Jpan'))
    
    D = {}
    for fnam in listdir(data_path('cldr', 'main')):
        if '_' in fnam:
            profile = fnam.split('.')[0]
            print(profile)
            #get_D_profile(profile)
            
            for key, value in list(get_D_keys(get_D_profile(profile)).items()):
                D.setdefault(key, []).append(value)
    
    with open('keys.txt', 'w', encoding='utf-8') as f:
        for key, value in sorted(D.items()):
            frm = '%s: %s\n' % ('->'.join(key), 
                                repr(value).decode('raw_unicode_escape', 'ignore')[:150])
            f.write(frm)
