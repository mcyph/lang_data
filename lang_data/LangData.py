# -*- coding: utf-8 -*-
from langdata_classes import Miscellaneous, Timezones, \
    Territories, Currencies, Alphabets, ISOPrettifier, Languages


def _ensure_cldr():
    try:
        CLDRProfiles
    except:
        global CLDRProfiles
        from cldr import CLDRProfiles


_DCache = {}


def LangData(iso, allow_fallback=False):
    _ensure_cldr()
    if allow_fallback:
        iso = CLDRProfiles.get_closest_profile(iso)

    if not iso in _DCache:
        _DCache[iso] = _LangData(iso)
    return _DCache[iso]


class _LangData(Alphabets, Currencies, ISOPrettifier, Languages,
                Miscellaneous, Territories, Timezones):

    def __init__(self, iso):
        """
        A class that reads the Unicode CLDR database, allowing for:

        * Alphabet: Getting the alphabet of each language
          (i.e. the characters used by the `iso` of this instance)

          >> from lang_data import LangData
          >> ld = LangData('en')
          >> print(ld.get_L_alpha())
          >> print(ld_get_L_symbols())

        * Currencies: A way of localising currencies

          >> print(ld.get_L_currencies())
          >> print(ld.get_currency_name())
          >> print(ld.get_currency_format())
          >> print(ld.get_currency_symbol())

        * ISOPrettifier: Uses data in Languages, and format localisation in
          Miscellaneous, to allow pretty-printing languages

          >> print(prettify_lang('zh_Hant-HK'))

        * Languages: Getting the names of languages from ISO 639 code, scripts

          >> get_lang_name('en')
          >> get_script_name('Latn')
          >> get_variant_name(FIXME)

        * Miscellaneous: Localisation of formats
          (such as for comma-separated lists, or parenthesis)

          >> ld.locale_pattern('main text', 'bracketed text')
          >> ld.join(['blah', 'blah'])
          >> ld.join(['apples', 'oranges', 'pears'])
          >> ld.ellipsis('first item', 'last item')
          >> ld.ellipsis('this thought never ends!!')
          >> ld.quotes("testing")
          >> ld.paranthesis("testing")
          >> ld.get_D_yes_no()
          >> ld.code_pattern(FIXME, FIXME)

        * Territory: Localising territory (e.g. country) names

          >> ld.get_L_territories()
          >> ld.get_territory_name('AU')

        * Timezones: Localisation of timezone names
        """
        self.iso = iso
        self.D = CLDRProfiles.get_D_profile_by_iso(
            iso, allow_fallbacks=False
        )
        Timezones.__init__(self)

    def get_script(self):
        return self.D['script']

    def get_territory(self):
        return self.D['territory']
