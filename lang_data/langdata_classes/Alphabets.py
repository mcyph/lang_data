class Alphabets:
    #=====================================================#
    #                Alphabets and Symbols                #
    #=====================================================#

    def get_L_alpha(self):
        """
        Get a list of the alphabet data in a more usable order
        """
        LPriority = [
            '', # Main: Letters used in the language.
            'auxiliary', # Auxiliary: Letters used in foreign and technical words.
            'index', # Index: Head letters that appear in an index.
            'punctuation',
            'currencySymbol'
        ]

        DAlpha = self.D['DAlpha']
        assert all(key in LPriority for key in DAlpha)

        L = []
        for key in LPriority:
            if key in DAlpha:
                L.append((key, DAlpha[key]))
        return L

    def get_L_symbols(self, exclude_blank=True, len_limit=None):
        """
        Get any relevant symbols from DSymbols
        """
        DSymbols = self.D['DSymbols']

        LRtn = []
        for script1, DScript1 in list(DSymbols.items()):

            for script2, DScript2 in list(DScript1.items()):
                LItem = []
                for key, symbol in list(DScript2.items()):
                    if not symbol and exclude_blank:
                        continue
                    elif len_limit and len(symbol)>len_limit:
                        continue

                    LItem.append((key or None, symbol))

                if exclude_blank and not LItem:
                    continue
                LRtn.append((script1, script2, sorted(LItem)))

        return sorted(LRtn)
