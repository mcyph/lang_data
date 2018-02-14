from json import dumps
from xmltodict import parse
from lang_data.data_paths import data_path

from defines import NONE, SCRIPT, TERRITORY, VARIANT

class SupplementalData:
    def __init__(self):
        self.DSupplementalData = parse(open(
            data_path('cldr', 'supplemental/supplementalData.xml'),
            'rb'
        ))

        """DSpeakers = self.get_D_num_speakers()

        print dumps(
            DSpeakers,
            ensure_ascii=False,
            indent=4
        )

        print sorted(DSpeakers, key=lambda k: -DSpeakers[k]['population'])"""


    def get_D_sup_languages(self):
        LGroup = self.DSupplementalData['supplementalData']['languageData']['language']
        #pprint(LGroup)

        DOut = {}
        for D in LGroup:
            if D['@type'] in ('cpe', 'fiu', 'pra', 'rjb', 'smi', 'son', 'tut'):
                continue # HACK!

            sec = D.get('@alt') == 'secondary'
            #if sec and len(D)>2: print D

            for x, s in enumerate(self.get_L_removed(
                self.join(
                    part3=D['@type'],
                    script=D.get('@scripts') if not ' ' in D.get('@scripts', ' ') else None,
                    territory=D.get('@territories') if not ' ' in D.get('@territories', ' ') else None
                ),
                [
                    NONE,
                    SCRIPT,
                    TERRITORY,
                    SCRIPT|TERRITORY
                ],
                rem_dupes=True
            )):
                if not s:
                    continue

                #print x, s, D

                if not sec:
                    #assert not s in DOut, s
                    if s in DOut:
                        print 'WARNING:', s, D, DOut[s]
                        if x: continue
                    DOut[s] = D

                elif len(D) > 3:
                    # Use secondary language combinations only as a last resort!
                    # CHECK ME! ===============================================================
                    DOut.setdefault(s, D)
                    #self.DLangData = {}

        return DOut


    def get_D_num_speakers(self):
        #print dumps(
        #    self.DSupplementalData['supplementalData']['territoryInfo'],
        #    ensure_ascii=False,
        #    indent=4
        #)
        LTerritories = (
            self.DSupplementalData['supplementalData']['territoryInfo']['territory']
        )

        DRtn = {}

        for DTerritory in LTerritories:
            if not 'languagePopulation' in DTerritory:
                continue


            """
            {
                "@type": "AC",
                "@gdp": "32580000",
                "@literacyPercent": "99",
                "@population": "940",
                (may be list!)
                "languagePopulation": {
                    "@type": "en",
                    "@populationPercent": "99",
                    "@references": "R1020"
                }
            }
            """

            LLangs = (
                DTerritory['languagePopulation']
                if isinstance(
                    DTerritory['languagePopulation'],
                    (list, tuple)
                )
                else [DTerritory['languagePopulation']]
            )

            for DLang in LLangs:
                try:
                    iso = self.remove_unneeded_info(
                        self.locale_to_iso(DLang['@type'])
                    )
                except (KeyError, AssertionError):
                    iso = DLang['@type']
                    print 'ISO WARNING:', iso


                #print DLang['@type'], iso

                DAdd = DRtn.setdefault(iso, {
                    'population': 0,
                    'DCountries': {}
                })

                percent = float(DLang['@populationPercent'])
                DAdd['population'] += int(
                    int(DTerritory['@population']) * (percent/100)
                )
                DAdd['DCountries'] = DTerritory

        return DRtn


