# -*- coding: utf-8 -*-
from toolkit import json_tools
from toolkit.file_tools import file_write
from lang_data.data_paths import data_path

from OpenTSV import open_tsv
from LCompressed import LCompressed
from WriteKey import write

def import_():
    """
    id[3L], 
    Part2B[3L/0], 
    Part2T[3L/0], 
    Part1[2L/0], 
    Scope [I(ndividual) 
           M(acrolanguage) 
           S(pecial)]
    Language_Type [A(ncient), 
                   C(onstructed), 
                   E(xtinct), 
                   H(istorical), 
                   L(iving), 
                   S(pecial)]
    Ref_Name [the primary language name]
    Comment [not used]
    """
    LNames = LCompressed('LLangNames')
    DISO639 = open_tsv(data_path('iso_codes', 'src/iso-639-3.tab'))
    write('DISO639', DISO639, {
        'Part2B': ('part2b', 'str', 3, '???'),
        'Part2T': ('part2t', 'str', 3, '???'),
        'Part1': ('part1', 'str', 2, '??'),
        'Scope': ('scope', 'str', 1),
        'Language_Type': ('language_type', 'str', 1),
        'Ref_Name': ('ref_name', 'names', LNames)
    })
    
    '''
    LangID[3L], 
    CountryID[2L],
    LangStatus[1L] [L(iving), 
                    N(early extinct), 
                    (E)X(tinct), 
                    S(econd language only)],
    Name [duplicate info]
    '''
    DLangCodes = open_tsv(
        data_path('iso_codes', 'src/LanguageCodes.tab'),
        encoding='iso8859-1'
    )
    write('DLangCodes', DLangCodes, {
        'CountryID': ('country_id', 'str', 2),
        'LangStatus': ('lang_status', 'str', 1),
        'Name': ('name', 'names', LNames)
    })
    
    '''
    LangID[3L], 
    CountryID[2L], 
    NameType [L(anguage), 
              LA(lternate), 
              D(ialect), 
              DA(lternate), 
              LP(Pejorative), 
              DP(ejorative)]
    NOTE: Two-letter codes have been modified 
    to be single letters to save space
    Name [WARNING: can be multiple names per ISO code!]
    '''
    DAlternateNames = open_tsv(
        data_path('iso_codes', 'src/LanguageIndex.tab'),
        multi=True,
        encoding='iso8859-1'
    )
    write('DAlternateNames', DAlternateNames, {
        'CountryID': ('country_id', 'str', 2),
        'NameType': ('name_type', 'str', 1, {
            'LA': 'A',
            'DA': 'B',
            'LP': 'C',
            'DP': 'E'
        }),
        'Name': ('name', 'names', LNames)
    })
    
    '''
    M_Id[3L], 
    I_Id[3L], 
    I_Status[A/R]
    '''
    DMacroLangs = open_tsv(
        data_path('iso_codes', 'src/iso-639-3-macrolanguages.tab'),
        multi=True
    )
    write('DMacroLangs', DMacroLangs, {
        'I_Id': ('i_id', 'str', 3),
        'I_Status': ('i_status', 'str', 1)
    })
    DRevMacros = {}
    for k in DMacroLangs:
        for D in DMacroLangs[k]:
            DRevMacros[D['I_Id']] = {
                'M_Id': k,
                'I_Status': D['I_Status']
            }
    write('DRevMacros', DRevMacros, {
        'M_Id': ('m_id', 'str', 3),
        'I_Status': ('i_status', 'str', 1)
    })
    LNames.write()
    
    '''
    Part2B/Part2T[3L], 
    id[3L]
    '''
    DISO639_2 = {}
    for id in DISO639:
        D = DISO639[id]
        
        if 'Part2B' in D and D['Part2T']:
            print D['Part2B']
            DISO639_2[D['Part2B']] = {'Part3': id}
        
        if 'Part2T' in D and D['Part2T']:
            print D['Part2T']
            DISO639_2[D['Part2T']] = {'Part3': id}
    write('DISO639_2', DISO639_2, {'Part3': ('part3', 'str', 3)})
    
    '''
    Part1[2L], id[3L]
    '''
    DISO639_1 = {}
    for id in DISO639:
        D = DISO639[id]
        if 'Part1' in D and D['Part1']:
            print D['Part1']
            DISO639_1[D['Part1']] = {'Part3': id}
    write('DISO639_1', DISO639_1, {'Part3': ('part3', 'str', 3)})
    
    '''
    Add country mappings as a simple JSON file - 
    it doesn't have a large overhead anyway :-P
    
    CountryID[2L], 
    Name[variable], 
    Area[variable]
    '''
    DCountries = open_tsv(
        data_path('iso_codes', 'src/CountryCodes.tab'),
        multi=-1, encoding='iso8859-1'
    )
    for key in DCountries:
        D = DCountries[key]
        DCountries[key] = D['Name'], D['Area']

    file_write(
        data_path('iso_codes', 'CountryCodes.json'),
        json_tools.dumps(DCountries)
    )
    
    #del DISO639, DLangCodes, DAlternateNames, DMacroLangs, DRevMacros
    #while 1: pass
import_()
