import urllib

class ISOEscape:
    #=========================================================================#
    #                            Make Filename Safe                           #
    #=========================================================================#

    def filename_escape(self, iso):
        # HACK - TODO: make more advanced (if need be :P)
        # strictly speaking
        assert not '!' in iso
        self.verify_iso(iso)
        return iso.replace('|', '!')

    def filename_unescape(self, s):
        r = s.replace('!', '|')
        self.verify_iso(r)
        return r

    def filename_join(self, iso1, iso2, escape=True):
        assert not ' ~ ' in iso1+iso2

        if escape:
            iso1 = self.filename_escape(iso1)
            iso2 = self.filename_escape(iso2)

        return '%s ~ %s' % (iso1, iso2)

    def filename_split(self, s, unescape=True):
        r = s.split(' ~ ')
        if unescape:
            r = [self.filename_unescape(i) for i in r]
        return r

    #=========================================================================#
    #                              Make URL Safe                              #
    #=========================================================================#

    def url_escape(self, iso):
        self.verify_iso(iso)
        #assert not '+' in iso, 'plus characters not allowed!'
        #assert not '!' in iso, 'exclamation characters not allowed!'
        #assert not '.' in iso, 'full stops not allowed!'
        # Hopefully "!" is slightly less unsafe than "|", but I
        # think it is regarded as bad practice in some ways
        #iso = iso.replace('|', '!')
        return urllib.quote_plus(iso.encode('utf-8')) # , safe='!'

    def url_unescape(self, s):
        r = urllib.unquote_plus(s).decode('utf-8')
        #r = r.replace('!', '|')
        self.verify_iso(r)
        return r

    def url_join(self, iso1, iso2):
        assert not '_-_' in iso1
        assert not '_-_' in iso2

        return '%s_-_%s' % (
            self.url_escape(iso1),
            self.url_escape(iso2)
        )

    def url_split(self, s):
        r = s.split('_-_')
        r = [self.url_unescape(i) for i in r]
        return r
