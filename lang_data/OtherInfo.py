from isotools_classes import LikelySubtags, SupplementalData

class OtherInfo(LikelySubtags, SupplementalData):
    def __init__(self):
        LikelySubtags.__init__(self)
        SupplementalData.__init__(self)

OtherInfo = OtherInfo()
