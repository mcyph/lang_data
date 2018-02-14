from LangData import LangData
from cldr.get_cldr_profiles import DPart3ToProfiles
from langdata_classes.Timezones import METAZONE_SZ_LONG_FIRST, METAZONE_SZ_SHORT_FIRST

def tests(iso, profile=None):
    inst = LangData(iso, profile)

    '''
    print 'ALPHABET:', inst.get_L_alpha()
    print 'SYMBOLS:', inst.get_L_symbols()

    try:
        for iso in inst.get_L_part3():
            print 'LANG:', iso, inst.get_lang_name(iso, default=None)
    except:
        print 'KeyError GETTING LANGUAGES!'

    try:
        for script in inst.get_L_scripts():
            print 'SCRIPT:', script, inst.get_script_name(script, default=None)
    except KeyError:
        print 'KeyError GETTING SCRIPTS!'

    for currency in inst.get_L_currencies():
        print currency,\
        inst.get_currency_name(currency, default=None),\
        inst.get_currency_format(currency, default=None),\
        inst.get_currency_symbol(currency, default=None)

    print 'DEXEMPLARCITIES:', inst.get_D_exemplar_cities()

    for tz in inst.get_L_exemplar_cities():
        print 'EXEMPLAR CITY:', tz, inst.get_exemplar_city(tz, default=None)

    try:
        for metazone in inst.get_L_metazones():
            common = inst.get_metazone_common(metazone, default=None)
            long_name = inst.get_metazone(metazone, METAZONE_SZ_LONG_FIRST, default=None)
            short_name = inst.get_metazone(metazone, METAZONE_SZ_SHORT_FIRST, default=None)
            print 'METAZONE:', metazone, long_name, short_name, common
    except KeyError:
        print 'KeyError GETTING METAZONES!'

    try:
        for t in inst.get_L_territories():
            print 'TERRITORY:', t, inst.get_territory_name(t, default=None)
    except KeyError:
        print 'KeyError GETTING TERRITORIES!'
    '''

    mls = inst.get_my_lang_string()
    DLang = inst.get_D_lang(mls)
    try:
        print mls, inst.pretty_print_D_lang(DLang), DLang
    except KeyError:
        print 'KeyError!'

    print inst.list_pattern_join(['apples'])
    print inst.list_pattern_join(['apples', 'oranges'])
    print inst.list_pattern_join(['apples', 'oranges', 'pears'])
    print inst.list_pattern_join(['apples', 'oranges', 'pears', 'bananas', 'grapes'])

if __name__ == '__main__':
    L = sorted(DPart3ToProfiles)
    #L = [('jpn', 'JP')]
    #L = [('en', 'AU')]

    for i in L:
        if not i[1]:
            continue

        print i
        tests(*i)
