# -*- coding: utf-8 -*-
from .langdata_classes import Miscellaneous, Timezones, \
    Territories, Currencies, Alphabets, ISOPrettifier, Languages


def _ensure_cldr():
    try:
        global CLDRProfiles
        CLDRProfiles
    except:
        from .cldr import CLDRProfiles


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

          >> print(ld.prettify_lang('zh_Hant-HK'))

        * Languages: Getting the names of languages from ISO 639 code, scripts

          >> ld.get_lang_name('en')
          >> ld.get_script_name('Latn')
          >> ld.get_variant_name(FIXME)

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
        Languages.__init__(self)

    def get_script(self):
        return self.D['script']

    def get_territory(self):
        return self.D['territory']



def get_L_possible_isos():
    import os
    from lang_data.data_paths import data_path
    from iso_tools import ISOTools

    LRtn = []

    for fnam in os.listdir(data_path('cldr', 'main')):
        if fnam.endswith('.xml'):
            if fnam in ('en_US_POSIX.xml', 'el_POLYTON.xml', 'root.xml', 'ar_001.xml', 'es_419.xml'):  # TODO: FIX POLYTONIC GREEK!!
                continue

            try:
                iso = ISOTools.locale_to_iso(fnam.rpartition('.')[0])
                LRtn.append(iso)
            except:
                from warnings import warn
                warn("can't make locale into ISO: %s" % fnam)

    return LRtn

if __name__ == '__main__':
    from pprint import pprint
    pprint(sorted(get_L_possible_isos()))

    for iso in get_L_possible_isos():
        ld = LangData(iso)
        print(ld.get_L_alpha())
        print(ld.get_L_symbols())

        from char_data.unicodeset import unicodeset_from_range
        print(ld.get_L_alpha()[0][1])

        for typ, data in ld.get_L_alpha():
            print(typ, data)
            for i in unicodeset_from_range(data):
                print(i)
