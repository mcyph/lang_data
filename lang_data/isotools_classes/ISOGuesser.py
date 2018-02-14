from defines import SCRIPT, TERRITORY, VARIANT, NONE

def pprint(o):
    from json import dumps
    print dumps(o, indent=4)

class ISOGuesser:
    def __init__(self):
        DLikelySubtags = self.DLikelySubtags = self.get_D_likely_subtags()

        # TODO: Check there aren't any collisions (somehow)! ======================================================================
        D = self.DRevLikelySubtags = {}
        for k, v in DLikelySubtags.items():
            for i in self.get_L_removed(
                v,
                [
                    NONE,
                    TERRITORY
                ]
            ):
                if not self.split(k)[0]:
                    # Only use in reverse if a language to reverse to!
                    continue
                D[i] = k

        #print sorted(self.DRevLikelySubtags.items())
        #self.DLangData = self.get_D_sup_languages()


    def pack_iso(self, iso):
        """
        Removes unneeded info from the ISO, e.g. "ja_Jpan" -> "ja",
        assuming the territory (e.g. "...-JP") isn't needed.

        This makes sure territory info isn't removed when shortening as
        it's meant to be reversible.
        """
        has_territory = self.removed(iso, TERRITORY) != iso
        if has_territory:
            return iso
        else:
            return self.remove_unneeded_info(iso)

    def unpack_iso(self, iso):
        """
        The opposite of pack_iso(), above.
        """
        return self.removed(
            self.guess_omitted_info(iso),
            TERRITORY
        )


    def remove_unneeded_info(self, s):
        """
        e.g. for "en_Latn", try remove the Latn part if obvious
        """
        if s in self.DRevLikelySubtags:
            r = self.DRevLikelySubtags[s]
            if r == 'zh_Hani':
                return 'zh' # HACK!

            elif r == 'cmn':
                return 'zh' # HACK!
            return r

        if s == 'cmn':
            return 'zh'
        return s

    def guess_omitted_info(self, s):
        lang, script, territory, variant = self.split(s)
        assert lang or territory, \
            "iso or territory is required to guess omitted info: %s" % s

        #print iso, script, territory, variant, s in self.DLikelySubtags, s in self.DLangData

        # Look in the likely subtags
        if s in self.DLikelySubtags:
            return self.DLikelySubtags[s]
        else:
            # Try with various keys removed as needed
            # e.g. "en_Latn" doesn't have a key, but "en" does (value
            # "en_Latn-US"), so look for without the script etc as well.

            for i in self.get_L_removed(
                s,
                [
                    SCRIPT,
                    TERRITORY,
                    VARIANT,
                    SCRIPT|TERRITORY,
                    SCRIPT|VARIANT,
                    VARIANT|TERRITORY,
                    SCRIPT|TERRITORY|VARIANT
                ],
                rem_dupes=True
            ):
                if i in self.DLikelySubtags:
                    i_split = self.split(self.DLikelySubtags[i])

                    # Don't allow if information (aside from territory)
                    # differs from one to the other!
                    allow = True
                    for x, y in zip(
                        (i_split.lang, i_split.script, i_split.variant),
                        (lang, script, variant)
                    ):
                        if x and y and x != y:
                            allow = False
                            break

                    if not allow:
                        continue

                    return self.join(*[
                        y or x for x, y in zip(
                            i_split,
                            (lang, script, territory, variant)
                        )
                    ])

        # Look in the CLDR supplemental data to add missing scripts
        # maybe deriving script from a main locale if only territory but
        # not script provided if it's a secondary locale
        #if s in self.DLangData:
        #    D = self.DLangData[s]

        #    lang = D['@type']
        #    script = D['@scripts'] if '@scripts' in D \
        #        and not ' ' in D['@scripts'] else script
        #    territory = D['@territories'] if '@territories' in D \
        #        and not ' ' in D['@territories'] else territory

        return self.join(
            lang, script, territory, variant
        )


if __name__ == '__main__':
    from lang_data.ISOTools import ISOTools as i
    from cProfile import run

    print i.get_L_removed('nl_Latn-NL', [
        NONE,
        SCRIPT,
        TERRITORY,
        SCRIPT|TERRITORY
    ],
        #rem_dupes=True
    )

    print i.guess_omitted_info('hy')
    print i.guess_omitted_info('ko')
    print i.guess_omitted_info('zh')
    print i.guess_omitted_info('en_Latn|MINE!')
    print i.guess_omitted_info('en_Shaw')

    #run("for x in xrange(50000): i.guess_omitted_info('ja')")
    #for x in xrange(5000):
    #    print i.guess_omitted_info('ja')
