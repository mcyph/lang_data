# -*- coding: utf-8 -*-
"""
    babel.numbers
    ~~~~~~~~~~~~~

    Locale dependent formatting and parsing of numeric data.

    The default locale for the functions in this module is determined by the
    following environment variables, in that order:

     * ``LC_NUMERIC``,
     * ``LC_ALL``, and
     * ``LANG``

    :copyright: (c) 2013 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""
# TODO:
#  Padding and rounding increments in pattern:
#  - http://www.unicode.org/reports/tr35/ (Appendix G.6)
from decimal import Decimal, InvalidOperation
import math
import re

#from babel.core import default_locale, Locale
#from babel._compat import range_type


#LC_NUMERIC = default_locale('LC_NUMERIC')


def get_currency_name(currency, count=None, locale=LC_NUMERIC):
    """Return the name used by the locale for the specified currency.

    >>> get_currency_name('USD', locale='en_US')
    u'US Dollar'
    
    .. versionadded:: 0.9.4

    :param currency: the currency code
    :param count: the optional count.  If provided the currency name
                  will be pluralized to that number if possible.
    :param locale: the `Locale` object or locale identifier
    """
    loc = Locale.parse(locale)
    if count is not None:
        plural_form = loc.plural_form(count)
        plural_names = loc._data['currency_names_plural']
        if currency in plural_names:
            return plural_names[currency][plural_form]
    return loc.currencies.get(currency, currency)


def get_currency_symbol(currency, locale=LC_NUMERIC):
    """Return the symbol used by the locale for the specified currency.

    >>> get_currency_symbol('USD', locale='en_US')
    u'$'

    :param currency: the currency code
    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).currency_symbols.get(currency, currency)


def get_decimal_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate decimal fractions.

    >>> get_decimal_symbol('en_US')
    u'.'

    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).number_symbols.get('decimal', '.')


def get_plus_sign_symbol(locale=LC_NUMERIC):
    """Return the plus sign symbol used by the current locale.

    >>> get_plus_sign_symbol('en_US')
    u'+'

    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).number_symbols.get('plusSign', '+')


def get_minus_sign_symbol(locale=LC_NUMERIC):
    """Return the plus sign symbol used by the current locale.

    >>> get_minus_sign_symbol('en_US')
    u'-'

    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).number_symbols.get('minusSign', '-')


def get_exponential_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate mantissa and exponent.

    >>> get_exponential_symbol('en_US')
    u'E'

    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).number_symbols.get('exponential', 'E')


