# -*- coding: utf-8 -*-
# See also https://docs.google.com/present/view?id=dfqr8rd5_303ckth2zhn
# and http://unicode.org/reports/tr35/

from lxml import etree
from lang_data.data_paths import data_path
from cldr_ignored_tags import SBlank, SNumberSystemsOnly, STypeOnly

DEBUG_MODE = False # turn me on for warnings!

def get(o, k, default=''):
    return o.get(k, default)

def get_tag_names(elem, add_keys=False):
    L = []
    while 1:
        if add_keys and elem.keys():
            items = '; '.join(['%s: %s' % (key, value) for key, value in elem.items()])
            L.append('%s[%s]' % (elem.tag, items))
        else:
            L.append(elem.tag)
        
        elem = elem.getparent()
    
        if elem is None or elem=='ldml':
            break
    return '.'.join(reversed(L))

def get_cal_type(elem):
    """
    Returns gregorian, buddhist, islamic etc
    """
    while 1:
        if elem is None:
            raise Exception("calendar element not found!")
        elif elem.tag == 'calendar':
            return get(elem, 'type')
        
        elem = elem.getparent()

def get_recursive(elem, attr, STags):
    """
    Go up the element tree until one of the tags in STags
    is found, then return the value of the attribute `attr`
    """
    if not isinstance(STags, set):
        STags = {STags}

    while 1:
        #print elem.tag
        if elem is None:
            raise Exception("element not found!")
        elif elem.tag in STags:
            return get(elem, attr)

        elem = elem.getparent()

