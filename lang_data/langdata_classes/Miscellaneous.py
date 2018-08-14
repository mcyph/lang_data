ELLIPSIS_INITIAL = 'initial'
ELLIPSIS_MEDIAL = 'medial'
ELLIPSIS_FINAL = 'final'

CODE_PATTERN_LANGUAGE = 'language'
CODE_PATTERN_SCRIPT = 'script'
CODE_PATTERN_TERRITORY = 'territory'


class Miscellaneous:
    #=====================================================#
    #                   Miscellaneous                     #
    #=====================================================#

    def locale_pattern(self, normal, brackets):
        """
        Make things in brackets e.g. in English "foo (bar)"
        """
        pat = self.D['locale_pattern']
        #print type(pat), type(normal), type(brackets)
        return unicode(pat).format(normal, brackets)

    def join(self, L):
        """
        Joins with locale-specific commas etc
        """
        return self.D['locale_separator'].join(L)

    def list_pattern_join(self, L):
        """
        makes e.g. ['apples', 'oranges', 'pears'] ->
                   "apples, oranges, and pears" (etc)
        """
        DParts = self.D['DListPatternParts']

        if not L:
            return ''
        elif len(L) == 1:
            return L[0]
        elif len(L) == 2:
            return unicode(DParts['2']).format(*L)

        # OPEN ISSUE: Optimize this if {0} is at the start of the string! ====================================
        # (It's not a top priority though)
        L = L[::-1]
        r = unicode(DParts['start']).format(L.pop(), L.pop())
        while 1:
            if len(L) == 1:
                break
            r = unicode(DParts['middle']).format(r, L.pop())
        return unicode(DParts['end']).format(r, L.pop())

    def ellipsis(self, first, second=None, typ=ELLIPSIS_MEDIAL):
        """
        Puts contents into an ellipsis
        e.g. "A...Z"
        """
        return unicode(self.D['DEllipsis'][typ]).format(first, second)

    def quotes(self, s):
        """
        Enclose in quotation marks
        """
        D = self.D['DSymbols']['']['']
        start = D['quotationStart']
        end = D['quotationEnd']
        return '%s%s%s' % (start, s, end)

    def parenthesis(self, s):
        """
        Enclose in "alternate" quotation marks, often parenthesis
        """
        D = self.D['DSymbols']['']['']
        start = D['alternateQuotationStart']
        end = D['alternateQuotationEnd']
        return '%s%s%s' % (start, s, end)

    def get_D_yes_no(self):
        D = {}
        D['yes'], D['y'] = self.D['yes'].split(':')
        D['no'], D['n'] = self.D['no'].split(':')
        return D

    def code_pattern(self, key, value):
        pattern = self.D['DCodePatterns'][key]
        return unicode(pattern).format(value)

