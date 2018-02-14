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


class _LangData(Alphabets,
                Currencies,
                ISOPrettifier,
                Languages,
                Miscellaneous,
                Territories,
                Timezones):

    def __init__(self, iso):
        self.iso = iso

        self.D = CLDRProfiles.get_D_profile_by_iso(iso, allow_fallbacks=False)
        Timezones.__init__(self)

    def get_script(self):
        return self.D['script']

    def get_territory(self):
        return self.D['territory']
