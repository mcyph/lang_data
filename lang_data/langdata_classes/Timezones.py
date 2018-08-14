from get import get

METAZONE_SZ_LONG = 'long'
METAZONE_SZ_SHORT = 'short'
METAZONE_SZ_LONG_FIRST = ('long', 'short')
METAZONE_SZ_SHORT_FIRST = ('short', 'long')

METAZONE_TYPE_DAYLIGHT = 'daylight'
METAZONE_TYPE_GENERIC = 'generic'
METAZONE_TYPE_STANDARD = 'standard'
METAZONE_TYPE_GENERIC_FIRST = ('generic', 'standard')
METAZONE_TYPE_DAYLIGHT_FIRST = ('daylight', 'generic')
METAZONE_TYPE_STANDARD_FIRST = ('standard', 'generic')


class Timezones:
    def __init__(self):
        self.DCities = {}

        DTZs = self.D['DTZs']
        for k, D in DTZs.items():
            self.DCities[k.partition('/')[-1]] = D

    #=====================================================#
    #                     Timezones                       #
    #=====================================================#

    def get_metazone_common(self, metazone, default=KeyError):
        """
        Get whether `metazone` (e.g. "Phoenix_Islands") is common
        """
        return get(self.D, default, ['DTZsCommon', metazone])

    def get_metazone(self, metazone,
                     sz=METAZONE_SZ_LONG_FIRST,
                     typ=METAZONE_TYPE_GENERIC_FIRST,
                     default=KeyError):
        """
        Get the printable name for metazone/timezone `tz`
        """
        DMetazones = self.D['DMetazones']
        return get(DMetazones, default, [metazone, sz, typ])

    def get_exemplar_city(self, tz, default=KeyError):
        if '/' in tz:
            return get(self.D, default, ['DTZs', tz, '', 'exemplar_city'])
        else:
            return get(self.DCities, default, [tz, '', 'exemplar_city'])

    def get_D_exemplar_cities(self):
        """
        Gets a map from timezone to exemplar city
        {timezone: exemplar city, ...}

        OPEN ISSUE: Can this be used for localizing common cities?
        """
        DRtn = {}
        DTZs = self.D['DTZs']
        for tz, i_D in DTZs.items():
            if '' in i_D and 'exemplar_city' in i_D['']:
                DRtn[tz] = i_D['']['exemplar_city']
        return DRtn

    def get_L_metazones(self):
        return sorted(self.D['DMetazones'])

    def get_L_exemplar_cities(self):
        """
        Returns Region/City

        For use with get_exemplar_city above
        """
        return sorted(self.D['DTZs'])
