from xmltodict import parse
from lang_data.data_paths import data_path

class LikelySubtags:
    def __init__(self):
        self.DLikelySubtags = parse(open(
            data_path('cldr', 'supplemental/likelySubtags.xml'),
            'rb'
        ))

    def get_D_likely_subtags(self):
        LLS = self.DLikelySubtags['supplementalData']['likelySubtags']['likelySubtag']

        DOut = {}
        #return
        for DLS in LLS:
            #print DLS
            from_ = DLS['@from']
            to = DLS['@to']

            DOut[self.locale_to_iso(from_)] = self.locale_to_iso(to)


        #print 'SS:', DOut

        #DOut['zh'] = 'zh' # HACK!!!
        return DOut
