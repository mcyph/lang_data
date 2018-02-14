import codecs
import  os
os.chdir('../../../')
from multi_translit.translit.TranslitLoad import DISOToAlpha # (iso, script) -> LAlphabet
from dtaLanguages import GetDLangs
DLangs = GetDLangs() # (iso, script) -> DLang
from input.VirtualKeyboard import DKeyLayouts
from toolkit.rem_dupes import fast_rem_dupes

def get_initial_spaces(S):
    LRtn = []
    for Char in S:
        if Char == ' ':
            LRtn.append(Char)
        else: break
    return ''.join(LRtn)

def process(Text):
    # TODO: Find all UNUSED scripts?
    
    x = 0
    LRtn = []
    CommentMode = 0
    iCommentMode = 0
    ClassIndent = 0
    LLines = Text.split('\n')
    for Line in LLines:
        Line = Line.rstrip().replace('\t', '    ')
        Line = Line.strip('\r\n'+unichr(65279)) # BOM HACK!
        #print 'LINE:', Line.encode('utf-8')
        LRtn.append(Line)
        
        if Line == "'''": 
            # Activate ''' ... ''' comment mode
            #CommentMode = not CommentMode
            iCommentMode = not iCommentMode
            x += 1
            continue
        
        elif not Line or (not Line.split('#')[0].strip()) or CommentMode or (not Line[0].strip()): 
            # Append as-is if line blank, in comment mode, the line is "hash" 
            # commented or whitespace (continuing from a previous line)
            x += 1
            continue
        
        if Line.startswith('class '):
            ClassIndent = len(get_initial_spaces(Line))
            x += 1
            continue
        elif ClassIndent and Line and Line[0]:
            ClassIndent = 0
            x += 1
            continue
        elif ClassIndent and Line.strip().startswith('Profile = '):
            # HACK: Ignore default profiles for now
            ClassIndent = 0
            x += 1
            continue
        elif ClassIndent:
            assert not Line[ClassIndent:].strip(), 'class line should be indented: %s' % Line
            Line = Line[ClassIndent:]
        
        # Get the language name (for verification only)
        LSplit = Line.split('[')
        LangName = LSplit[0].strip()
        
        # Get the ISO code
        LISO = tuple(LSplit[1].split(']')[0].split(':'))
        #assert len(LISO) == 2, LISO
        
        # Get the font language/alphabet name
        def split_script(S): 
            return [i.strip(' {}') for i in S.split('{')]
        LFontLang = tuple(LSplit[2].split(']')[0].split(':'))
        #print LFontLang
        if len(LFontLang) == 1:
            LWord = split_script(LFontLang[0])
            LReadings = None
        elif len(LFontLang) == 2:
            LWord = split_script(LFontLang[0])
            LReadings = split_script(LFontLang[1])
        else: raise Exception(LFontLang)
        
        # TODO: Separate into "Common" characters when in some but 
        # not all data, "Semi-Common" for 2/3 and "Uncommon" for 
        # outdated characters etc if in 1/2 or 1/3?
        # OPEN ISSUE: What about multiple characters? 
        # (i.e. some data might split the characters up)
        
        LScript = (LISO[0], LWord[-1])
        #print 'LScript:', LScript, LScript in DISOToAlpha    
        
        # TODO: Otherwise, find the script in the 
        # keyboard data (if not US English)
        
        y = x
        KeyIndent = 0
        LKeyboards = []
        while 1:
            # Parse the "LKeyLayouts = [...]" format
            if y > len(LLines)-1: break
            Line = LLines[y].replace('\t', '    ')
            if not Line.strip(): break
            
            if Line.lstrip().startswith('LKeyLayouts = '):
                LSplit = Line.split('LKeyLayouts = ')
                KeyIndent = len(LSplit[0])
                LKeyboards.append(LSplit[1].strip().split('#')[0])
            elif KeyIndent and len(get_initial_spaces(Line)) <= KeyIndent:
                break
            elif KeyIndent:
                if Line.strip().startswith('#'):
                    LKeyboards[-1] = LKeyboards[-1].rstrip(', ') # HACK!
                else: LKeyboards.append(Line.strip().split('#')[0])
            y += 1
        
        JSON = ' '.join(LKeyboards).strip()
        if JSON == 'FIXME' and not iCommentMode:
            raise Exception('%s Has FIXME in non-comments mode!' % LangName)
        
        if LKeyboards and JSON != 'FIXME': # HACK!
            JSON = JSON.replace('True', 'true')
            JSON = JSON.replace('False', 'false')
            JSON = JSON.replace('None', 'null')
            JSON = JSON.replace("'", '"')
            JSON = JSON.replace(u'\u200E', '') # LTR HACK!
            print 'Keyboards:', JSON.encode('utf-8'), ord(JSON[-1]), ord(JSON[0])
            LKeyboards = JSON.loads(JSON)
        else: LKeyboards = []
        
        LAlpha = []
        LAccents = []
        for Keyboard, Accents in LKeyboards: # FIXME!
            if not Keyboard in DKeyLayouts:
                import warnings
                warnings.warn('Keyboard Warning: %s (Language %s)' % (Keyboard, LangName))
            elif not Accents:
                # NOTE: Keyboards with accents are ignored as 
                # they usually aren't native to that language!
                
                # TODO: Should the keyboard languages be updated here?
                DLayout = DKeyLayouts[Keyboard]['Layout']
                for k1 in DLayout:
                    for k2 in DLayout[k1]:
                        for LRow in DLayout[k1][k2]:
                            #print LRow
                            LExtend = [i for i in LRow if type(i) in (str, unicode)]
                            if k1: LAccents.extend(LExtend) # deadkeys mode, might have false positives!
                            else: LAlpha.extend(LExtend)
        LAlpha = fast_rem_dupes(LAlpha)
        LAccents = fast_rem_dupes(LAccents)
        
        TotalNum = 0
        DNumChars = {}
        DChars = {}
        Ignore = '0123456789~!@#$%^&*()_+`{}|:"<>?-=[]\;\',./'
        
        def count_chars(L, TotalNum, AddToDChars=True):
            TotalNum += 1
            DCurChars = {}
            for c1 in L:
                if AddToDChars: 
                    DChars[c1] = None
                for c2 in c1:
                    DCurChars[c2] = None
            for c in DCurChars: 
                if not c in DNumChars:
                    DNumChars[c] = 0
                if not AddToDChars and DNumChars[c]:
                    continue # HACK!
                DNumChars[c] += 1
            return TotalNum
        
        if LAlpha:
            # Count the keyboard data
            TotalNum = count_chars(LAlpha, TotalNum)
            # NOTE: Not incremented as the "deadkeys" can have lots of false positives!
            # It only adds to the "frequency" information, it doesn't add to DChars so 
            # characters are only moved from the "uncommon" to the "common" if also in 
            # *other* sources such as the language alphabet info etc and only increments 
            # if added on the previous line
            count_chars(LAccents, TotalNum, AddToDChars=False)
        
        if LScript in DISOToAlpha and DISOToAlpha[LScript]:
            # Find the script in the alphabet data
            TotalNum = count_chars(DISOToAlpha[LScript], TotalNum)
        
        #LTry = LISO # Latin/Cyrillic etc collision warning!
        LTry = LScript
        if LTry in DLangs and DLangs[LTry]['Alphabet']:
            # Find the script in the "old" data if available
            TotalNum = count_chars(DLangs[LTry]['Alphabet'], TotalNum)
        
        ClassChars = ' '*ClassIndent
        def get_map(L):
            # Wrap the data over lines to make it more readable
            import locale
            locale.setlocale(locale.LC_ALL, "") # CHECK ME!
            L.sort(cmp=locale.strcoll)
            
            xx = 0
            LRtn = []
            LItem = []
            for Char in L:
                if Char in '\n\r\t ': continue # HACK!
                if xx and xx % 32 == 0:
                    LRtn.append('%s        %s' % (ClassChars, ';'.join(LItem)))
                    LItem = []
                LItem.append(Char)
                xx += 1
            if LItem: 
                LRtn.append('%s        %s' % (ClassChars, ';'.join(LItem)))
            return '\n'.join(LRtn)
        
        if TotalNum == 1:
            # A single data source, alphabet can't be checked for accuracy
            LRtn.append('%s    Characters:' % ClassChars)
            LChars = list(DChars.keys())
            LChars.sort()
            LChars = [i for i in LChars if i not in Ignore]
            LRtn.append(get_map(LChars))
            
        elif TotalNum == 2 or TotalNum == 3:
            # If in > 2 sets (or two characters) append in "common"
            LCommon = []
            LUncommon = []
            for c in DChars:
                if len(c) == 1:
                    if DNumChars[c] > 1:
                        LCommon.append(c)
                    else: LUncommon.append(c)
                else: 
                    LCommon.append(c)
            LCommon.sort()
            LUncommon.sort()
            LCommon = [i for i in LCommon if i not in Ignore]
            LUncommon = [i for i in LUncommon if i not in Ignore]
            LRtn.append('%s    Common Characters:' % ClassChars)
            LRtn.append(get_map(LCommon))
            LRtn.append('%s    Uncommon Characters:' % ClassChars)
            LRtn.append(get_map(LUncommon))
        x += 1
    return '\n'.join(LRtn)

Folder = 'Data/Languages/Data'
for FileName in os.listdir(Folder):
    # First read the text and add the alphabet info
    if FileName[0] == '.': continue # SVN Hack!
    Path = '%s/%s' % (Folder, FileName)
    File = codecs.open(Path, 'rb', 'utf-8')
    Text = process(File.read())
    File.close()
    
    # Then output the processed lines
    File = codecs.open(Path, 'wb', 'utf-8')
    File.write(Text)
    File.close()
print '\nProgram exited normally!'
