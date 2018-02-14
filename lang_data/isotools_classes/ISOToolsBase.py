from re import compile
from collections import namedtuple
from lang_data.data_paths import data_path
from toolkit.json_tools import load

from toolkit.rem_dupes import rem_dupes as _rem_dupes
from lang_data.iso_codes import ISOCodes, DCountries

from ISOEscape import ISOEscape
from ISOGuesser import ISOGuesser
from LikelySubtags import LikelySubtags
from SupplementalData import SupplementalData

DRevCountries = {v[0].lower():k for k, v in DCountries.items()}

RE_ISO = compile(
    r'^([a-z]{2,3})?'
    r'(?:(?:_|^)([A-Z][a-z]{3}))?'
    r'(?:(?:-|^)([A-Z]{2}|[0-9]{3}))?'
    r'(?:(?:\|)(.*))?$'
)

SPLIT_CHECKING = True

ISOCode = namedtuple('ISOCode', [
    'lang', 'script', 'territory', 'variant'
])


class ISOToolsBase(ISOEscape, ISOGuesser, LikelySubtags, SupplementalData):
    def __init__(self):
        """
        See ../iso_tools/ISOCodes.py for more detailed information about individual ISO codes

        This is mainly for converting/providing ISO codes/scripts/variants to be a standard
        format throughout LanguageLynx
        """
        D = load(data_path('cldr', 'script_mappings.json'))
        self.DName2Script = D['DName2Script']
        self.DScript2Name = D['DScript2Name']
        self.STerritories = set(D['LTerritories'])

    #=========================================================================#
    #                           Split/Join FUnctions                          #
    #=========================================================================#

    def verify_iso(self, s):
        # This is a stub for now forwarding to `split`, but if SPLIT_CHECKING is
        # ever turned off for performance later I might modify this.
        assert SPLIT_CHECKING
        self.split(s)

    SOKISOs = set()

    def split(self, s):
        m = RE_ISO.match(s)
        assert m, "invalid ISO code format: %s" % s
        lang, script, territory, variant = m.group(1, 2, 3, 4)

        if SPLIT_CHECKING:
            if lang and not lang in self.SOKISOs:
                assert lang in ISOCodes, \
                    "lang code %s not valid!" % lang

                # Shorten if possible to a two-letter code
                if lang and len(lang) == 3:
                    DISO = ISOCodes.get_D_iso(lang)
                    assert not 'part1' in DISO, \
                        "lang code %s should be shortened to %s!" % (lang, DISO['part1'])

                # This ISO checking is very slow, so
                # remember this ISO as OK for next time
                self.SOKISOs.add(lang)

            if script:
                assert script in self.DScript2Name, \
                    "script %s not valid!" % script

            if territory:
                assert territory in self.STerritories, \
                    "territory code %s not valid!" % territory

        return ISOCode(lang, script, territory, variant)

    DPart2Cache = {}
    DPart3Cache = {}

    def join(self, part3=None,
                   script=None,
                   territory=None,
                   variant=None,
                   part2=None):

        _lang = _script = _territory = _variant = None

        # Process ISO
        if part3 and part3 in self.DPart3Cache:
            _lang = self.DPart3Cache[part3]

        elif part2 and part2 in self.DPart2Cache:
            _lang = self.DPart2Cache[part2]

        else:
            if part3:
                _lang = part3
                assert _lang in ISOCodes, \
                    "language code %s not valid!" % _lang
            elif part2:
                _lang = ISOCodes.to_part3(part2)

            # "undefined" iso codes will be omitted
            _lang = None if _lang == 'und' else _lang

            # Shorten if possible to a two-letter code
            if _lang and len(_lang) == 3:
                DISO = ISOCodes.get_D_iso(_lang)
                if DISO and 'part1' in DISO:
                    _lang = DISO['part1']

            # Cache the result for later
            DSet = self.DPart3Cache if part3 else self.DPart2Cache
            DSet[part3 if part3 else part2] = _lang


        # Process script, converting from the
        # English script name if necessary
        if script:
            if not len(script) == 4 or not script.istitle():
                assert script.lower() in self.DName2Script,\
                    "script name %s not valid!" % script

                script = self.DName2Script[script.lower()]
            else:
                assert script in self.DScript2Name, \
                    "script %s not valid!" % script

            _script = script


        # Process Country
        if territory:
            if (
                (
                    not len(territory)==2 or
                    not territory.isupper()
                )
                and not territory.isdigit()
            ):
                # Convert to a territory code from
                # the English script name if necessary
                assert territory.lower() in DRevCountries,\
                    "territory name %s was not found!" % territory

                _territory = DRevCountries[territory.lower()]
            else:
                # Otherwise just verify the territory code is valid
                assert territory in self.STerritories, \
                    "territory code %s not valid!" % territory

                _territory = territory


        # Process Variant
        # (currently no checking, but it may pay
        #  to check if a localization is available etc)
        if variant:
            _variant = variant


        return  '%s%s%s%s' % (
            _lang if _lang else '',
            ('_' if _lang else '') + _script if _script else '',
            ('-' if _script or _lang else '') + _territory if _territory else '',
            '|'+_variant if _variant else ''
        )

    #=========================================================================#
    #                              Locale to ISO                              #
    #=========================================================================#

    def locale_to_iso(self, locale, initial_key='part3', allow_variants=False):
        LKeys = [initial_key]
        LLocale = locale.replace('_', '-').split('-')
        LLocale[0] = LLocale[0].lower()

        for x, s in enumerate(LLocale[1:]):
            if len(s) == 2 or s.isdigit():
                LLocale[x+1] = s.upper()
                LKeys.append('territory')
            elif len(s) == 4:
                LLocale[x+1] = s.title()
                LKeys.append('script')
            else:
                if allow_variants:
                    LKeys.append('variant') # CHECK ME! ==================================================================
                else:
                    raise Exception('invalid locale: %s' % locale)

        return self.join(
            **dict(zip(LKeys, LLocale))
        )

    #=========================================================================#
    #                           Remove Specific Info                          #
    #=========================================================================#

    def get_L_removed(self, s, L, rem_dupes=False):
        LRtn = []
        for bitflag in L:
            LRtn.append(self.removed(s, bitflag))

        return _rem_dupes(LRtn) if rem_dupes else LRtn

    def removed(self, s, bitflag):
        LSplit = list(self.split(s))

        for x, bit in enumerate((1, 2, 4, 8)):
            #print bit, bitflag, bitflag& bit

            if bitflag& bit:
                LSplit[x] = None

        return self.join(*LSplit)

    #=========================================================================#
    #                            Join Multiple                                #
    #=========================================================================#

    def join_multiple(self, L):
        [self.verify_iso(i) for i in L]
        assert not '_-_' in ' '.join(L)
        return '_-_'.join(L)

    def split_multiple(self, s):
        L = s.split('_-_')
        assert len(L) > 1
        [self.verify_iso(i) for i in L]
        return L


if __name__ == '__main__':
    s = 'en_Latn-AU|aaa+++'
    print ISOToolsBase().url_escape(s)
    print ISOToolsBase().url_join(s, s)
