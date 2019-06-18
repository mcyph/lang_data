=====
About
=====

Provides access to parts of the Unicode Common Locale Data Repository (CLDR).

=======
Install
=======

=====
Usage
=====


::

    from lang_data.LangData import LangData

    ld = LangData('en')
    get_L_alpha
    get_L_symbols

    get_currency_name
    get_currency_format
    get_currency_symbol
    get_L_currencies

    prettify_script(self, s):
    prettify_territory(self, s):
    get_L_pretty(self, s):
    _locale_pattern(self, s, L):
