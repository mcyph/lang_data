# LBlank -> elements to ignore if no attributes+no value

SBlank = {
    'identity',
    'fallback',
    'languages',
    'scripts',
    'territories',
    'variants',
    'keys',
    'types',
    'transformNames',
    'measurementSystemNames',
    'codePatterns',
    'localeDisplayNames',
    'stopwords',
    'characters',
    'delimiters',
    'localeDisplayPattern',

    'dateFormat',
    'dateFormats',
    'dateTimeFormat',
    'dateTimeFormats',
    'availableFormats',
    'dateTimeFormats',
    'timeFormat',
    'timeFormats',
    'intervalFormats',

    'months',
    'days',
    'dayPeriods',
    'quarters',

    'eraNames',
    'eraAbbr',
    'eraNarrow',
    'eras',
    'fields',
    'units',

    'long',
    'short',

    'ldml',
    'posix',
    'messages',
    'layout',

    'scientificFormat',
    'decimalFormat',
    'percentFormat',
    'currencyFormat',

    'scientificFormatLength',
    'decimalFormatLength',
    'percentFormatLength',
    'currencyFormatLength',
    'dateTimeFormatLength',

    'scientificFormats',
    'decimalFormats',
    'percentFormats',
    'currencyFormats',

    'dates',
    'currencies',
    'numbers',
    'calendars',
    'timeZoneNames',

    'listPatterns',
    'listPattern',
    'appendItems',

    'otherNumberingSystems',

    'contextTransforms',

    'cyclicNameSets',
    'monthPatterns'
}

STypeOnly = {
    'dateFormatLength',
    'dateTimeFormatLength',
    'calendar',
    'timeFormatLength',
    'decimalFormatLength',
    #'zone',

    'monthWidth',
    'dayWidth',
    'dayPeriodWidth',
    'quarterWidth',

    'monthContext',
    'dayContext',
    'dayPeriodContext',
    'quarterContext',

    'field',
    'unit',
    'territory',

    'contextTransformUsage',

    # Cyclic calendars etc
    'calendar', # WARNING!
    'cyclicNameSet',
    'cyclicNameContext',
    'cyclicNameWidth',
    'monthPatternWidth',
    'monthPatternContext'
}

SNumberSystemsOnly = {
    'numberSystem',
    'decimalFormats',
    'scientificFormats',
    'percentFormats',
    'currencyFormats'
}