def get_D_cldr(path):
    DRtn = {
        'locale_name': path[:-4] if path[-4:] == '.xml' else path
    }

    path = data_path('cldr', 'main/%s' % path)

    DTZ = {}
    DCurrency = {}
    
    for event, elem in etree.iterparse(path):
        tag = elem.tag.strip()
        print_ = "<%s>: %s" % (get_tag_names(elem, add_keys=True), 
                               (elem.text or 'None').strip())
        
        #if True:
        #    print print_
        
        parent = elem.getparent()
        parent_tag = parent != None and parent.tag.strip()
        
        parent_parent = parent != None and parent.getparent()
        parent_parent_tag = parent_parent not in (False, None) and parent_parent.tag.strip()
        
        DAlts = {'language': 'DLangs',
                 'script': 'DScripts',
                 'territory': 'DTerritories',
                 
                 # e.g. fi.xml has an alt of "secondary" for FONUPA
                 'variant': 'DVariants',}
        
        DTypes = {'key': 'DKeys',
                  
                  # Sort orders (e.g. Sort Digits Numerically)/
                  # numeric systems (e.g. Arabic-Indic Digits)
                  #'type': 'DTypes',
                  
                  # e.g. {'x-Fullwidth': 'Fullwidth', ...}
                  'transformName': 'DTransformNames',
                  
                  'stopwordList': 'DStopWords',
                  'exemplarCharacters': 'DAlpha',
                  'codePattern': 'DCodePatterns',
                  #'pattern': 'DPatterns',
                  'measurementSystemName': 'DMeasurementSystems',
                  'listPatternPart': 'DListPatternParts',
                  
                  'inText': 'DInText', # e.g. "type: currency": "lowercase-words"
                  }
        
        #=======================================================#
        #                 File Language Code                    #
        #=======================================================#
        
        if tag=='language' and not elem.text:
            # The language code of the current XML file
            assert DRtn.get('language_code')==elem.get('type') or not 'language_code' in DRtn
            DRtn['language_code'] = elem.get('type')
        
        elif tag=='territory' and not elem.text:
            # The territory of the currenct file
            assert not 'territory' in DRtn
            DRtn['territory'] = elem.get('type')
        
        elif tag=='script' and not elem.text:
            assert not 'script' in DRtn
            DRtn['script'] = elem.get('type')
        
        elif tag == 'version':
            assert not 'version' in DRtn
            DRtn['version'] = elem.get('number')
        
        elif tag == 'generation':
            assert not 'generation_date' in DRtn
            DRtn['generation_date'] = elem.get('date')
        
        elif tag=='alias' and parent_tag=='ldml':
            # e.g. in az_AZ.xml "az_Latn_AZ"
            assert not 'alias' in DRtn
            DRtn['alias'] = elem.text
        
        elif tag == 'fallback':
            # e.g. 'es_ES' for 'ca.xml' (Catalan)
            assert not 'fallback' in DRtn
            DRtn['fallback'] = elem.text
        
        elif tag=='variant' and not elem.text:
            # e.g. en_US_POSIX has a variant of 'POSIX'
            DRtn['variant'] = elem.get('type')
        
        #=======================================================#
        #                 Symbols/Delimiters                    #
        #=======================================================#
        
        elif parent_tag in ('symbols', 'delimiters'):
            number_system = get(parent, 'numberSystem') # 'arab' or 'latn' differentiated in Arabic languages
            alt = get(elem, 'alt') # e.g. 'mlym' for `nan` in native Malayalam instead of 'NaN'
            
            # Symbols, e.g. "percentSign", "group", "plusSign" etc
            DSymbols = DRtn.setdefault('DSymbols', {})
            DNumberSystem = DSymbols.setdefault(number_system, {})
            DAlt = DNumberSystem.setdefault(alt, {})
            
            assert not tag in DAlt
            DAlt[tag] = elem.text
        
        #=======================================================#
        #           Miscellaneous Words/Expressions             #
        #=======================================================#
        
        elif tag in ('yesstr', 'nostr',
                     'localePattern', 'localeSeparator'):
            DMap = {'yesstr': 'yes',
                    'nostr': 'no',
                    'localePattern': 'locale_pattern',
                    'localeSeparator': 'locale_separator'}
            
            conv_tag = DMap[tag]
            assert not conv_tag in DRtn
            DRtn[conv_tag] = elem.text
        
        elif tag=='pattern' and parent_tag in ('scientificFormat', 
                                               'percentFormat',
                                               'currencyFormat'):
            DMap = {'scientificFormat': 'DScientificFormat',
                    'percentFormat': 'DPercentFormat',
                    'currencyFormat': 'DCurrencyFormat'}

            number_system = get_recursive(parent, 'numberSystem', parent_tag+'s')
            DPattern = DRtn.setdefault(DMap[parent_tag], {})

            assert not number_system in DPattern, get_tag_names(elem, True)
            DPattern[number_system] = elem.text

        elif tag == 'ellipsis':
            typ = get(elem, 'type')
            DEllipsis = DRtn.setdefault('DEllipsis', {})
            
            assert not typ in DEllipsis
            DEllipsis[typ] = elem.text
        
        #=======================================================#
        #          Symbols/Delimiters/Number Patterns           #
        #=======================================================#
        
        elif tag=='symbols' and elem.get('numberSystem'):
            LNumberSystems = DRtn.setdefault('LNumberSystems', [])
            LNumberSystems.append(elem.get('numberSystem'))
            
        elif tag == 'defaultNumberingSystem':
            assert not 'default_number_system' in DRtn
            DRtn['default_number_system'] = elem.text

        elif parent_tag=='otherNumberingSystems':
            DOtherNumberingSystems = DRtn.setdefault('DOtherNumberingSystems', {})
            assert not tag in DOtherNumberingSystems
            DOtherNumberingSystems[tag] = elem.text

        elif tag=='pattern' and parent_tag=='decimalFormat':
            DNumPatterns = DRtn.setdefault('DNumPatterns', {})
            typ = get(elem, 'type')

            #print elem.items(), elem.text, get_tag_names(elem)
            #assert not typ in DNumPatterns, get_tag_names(elem)

            LNumPatterns = DNumPatterns.setdefault(typ, [])
            LNumPatterns.append(elem.text)
        
        elif tag == 'moreInformation':
            # Usually a question mark, specific to the language
            # e.g. Spanish might have a backwards question mark
            assert not 'more_information' in DRtn
            DRtn['more_information'] = elem.text
        
        #=======================================================#
        #                 Layout/Orientation                    #
        #=======================================================#
        
        elif tag == 'inList':
            assert not 'in_list' in DRtn
            DRtn['in_list'] = elem.text
        
        elif tag == 'orientation':
            # Provides whether "right-to-left" etc 
            # for "characters" or "lines"
            assert not 'DOrientation' in DRtn
            DRtn['DOrientation'] = dict(list(elem.items()))
        
        #=======================================================#
        #                     Currencies                        #
        #=======================================================#
            
        elif tag == 'currency':
            # End the currency tag
            DCurrencies = DRtn.setdefault('DCurrencies', {})
            cur_currency = get(elem, 'type')
            
            assert not cur_currency in DCurrencies
            DCurrencies[cur_currency] = DCurrency
            DCurrency = {}
            
        elif tag in ('symbol', 'pattern', 'decimal', 'group') and parent_tag=='currency':
            # A symbol for a currency, e.g. $ or ¥
            # Note not many currencies have them in many languages
            
            DMap = {'symbol': 'DSymbols',
                    'pattern': 'DPatterns',
                    'decimal': 'DDecimals',
                    'group': 'DGroups'}
            
            cur_currency = get(parent, 'type')
            alt = get(elem, 'alt') # e.g. 'new' in `ee.xml`
            
            DFormat = DCurrency.setdefault('DFormat', {})
            DTag = DFormat.setdefault(DMap[tag], {})
            DAlt = DTag.setdefault(alt, {})
            
            assert not cur_currency in DAlt
            DAlt[cur_currency] = elem.text
            
        elif tag == 'displayName' and parent_tag=='currency':
            count = get(elem, 'count') # MULTIPLE?
            #typ = get(elem, 'type')
            
            DNames = DCurrency.setdefault('DNames', {})
            assert not count in DNames
            DNames[count] = elem.text
            
        #=======================================================#
        #                      Timezones                        #
        #=======================================================#
        
        elif tag in ('metazone', 'zone'):
            # End of the timezone's metazone tag
            DMap = {'metazone': 'DMetazones',
                    'zone': 'DTZs'}
            
            DTZs = DRtn.setdefault(DMap[tag], {})
            typ = get(elem, 'type')
            
            assert not typ in DTZs
            DTZs[typ] = DTZ
            DTZ = {}
            
        elif parent_parent_tag in ('metazone', 'zone'):
            # "zone" Provides a place (exemplarCity) or timezone name 
            # (e.g. BST, British Summer Time) associated with a metazone
            
            # "metazone" provides a timezone encompassing a region, 
            # e.g. "Eastern Standard Time"
            
            if not parent.tag in DTZ:
                DTZ[parent.tag] = {}
            
            assert not tag in DTZ[parent.tag]
            DTZ[parent.tag][tag] = elem.text
        
        elif tag == 'exemplarCity':
            # a "zone" element as parent, registers a city as 
            # being particularly associated with a timezone
            
            alt = get(elem, 'alt') # 'secondary' in fi.xml
            DAlt = DTZ.setdefault(alt, {})
            
            assert not 'exemplar_city' in DAlt
            DAlt['exemplar_city'] = elem.text
        
        elif tag == 'commonlyUsed' and parent_tag=='metazone':
            DTZsCommon = DRtn.setdefault('DTZsCommon', {})
            tz = get(parent, 'type')
            assert not tz in DTZsCommon
            DTZsCommon[tz] = True if elem.text.strip()=='true' else False
        
        elif parent_tag == 'timeZoneNames' and tag in ('hourFormat', 
                                                       'gmtFormat', 
                                                       'regionFormat', 
                                                       'fallbackFormat', 
                                                       'fallbackRegionFormat'):
            #assert not list(elem.keys())
            DTZNames = DRtn.setdefault('DTZNames', {})
            
            assert not tag in DTZNames
            DTZNames[tag] = elem.text
        
        elif tag == 'gmtZeroFormat':
            assert not 'gmt_zero_format' in DRtn
            DRtn['gmt_zero_format'] = elem.text
        
        #=======================================================#
        #                       Types                           #
        #=======================================================#
        
        elif tag == 'type':
            key = get(elem, 'key')
            typ = get(elem, 'type')
            
            DTypes = DRtn.setdefault('DTypes', {})
            DKey = DTypes.setdefault(key, {})
            assert not typ in DKey
            DKey[typ] = elem.text
        
        #=======================================================#
        #                    Dates/Times                        #
        #=======================================================#
        
        elif parent_tag in ('monthWidth', 'dayWidth', 'dayPeriodWidth', 'quarterWidth'):
            DMap = {'monthWidth': 'DMonths',
                    'dayWidth': 'DDays',
                    'dayPeriodWidth': 'DDayPeriods',
                    'quarterWidth': 'DQuarters'}
            
            context = get(parent_parent, 'type')
            width = get(parent, 'type')
            typ = get(elem, 'type') # e.g. "1" (for January) etc
            alt = get(elem, 'alt') # e.g. "variant" (usually None)
            yeartype = get(elem, 'yeartype') # e.g. "leap" in Hebrew's profile (usually None)
            
            DItems = DRtn.setdefault(DMap[parent_tag], {})
            DItem = DItems.setdefault(get_cal_type(elem), {})
            DContext = DItem.setdefault(context, {})
            DWidth = DContext.setdefault(width, {})
            DType = DWidth.setdefault(typ, {})
            DYearType = DType.setdefault(yeartype, {})
            
            assert not alt in DYearType
            DYearType[alt] = elem.text
        
        elif tag == 'era':
            DMap = {'eraNames': 'DNames',
                    'eraAbbr': 'DAbbr',
                    'eraNarrow': 'DNarrow'}
            
            DEras = DRtn.setdefault('DEras', {})
            DItems = DEras.setdefault(get_cal_type(elem), {})
            DItem = DItems.setdefault(DMap[parent_tag], {})
            
            typ = get(elem, 'type')
            assert not typ in DItem
            DItem[typ] = elem.text
        
        elif tag == 'greatestDifference':
            # NOTE: Falls back to intervalFormatFallback if not available (I think?)
            interval_id = get(parent, 'id')
            diff_id = get(elem, 'id')
            
            DItems = DRtn.setdefault('DGreatestDiffs', {})
            DIntervals = DItems.setdefault(get_cal_type(elem), {})
            DInterval = DIntervals.setdefault(interval_id, {})
            
            assert not diff_id in DInterval
            DInterval[diff_id] = elem.text
        
        elif tag == 'intervalFormatFallback':
            DFallbacks = DRtn.setdefault('DIntervalFallbacks', {})
            cal_type = get_cal_type(elem)
            
            assert not cal_type in DFallbacks
            DFallbacks[cal_type] = elem.text
        
        elif parent_tag == 'field' and tag in ('displayName', 'relative'):
            if tag == 'displayName':
                # Assign fallbacks to `None`
                assert not 'type' in elem
            
            field_type = get(parent, 'type') # e.g. year
            relative_type = get(elem, 'type') # e.g. "-1" for "Last year"
            
            DCalFields = DRtn.setdefault('DCalFields', {})
            DItems = DCalFields.setdefault(get_cal_type(elem), {})
            DFields = DItems.setdefault(field_type, {})
            
            assert not relative_type in DFields
            DFields[relative_type] = elem.text
        
        elif tag in ('am', 'pm'):
            # Provides an alternate for AM/PM e.g. in twq.xml
            # TODO: How does this differ from <dayPeriod type="{am/pm}"> ? ===============================
            # NOTE: in twq.xml dayPeriod is "Subbaahi/Zaarikay banda"! ===================================
            assert not tag in DRtn
            DRtn[tag] = elem.text

        elif tag == 'cyclicName':
            # Chinese cyclic calendars
            typ = get_recursive(elem, 'type', 'calendar')
            nameset = get_recursive(elem, 'type', 'cyclicNameSet')
            name_context = get_recursive(elem, 'type', 'cyclicNameContext')
            name_width = get_recursive(elem, 'type', 'cyclicNameWidth')
            name = get_recursive(elem, 'type', 'cyclicName')

            DCyclicCalendars = DRtn.setdefault('DCyclicCalendars', {})
            DType = DCyclicCalendars.setdefault(typ, {})
            DNameset = DType.setdefault(nameset, {})
            DNameContext = DNameset.setdefault(name_context, {})
            DNameWidth = DNameContext.setdefault(name_width, {})

            assert not name in DNameWidth
            DNameWidth[name] = elem.text

        elif tag == 'monthPattern':
            typ = get_recursive(elem, 'type', 'calendar')
            pattern_context = get_recursive(elem, 'type', 'monthPatternContext')
            pattern_width = get_recursive(elem, 'type', 'monthPatternWidth')
            pattern = get_recursive(elem, 'type', 'monthPattern')

            DMonthPatterns = DRtn.setdefault('DMonthPatterns', {})
            DType = DMonthPatterns.setdefault(typ, {})
            DContext = DType.setdefault(pattern_context, {})
            DWidth = DContext.setdefault(pattern_width, {})

            assert not pattern in DWidth
            DWidth[pattern] = elem.text

        #=======================================================#
        #                Dates/Times Formats                    #
        #=======================================================#
        
        elif parent_tag in ('dateFormat', 'dateTimeFormat', 'timeFormat') and tag=='pattern':
            DMap = {'dateFormat': 'DDateFormats',
                    'dateTimeFormat': 'DDateTimeFormats',
                    'timeFormat': 'DTimeFormats'}
            
            cal_type = get_cal_type(elem) 
            
            DItems = DRtn.setdefault(DMap[parent_tag], {})
            DItem = DItems.setdefault(cal_type, {})
            DFormats = DItem.setdefault('DFormats', {})
            
            typ = get(parent_parent, 'type') # full/long/medium/short etc
            assert not typ in DFormats
            DFormats[typ] = elem.text
        
        elif parent_parent_tag=='dateTimeFormats' and tag=='dateFormatItem':
            # ??? ==========================================================================================
            DDates = DRtn.setdefault('DDateTimes', {})
            DDate = DDates.setdefault(get_cal_type(elem), {})
            DFormats = DDate.setdefault('DFormats', {})
            
            typ = get(elem, 'type')
            id = get(elem, 'id') # d/EEEd/Gy/hm/hms etc
            assert not id in DFormats
            DFormats[typ] = elem.text
        
        elif tag=='unitPattern' and parent_tag=='currencyFormats':
            # Currency unit patterns (one per script)
            typ = get(parent, 'type') # e.g. year-past, year, year-future
            count = get(elem, 'count') # e.g. "one", 'other", "2", "end" etc
            alt = get(elem, 'alt') # e.g. short (usually None)
            number_system = get_recursive(parent, 'numberSystem', 'currencyFormats')
            
            DUnitPatterns = DRtn.setdefault('DCurrencyUnitPatterns', {})
            DNumberSystem = DUnitPatterns.setdefault(number_system, {})
            DUnitPattern = DNumberSystem.setdefault(typ, {})
            DAlt = DUnitPattern.setdefault(alt, {})

            assert not count in DAlt
            DAlt[count] = elem.text

        elif tag=='unitPattern' and parent_tag=='unit':
            # Unit patterns for dates (?)
            typ = get(parent, 'type') # e.g. year-past, year, year-future
            count = get(elem, 'count') # e.g. "one", 'other", "2", "end" etc
            alt = get(elem, 'alt') # e.g. short (usually None)

            DUnitPatterns = DRtn.setdefault('DUnitPatterns', {})
            DUnitPattern = DUnitPatterns.setdefault(typ, {})
            DAlt = DUnitPattern.setdefault(alt, {})

            assert not count in DAlt
            DAlt[count] = elem.text
        
        elif tag == 'dateRangePattern':
            # Usually e.g. "{0} - {1}" for formatting "{from date} - {to date}"
            assert not 'date_range_pattern' in DRtn
            DRtn['date_range_pattern'] = elem.text
        
        elif tag == 'appendItem':
            assert parent_parent_tag == 'dateTimeFormats'
            
            DAppendItems = DRtn.setdefault('DAppendItems', {})
            LType = DAppendItems.setdefault(get_cal_type(elem), [])
            
            # Appends e.g. ("Day", "{0} ({2}: {1})")
            # TODO: What is the pattern for? ============================================================
            LType.append((get(elem, 'request'), elem.text))
        
        #=======================================================#
        #                Dates/Time Defaults                    #
        #=======================================================#
            
        elif tag=='default' and parent_tag=='monthContext':
            typ = get(parent, 'type')
            cal_type = get_cal_type(elem)
            
            DMonthContextDefault = DRtn.setdefault('DMonthContextDefault', {})
            DCalType = DMonthContextDefault.setdefault(cal_type, {})
            
            assert not typ in DCalType
            DCalType[typ] = elem.get('choice')
        
        elif tag=='default' and parent_tag in ('months', 'dateFormats', 'dateTimeFormats'):
            DMap = {'months': 'DMonthsDefault',
                    'dateFormats': 'DDateFormatsDefault',
                    'dateTimeFormats': 'DDateTimeFormatsDefault'}
            
            cal_type = get_cal_type(elem)
            DItems = DRtn.setdefault(DMap[parent_tag], {})
            
            assert not cal_type in DItems
            DItems[cal_type] = elem.get('choice')
        
        elif tag=='default' and parent_tag=='calendars':
            assert not 'default_calendar' in DRtn
            DRtn['default_calendar'] = elem.get('choice') # CHECK ME! ===================================
        
        elif tag=='default' and parent_tag=='timeFormats':
            assert not 'default_timeformat' in DRtn
            DRtn['default_timeformat'] = elem.get('choice') # CHECK ME! =================================

        #=======================================================#
        #                 Context Transforms                    #
        #=======================================================#

        elif tag == 'contextTransform':
            typ1 = get_recursive(elem, 'type', 'contextTransformUsage')
            typ2 = get(elem, 'type')

            DContextTransforms = DRtn.setdefault('DContextTransforms', {})
            DType1 = DContextTransforms.setdefault(typ1, {})

            assert not typ2 in DType1
            DType1[typ2] = elem.text

        #=======================================================#
        #                     Other Tags                        #
        #=======================================================#
        
        elif tag in DAlts and elem.text:
            # Tags with "type" and sometimes "alt" attributes
            for key in elem:
                if not key in ('type', 'alt'):
                    print 'tag %s key skipped warning: %s' % (tag, key)
            
            D = DRtn.setdefault(DAlts[tag], {})
            typ = get(elem, 'type')
            i_D = D.setdefault(typ, {})
            
            alt = get(elem, 'alt') # e.g. 'short' (language)/'variant' (script)/None
            assert not alt in i_D
            
            i_D[alt] = elem.text
        
        elif tag in DTypes:
            # Tags with only "type" attributes
            for key in elem:
                if key != 'type':
                    print 'tag %s key skipped warning: %s' % (tag, key)
            
            D = DRtn.setdefault(DTypes[tag], {})
            assert not 'alt' in elem
            
            typ = get(elem, 'type')
            assert not typ in D
            D[typ] = elem.text
            
        else:
            if tag in SBlank and not (elem.text or '').strip() and not list(elem.keys()):
                continue
            elif tag in STypeOnly and tuple(elem.keys())==('type',):
                continue
            elif tag=='intervalFormatItem' and tuple(elem.keys())==('id',):
                continue
            elif tag in SNumberSystemsOnly and tuple(elem.keys())==('numberSystem',):
                continue
            elif tag=='alias' and elem.get('path'):
                continue # root.xml HACK! ==============================================================
            
            if DEBUG_MODE:
                print 'NOT HANDLED:', print_
    return DRtn

if __name__ == '__main__':
    import os
    from pprint import pprint
    
    D = get_D_cldr('en.xml')
    pprint(D)
    
    if False:
        print
        
        for path in os.listdir(data_path('cldr')):
            if path.endswith('.xml') and (path != 'root.xml' or True):
                print 'OPENING:', path
                D = get_D_cldr(path)
                print
    