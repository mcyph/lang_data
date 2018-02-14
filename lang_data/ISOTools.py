from isotools_classes import NONE, LANG, SCRIPT, TERRITORY, VARIANT
from isotools_classes import ISOGuesser, ISOToolsBase, LikelySubtags, SupplementalData, LangGroups

class ISOTools(ISOGuesser, ISOToolsBase, LikelySubtags, SupplementalData, LangGroups):
    def __init__(self):
        ISOToolsBase.__init__(self)
        LikelySubtags.__init__(self)
        SupplementalData.__init__(self)
        ISOGuesser.__init__(self)

ISOTools = ISOTools()
