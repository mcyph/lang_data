from get import get

COUNTRIES_ALL = 0
COUNTRIES_CODES_ONLY = 1
COUNTRIES_LETTERS_ONLY = 2

TERRITORY_DEFAULT = ''
TERRITORY_VARIANT = 'variant'


class Territories:
    #=====================================================#
    #                    Territories                      #
    #=====================================================#

    def get_territory_name(self, s, typ=TERRITORY_DEFAULT, default=KeyError):
        """
        Get the localized name for territory name `s`
        """
        return get(self.D, default, ['DTerritories', s, typ])

    def get_L_territories(self, typ=COUNTRIES_ALL):
        """
        Get a list of country codes/letters
        """
        DTerritories = self.D['DTerritories']

        if typ == COUNTRIES_ALL:
            return sorted(DTerritories)
        elif typ == COUNTRIES_CODES_ONLY:
            return sorted(i for i in DTerritories if i.isdigit())
        elif typ == COUNTRIES_LETTERS_ONLY:
            return sorted(i for i in DTerritories if not i.isdigit())
        else:
            raise Exception("Unknown country type: %s" % typ)
