from collections import namedtuple


SJapanese = {
    'Hrkt', 'Kana', 'Hira', 'Jpan'
}
SChinese = {
    'Hani', 'Hans', 'Hant', 'Bopo'
}
SKorean = {
    'Hang', 'Kore'
}
SThaiLike = {
    # Khmer, Lao, Thai, Burmese scripts
    'Thai', 'Khmr', 'Laoo', 'Mymr'
}
SIndic = {
    'Beng', 'Deva', 'Gujr', 'Guru', 'Knda',
    'Mlym', 'Orya', 'Sinh', 'Sylo', 'Taml', 'Telu'
}
SEastAsian = (
    # TODO: Add more scripts/languages here(!)
    SJapanese | SChinese | SKorean | SThaiLike | {'Yiii', 'vi'}
)
SNoSpaces = (
    SJapanese | SChinese | SThaiLike
)
SNotInflected = (
    # TODO: Add more languages here(!)
    SChinese | {'tha', 'vie'}
)
SRTLScripts = {
    # (These should be reasonably complete I hope though)
    'Hebr', 'Nkoo', 'Samr', 'Cprt', 'Armi', 'Phnx', 'Lydi', 'Khar',
    'Sarb', 'Avst', 'Prti', 'Phli', 'Orkh', 'Arab', 'Syrc', 'Syre',
    'Syrj', 'Syrn', 'Thaa'
}


LangProps = namedtuple('LangProps', [
    'chinese', 'japanese', 'korean',
    'thailike', 'indic',
    'has_spaces', 'east_asian',
    'inflected', 'rtl'
])


class LangGroups:
    def get_lang_props(self, iso):
        _ = self.split(
            self.guess_omitted_info(iso)
        )

        return LangProps(
            chinese=_.script in SChinese,
            japanese=_.script in SJapanese,
            korean=_.script in SKorean,
            thailike=_.script in SThaiLike,
            indic=_.script in SIndic,

            has_spaces=not _.script in SNoSpaces,
            east_asian=(
                _.script in SEastAsian or
                _.lang in SEastAsian
            ),
            inflected=_.lang in SNotInflected,
            rtl=_.script in SRTLScripts
        )
