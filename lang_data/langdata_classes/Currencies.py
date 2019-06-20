# -*- coding: utf-8 -*-
from .get import get

CURRENCY_DEFAULT = ''         # 'Yemeni Rial'
CURRENCY_FEW = 'few'          # 'zimbabvejska dolara (2009)'
CURRENCY_MANY = 'many'        # 'zimbabvejskih dolara (2009)'
CURRENCY_ONE = 'one'          # 'Yemeni rial'
CURRENCY_OTHER = 'other'      # 'Yemeni rials'
CURRENCY_TWO = 'two'          # 'ZWL' ???
CURRENCY_ZERO = 'zero'        # 'Zimbabves dollāri (2009)'


class Currencies:
    #=====================================================#
    #          Currencies and Currency Formats            #
    #=====================================================#

    def get_currency_name(self, s, typ=CURRENCY_DEFAULT, default=KeyError):
        return get(self.D, default, ['DCurrencies', s, 'DNames', typ])

    def get_currency_format(self, s, default=KeyError):
        return get(self.D, default, ['DCurrencies', s, 'DFormat', '', s])

    def get_currency_symbol(self, s, default=KeyError):
        D = self.D['DCurrencies'][s]
        return get(D, default, ['DFormat', 'DSymbols', '', s]) # HACK!

    def get_L_currencies(self):
        return sorted(self.D['DCurrencies'])
