from string import ascii_letters, digits

DLetters = {}
DNumbers = {}
for x, c in enumerate(ascii_letters+digits):
    DLetters[c] = x+1
    DNumbers[x+1] = c

def letters_to_code(s):
    """
    Convert s into XXYYZZ number for 
    e.g. country codes or language codes
    """
    LRtn = []
    for char in s:
        ord_ = str(DLetters[char])
        if len(ord_) == 1:
            ord_ = '0%s' % ord_
        LRtn.append(ord_)
    return int(''.join(LRtn)) if LRtn else ''

def code_to_letters(I):
    """
    Convert integer format I into characters
    """
    LRtn = []
    s = str(I)
    if len(s) % 2 != 0:
        s = '0%s' % s
    
    while 1:
        if not s: 
            break
        
        i = int(s[:2])
        LRtn.append(DNumbers[i])
        s = s[2:]
    return ''.join(LRtn)