def get_group_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate groups of thousands.

    >>> get_group_symbol('en_US')
    u','

    :param locale: the `Locale` object or locale identifier
    """
    return Locale.parse(locale).number_symbols.get('group', ',')


def format_number(number, locale=LC_NUMERIC):
    """Return the given number formatted for a specific locale.

    >>> format_number(1099, locale='en_US')
    u'1,099'
    >>> format_number(1099, locale='de_DE')
    u'1.099'


    :param number: the number to format
    :param locale: the `Locale` object or locale identifier
    """
    # Do we really need this one?
    return format_decimal(number, locale=locale)


def format_decimal(number, format=None):
    """Return the given decimal number formatted for a specific locale.

    >>> format_decimal(1.2345, locale='en_US')
    u'1.234'
    >>> format_decimal(1.2346, locale='en_US')
    u'1.235'
    >>> format_decimal(-1.2346, locale='en_US')
    u'-1.235'
    >>> format_decimal(1.2345, locale='sv_SE')
    u'1,234'
    >>> format_decimal(1.2345, locale='de')
    u'1,234'

    The appropriate thousands grouping and the decimal separator are used for
    each locale:

    >>> format_decimal(12345.5, locale='en_US')
    u'12,345.5'

    :param number: the number to format
    :param format:
    :param locale: the `Locale` object or locale identifier
    """
    pattern = parse_pattern(format)
    return pattern.apply(number, locale)




class NumberFormatError(ValueError):
    """Exception raised when a string cannot be parsed into a number."""


PREFIX_END = r'[^0-9@#.,]'
NUMBER_TOKEN = r'[0-9@#.\-,E+]'

PREFIX_PATTERN = r"(?P<prefix>(?:'[^']*'|%s)*)" % PREFIX_END
NUMBER_PATTERN = r"(?P<number>%s+)" % NUMBER_TOKEN
SUFFIX_PATTERN = r"(?P<suffix>.*)"

number_re = re.compile(r"%s%s%s" % (PREFIX_PATTERN, NUMBER_PATTERN,
                                    SUFFIX_PATTERN))

def split_number(value):
    """Convert a number into a (intasstring, fractionasstring) tuple"""
    if isinstance(value, Decimal):
        # NB can't just do text = str(value) as str repr of Decimal may be
        # in scientific notation, e.g. for small numbers.

        sign, digits, exp = value.as_tuple()
        # build list of digits in reverse order, then reverse+join
        # as per http://docs.python.org/library/decimal.html#recipes
        int_part = []
        frac_part = []

        digits = list(map(str, digits))

        # get figures after decimal point
        for i in range(-exp):
            # add digit if available, else 0
            if digits:
                frac_part.append(digits.pop())
            else:
                frac_part.append('0')

        # add in some zeroes...
        for i in range(exp):
            int_part.append('0')

        # and the rest
        while digits:
            int_part.append(digits.pop())

        # if < 1, int_part must be set to '0'
        if len(int_part) == 0:
            int_part = '0',

        if sign:
            int_part.append('-')

        return ''.join(reversed(int_part)), ''.join(reversed(frac_part))
    text = ('%.9f' % value).rstrip('0')
    if '.' in text:
        a, b = text.split('.', 1)
        if b == '0':
            b = ''
    else:
        a, b = text, ''
    return a, b


def parse_grouping(p):
    """Parse primary and secondary digit grouping

    >>> parse_grouping('##')
    (1000, 1000)
    >>> parse_grouping('#,###')
    (3, 3)
    >>> parse_grouping('#,####,###')
    (3, 4)
    """
    width = len(p)
    g1 = p.rfind(',')
    if g1 == -1:
        return 1000, 1000
    g1 = width - g1 - 1
    g2 = p[:-g1 - 1].rfind(',')
    if g2 == -1:
        return g1, g1
    g2 = width - g1 - g2 - 2
    return g1, g2


def parse_pattern(pattern):
    """Parse number format patterns"""
    if isinstance(pattern, NumberPattern):
        return pattern

    def _match_number(pattern):
        rv = number_re.search(pattern)
        if rv is None:
            raise ValueError('Invalid number pattern %r' % pattern)
        return rv.groups()

    # Do we have a negative subpattern?
    if ';' in pattern:
        pattern, neg_pattern = pattern.split(';', 1)
        pos_prefix, number, pos_suffix = _match_number(pattern)
        neg_prefix, _, neg_suffix = _match_number(neg_pattern)
    else:
        pos_prefix, number, pos_suffix = _match_number(pattern)
        neg_prefix = '-' + pos_prefix
        neg_suffix = pos_suffix
    if 'E' in number:
        number, exp = number.split('E', 1)
    else:
        exp = None
    if '@' in number:
        if '.' in number and '0' in number:
            raise ValueError('Significant digit patterns can not contain '
                             '"@" or "0"')
    if '.' in number:
        integer, fraction = number.rsplit('.', 1)
    else:
        integer = number
        fraction = ''

    def parse_precision(p):
        """Calculate the min and max allowed digits"""
        min = max = 0
        for c in p:
            if c in '@0':
                min += 1
                max += 1
            elif c == '#':
                max += 1
            elif c == ',':
                continue
            else:
                break
        return min, max

    int_prec = parse_precision(integer)
    frac_prec = parse_precision(fraction)
    if exp:
        frac_prec = parse_precision(integer+fraction)
        exp_plus = exp.startswith('+')
        exp = exp.lstrip('+')
        exp_prec = parse_precision(exp)
    else:
        exp_plus = None
        exp_prec = None
    grouping = parse_grouping(integer)
    return NumberPattern(pattern, (pos_prefix, neg_prefix),
                         (pos_suffix, neg_suffix), grouping,
                         int_prec, frac_prec,
                         exp_prec, exp_plus)


class NumberPattern(object):

    def __init__(self, pattern, prefix, suffix, grouping,
                 int_prec, frac_prec, exp_prec, exp_plus):
        self.pattern = pattern
        self.prefix = prefix
        self.suffix = suffix
        self.grouping = grouping
        self.int_prec = int_prec
        self.frac_prec = frac_prec
        self.exp_prec = exp_prec
        self.exp_plus = exp_plus
        if '%' in ''.join(self.prefix + self.suffix):
            self.scale = 100
        elif '‰' in ''.join(self.prefix + self.suffix):
            self.scale = 1000
        else:
            self.scale = 1

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.pattern)

    def apply(self, value, locale, currency=None):
        if isinstance(value, float):
            value = Decimal(str(value))
        value *= self.scale
        is_negative = int(value < 0)
        if self.exp_prec: # Scientific notation
            value = abs(value)
            if value:
                exp = int(math.floor(math.log(value, 10)))
            else:
                exp = 0
            # Minimum number of integer digits
            if self.int_prec[0] == self.int_prec[1]:
                exp -= self.int_prec[0] - 1
            # Exponent grouping
            elif self.int_prec[1]:
                exp = int(exp / self.int_prec[1]) * self.int_prec[1]
            if not isinstance(value, Decimal):
                value = float(value)
            if exp < 0:
                value = value * 10**(-exp)
            else:
                value = value / 10**exp
            exp_sign = ''
            if exp < 0:
                exp_sign = get_minus_sign_symbol(locale)
            elif self.exp_plus:
                exp_sign = get_plus_sign_symbol(locale)
            exp = abs(exp)
            number = '%s%s%s%s' % \
                 (self._format_sigdig(value, self.frac_prec[0],
                                     self.frac_prec[1]),
                  get_exponential_symbol(locale),  exp_sign,
                  self._format_int(str(exp), self.exp_prec[0],
                                   self.exp_prec[1], locale))
        elif '@' in self.pattern: # Is it a siginificant digits pattern?
            text = self._format_sigdig(abs(value),
                                      self.int_prec[0],
                                      self.int_prec[1])
            if '.' in text:
                a, b = text.split('.')
                a = self._format_int(a, 0, 1000, locale)
                if b:
                    b = get_decimal_symbol(locale) + b
                number = a + b
            else:
                number = self._format_int(text, 0, 1000, locale)
        else: # A normal number pattern
            a, b = split_number(bankersround(abs(value),
                                             self.frac_prec[1]))
            b = b or '0'
            a = self._format_int(a, self.int_prec[0],
                                 self.int_prec[1], locale)
            b = self._format_frac(b, locale)
            number = a + b
        retval = '%s%s%s' % (self.prefix[is_negative], number,
                                self.suffix[is_negative])
        if '¤' in retval:
            retval = retval.replace('¤¤¤',
                get_currency_name(currency, value, locale))
            retval = retval.replace('¤¤', currency.upper())
            retval = retval.replace('¤', get_currency_symbol(currency, locale))
        return retval

    def _format_sigdig(self, value, min, max):
        """Convert value to a string.

        The resulting string will contain between (min, max) number of
        significant digits.
        """
        a, b = split_number(value)
        ndecimals = len(a)
        if a == '0' and b != '':
            ndecimals = 0
            while b.startswith('0'):
                b = b[1:]
                ndecimals -= 1
        a, b = split_number(bankersround(value, max - ndecimals))
        digits = len((a + b).lstrip('0'))
        if not digits:
            digits = 1
        # Figure out if we need to add any trailing '0':s
        if len(a) >= max and a != '0':
            return a
        if digits < min:
            b += ('0' * (min - digits))
        if b:
            return '%s.%s' % (a, b)
        return a

    def _format_int(self, value, min, max, locale):
        width = len(value)
        if width < min:
            value = '0' * (min - width) + value
        gsize = self.grouping[0]
        ret = ''
        symbol = get_group_symbol(locale)
        while len(value) > gsize:
            ret = symbol + value[-gsize:] + ret
            value = value[:-gsize]
            gsize = self.grouping[1]
        return value + ret

    def _format_frac(self, value, locale):
        min, max = self.frac_prec
        if len(value) < min:
            value += ('0' * (min - len(value)))
        if max == 0 or (min == 0 and int(value) == 0):
            return ''
        width = len(value)
        while len(value) > min and value[-1] == '0':
            value = value[:-1]
        return get_decimal_symbol(locale) + value
