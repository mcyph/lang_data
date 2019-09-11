from iso_tools.iso_codes import ISOCodes
from .get import get

LANG_DEFAULT = ''                  # 'Azerbaijani'
LANG_SHORT = 'short'               # 'Azeri'
LANG_SHORT_FIRST = ('short', '')

SCRIPT_DEFAULT = ''                # 'Arabic'
SCRIPT_VARIANT = 'variant'         # 'Perso-Arabic'
SCRIPT_SECONDARY = 'secondary'
SCRIPT_STAND_ALONE = 'stand-alone'


class Languages:
    def __init__(self):
        DLangs = self.D['DLangs']

        # Provide a case-insensitive map from the native language
        # name in a given language and the ISO 639 code
        self.DLangsByName = DLangsByName = {}

        for iso_code, DLang in DLangs.items():
            for lang_name in DLang.values():
                lcase_lang_name = lang_name.lower()

                if lcase_lang_name in DLangsByName:
                    assert DLangsByName[lcase_lang_name] == iso_code, \
                        f"Conflicting language name -> ISO code mapping: " \
                            f"{lcase_lang_name} -> {iso_code} and {DLangsByName[lcase_lang_name]}"

                DLangsByName[lcase_lang_name] = iso_code

    #=====================================================#
    #              Language and Script Names              #
    #=====================================================#

    def get_lang_name(self, part3, typ=LANG_DEFAULT, default=KeyError):
        """
        Finds the localized name for ISO 639-3 code `part3`,
        converting first to ISO 639-1 if necessary

        NOTE: See also ISOPrettifier for ISO string
        aware (e.g. "en_Latn-AU")-style pretty formatting!

        TODO: Add support for profiles/scripts/variants, e.g. "zh_CN"!
        TODO: Make sure CLDR doesn't used ISO 639-2! =========================
        """
        DLangs = self.D['DLangs']
        if part3 in DLangs:
            return get(DLangs, default, [part3, typ])

        # Get the ISO-639-1 two-letter code
        try:
            DISO = ISOCodes.get_D_iso(part3, add_alternates=False)

        except KeyError:
            if default == KeyError:
                raise
            return default

        if 'part1' in DISO:
            part1 = DISO['part1']
        else:
            part1 = part3 # WARNING! ===========================================
        return get(DLangs, default, [part1, typ])

    def get_D_lang_names_to_iso(self, make_case_insensitive=False):
        DRtn = {}
        DLangs = self.D['DLangs']

        for part3, DLang in DLangs.items():
            for typ, loc_lang_name in DLang.items():
                try:
                    DISO = ISOCodes.get_D_iso(part3, add_alternates=False)
                except KeyError:
                    DISO = {}

                # Try to convert to two-char codes
                if 'part1' in DISO:
                    part1 = DISO['part1']
                else:
                    part1 = part3

                if make_case_insensitive:
                    loc_lang_name = loc_lang_name.lower()
                DRtn[loc_lang_name] = part1

        return DRtn

    def get_iso_from_lang_name(self, lang_name, default=KeyError):
        """
        Find the ISO 639-3 code from the localized name
        """
        try:
            return self.DLangsByName[lang_name]
        except KeyError:
            if default == KeyError:
                raise
            return default

    def get_script_name(self, script, typ=SCRIPT_DEFAULT, default=KeyError):
        """
        Search in DScripts for `s`
        """
        return get(self.D, default, ['DScripts', script, typ])

    def get_variant_name(self, variant, default=KeyError):
        """
        Searches in DVariants then DTransformNames for `variant`
        """
        if variant in self.D['DVariants']:
            return get(self.D, default, ['DVariants', variant, ''])
        else:
            return get(self.D, default, ['DTransformNames', variant])

    def get_lang_script_name(self, part3, script,
                             lang_type=LANG_DEFAULT,
                             script_type=SCRIPT_DEFAULT):
        """
        Gets a displayable "language (script)"

        TODO: Make this region/variant aware! =================================================
        """

        lang = self.get_lang_name(part3, lang_type)
        script = self.get_script_name(script, script_type)
        return self.locale_pattern(lang, script)

    def get_L_part3(self):
        LRtn = []
        for iso in self.D['DLangs']:

            if len(iso) == 2:
                if iso == 'bh':
                    continue # Bihari not in 639-3 HACK! =====================================
                iso = ISOCodes.to_part3(iso)

            LRtn.append(iso)
        return sorted(LRtn)

    def get_L_scripts(self):
        return sorted(self.D['DScripts'])
