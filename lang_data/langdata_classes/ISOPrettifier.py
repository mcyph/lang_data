from iso_tools.iso_codes import ISOCodes, DCountries


SAlwaysShow = {
    # Don't shorten Taiwan Traditional Chinese
    # to "zh_Hant-TW" when printing
    'zh_Hant-TW'
}


class ISOPrettifier:
    def prettify_lang(self, s, always_show_script=False):
        if not always_show_script and not s in SAlwaysShow:
            from iso_tools import ISOTools
            s = ISOTools.remove_unneeded_info(s)

        pr_lang, pr_script, pr_territory, pr_variant = self.get_L_pretty(s)

        return self._locale_pattern(pr_lang or 'und', [
            pr_script, # FIXME!
            pr_territory,
            pr_variant
        ])

    def prettify_script(self, s):
        """
        Localizes a script/lang-name/variant
        into a more hu man-readable format
        """
        pr_lang, pr_script, pr_territory, pr_variant = self.get_L_pretty(s)

        return self._locale_pattern(pr_script or 'Zyyy', [
            pr_lang,
            pr_territory,
            pr_variant
        ])

    def prettify_territory(self, s):
        pr_lang, pr_script, pr_territory, pr_variant = self.get_L_pretty(s)

        return self._locale_pattern(pr_territory, [
            pr_lang,
            pr_script,
            pr_variant
        ])

    def get_L_pretty(self, s):
        """
        get the localized names of the language,
        script, territory+variant (if specified)
        """
        from iso_tools.ISOTools import ISOTools
        lang, script, territory, variant = ISOTools.split(s)

        if lang:
            DISO = ISOCodes.get_D_iso(lang)

        territory_default = DCountries.get(territory, [territory])[0]

        return (
            self.get_lang_name(
                lang,
                default=DISO.get('short_name', DISO['long_name'])
            ) if lang else None,

            self.get_script_name(script) if script else None,
            self.get_territory_name(territory, default=territory_default) if territory else None,
            self.get_variant_name(variant, default=variant) if variant else None
        )

    def _locale_pattern(self, s, L):
        assert s

        L = [i for i in L if i]

        if len(L) > 1:
            return self.locale_pattern(
                s,
                self.join(L)
            )
        elif L:
            return self.locale_pattern(s, L[0])
        else:
            return s
