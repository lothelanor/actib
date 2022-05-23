import argparse
import sys
import tempfile
import os
import subprocess
import re
import bs4
#from pybo import WordTokenizer
from bs4 import BeautifulSoup
from botok import Text, WordTokenizer
from botok.config import Config
from multiprocessing import freeze_support

VERBS = None

def ensureverbs():
    """ returns a dict with verb as key and True as value """
    global VERBS
    if VERBS:
        return
    VERBS = {}
    source_file = open("conf/verblex.txt", encoding='utf-8')
    line = source_file.readline()
    while line:
        elts = line.split("\t")
        VERBS[elts[0]] = True
        line = source_file.readline()
    source_file.close()

VERBPAT = re.compile("([^/ ]+)/+[^ v]*v\.[^ ]+ ")
VERBCASEPAT = re.compile(r"/(?P<firsttag>[^\s]+\.)(?P<second>[^ \.]+\s+[^/ ]+/+)(?P<caseorcv>case|cv)\.")

def verbrepl(matchobj, verbs):
    """ a function to be used in re.sub, replaces non-verbs tagged as verbs into n.count """
    entry = matchobj.group(1)
    if entry not in verbs:
        return entry+'/n.count '
    else:
        return matchobj.group(0)

def verblook(posstr, verbs):
    """
    Function takes two arguments (posstr, verbs), 
    and returns the output converting tags of Tibetan tokens that are tagged as verbs but don't occur in the verb lexicon
    to 'n.count' instead.
    """   
    posstr = re.sub(VERBPAT, lambda x: verbrepl(x,verbs), posstr)
    
    return posstr

def verbcaserepl(matchobj):
    firsttag = matchobj.group(1)
    secondtag = matchobj.group(3)
    if firsttag.startswith("v.") and secondtag == "case":
        return "/"+firsttag+matchobj.group(2)+"cv."
    if not firsttag.startswith("v.") and secondtag == "cv":
        return "/"+firsttag+matchobj.group(2)+"case."
    return str(matchobj.group(0))

def verbcaselookup(posstr):
    return re.sub(VERBCASEPAT, lambda x: verbcaserepl(x), posstr)

def forcedpos(posstr):
    posstr = re.sub(r'(^|\s)((?:ཏེ|སྟེ)་?//?)([^\s]+)', r'\1\2cv.sem', posstr)
    posstr = re.sub(r'(^|\s)((?:p[0-9]+)//?)([^\s]+)', r'\1\2page.num', posstr)
    posstr = re.sub(r'(^|\s)((?:l[0-9]+)//?)([^\s]+)', r'\1\2line.num', posstr)
    posstr = re.sub(r'(^|\s)((?:[0-9༠-༳]+)་?//?)([^\s]+)', r'\1\2numeral', posstr)
    posstr = re.sub(r'(^|\s)((?:ཏུ|དུ)་?//?)([^\s]+)', r'\1\2cv.term', posstr)
    posstr = re.sub(r'(^|\s)((?:ནོ|རོ|ཏོ|འོ|དོ)་?//?)([^\s]+)', r'\1\2cv.fin', posstr)
    posstr = re.sub(r'(^|\s)((?:ལོ|ངོ|གོ|སོ|མོ)་?//?)([^\s]+)\s།', r'\1\2cv.fin །', posstr)
    posstr = re.sub(r'(^|\s)((?:《|》|༈|༼|༽|༏|༑|༐|༒)//?)([^\s]+)', r'\1\2punc', posstr)
    posstr = re.sub(r'(^|\s)((?:གང|མཆོག)་?//?)([^\s]+)', r'\1\2adj', posstr) #new SOAS pos corrections starting here
    return posstr

WTConfig = Config() # TODO: load only the GMD
WT = WordTokenizer(WTConfig)

def open_pecha_tokenizer(in_str):
    return WT.tokenize(in_str)

def actib_modifier(tokens):
    op = []
    for t in tokens:
        op_token = {
            'start': t.start,
            'end': t.start + t.len,
            'type': t.chunk_type
        }
        op.append(op_token)
    return op

def lexiconsegment(multisylstr):
    #return multisylstr
    # t = Text(multisylstr, tok_params={'profile': 'GMD'})  # Text caches the tries using lru_cache. The trie should only be loaded once.
    try:
        t = Text(multisylstr, tok_params={'profile': 'GMD'})
        tokens = t.custom_pipeline('dummy', open_pecha_tokenizer, actib_modifier, 'dummy')
    except:
        print("botok failed to segment "+multisylstr)
        return multisylstr
    res = ''
    first = True
    for token in tokens:
       if not first:
           res += "\n"
       first = False
       res += multisylstr[token['start']:token['end']]
    return res

def xmltocorpus(xml_str):
    """
    Function that uses bs4 to return the relevant text from the xmlcorpus as a string.
    It uses a str for xmlcorpus instead of list because str changes are costly, 
    so one string to modify in the end is better than joining all strings from a list.
    """ 

    xmlcorpus = ""

    soup = BeautifulSoup(xml_str, 'lxml')

    first = True
    for p in soup.find_all('tei:p'):
        if not xmlcorpus.endswith("\n") and not first:
            xmlcorpus += "\n"
        first = False
        xmlcorpus += getpage(p)

    #Below is to find pagenums in W-files (bad OCR'ed ones that we don't need now)
    #for p in soup.find_all('tei:milestone'):
    #   xmlcorpus += getpage(p)

    return xmlcorpus

def getpage(p):
    """
    Function that finds the pagenums, text and linenums and returns it as the xmlcorpus.
    """

    xmlcorpus = ""
    pagename = p["n"]
    if pagename:
        #strips off file extensions, e.g. ".tif"  
        dotidx = pagename.find(".")  
        if dotidx >= 0:
            xmlcorpus += "p" + pagename[0:dotidx] + "\n" #add pagenum
        else: 
            xmlcorpus += "p" + pagename + "\n" #add pagenum
    first = True
    for child in p.children:
        #check if child is str or linenum markup
        if isinstance(child,str): 
            text = remove_spur_chars(child)
            text = sylsplit(text)
            xmlcorpus += text
        elif child.get("unit") == "line" and child.get("n"):
            linename = child["n"]
            if not first:
                xmlcorpus += "\n"
            first = False
            xmlcorpus += "ln" + linename + "\n" #add linenum

    return xmlcorpus

def remove_spur_chars(s):
    s = re.sub(r"(\(|\)|\\|\$|\"|-|\.|\*|=|£|¥|\+|è|%|;|¿|¡|¤|\?)+","",s)
    #s = re.sub(r"[A-Za-z0-9]+","",s) #to keep line and page numbers
    return s

def preprocess(s):
    s = remove_spur_chars(s)
    s = sylsplit(s)
    return s


def sylsplit(child):
    """
    Function that puts every syllable on a newline
    and adds utterance boundaries after shads and the like.
    It takes child as its argument as these are the children of p (=tei:p);
    both the tei:milestone markup for line numbers and the text are children.
    """

    #add newlines after Tibetan
    child = re.sub(r"([ༀ-࿘])([^ༀ-࿘])",r"\1\n\2",child) 

    #add newlines before Tibetan
    child = re.sub(r"([^ༀ-࿘])([ༀ-࿘])",r"\1\n\2",child) 
    
    #Add newline & utt after shad and the like.
    child = re.sub(r"([།-༔])",r"\n\1\n<utt>\n",child) 

    #Add newline after tsheg and the like.
    child = re.sub(r"([་༌ཿ࿒])([ༀ-࿘])",r"\1\n\2",child) 

    #Put Tibetan brackets, etc. on a newline.
    child = re.sub(r"([༼༽《》༈])",r"\n\1\n",child)

    #Change unbreakable tsheg to breakable tsheg. 
    child = re.sub("\u0F0C","\u0F0B",child) 

    #Remove empty lines.
    child = re.sub(r"\n+",r"\n",child) 

    return child

def cutallgroups(m):
    """
    Auxiliary function, takes a match as argument and inserts a new line
    between all the groups
    """
    res = ''
    lastghaslb = True
    for g in m.groups():
        #print("g=\""+g+"\"")
        if g is None:
            continue
        if not lastghaslb and not str(g) == "" and not g.startswith("\n"):
            res += "\n"
        lastghaslb = (g.endswith("\n") or str(g) == "")
        res += g
    return res

def post_seg_processing_str(srcstr):
    """
    Function to be called after segmentation to finale it:
       - cut affixes
       - remove tags
       - fix obvious errors

    Example of input:
༄༅/S །/S <utt>
།/S <utt>
རྒྱ་/X གར་/E སྐད་/S དུ/S །/S <utt>
རཱ་/X ཛ་/Y ནཱི་//Y ཏི་/Z ཤཱསྟྲ་//M བྷཱུ་//E མི་/S པཱ་/Y ལ་/E སྱ་//S ཨ་/X ལངྐཱ་//Y ར་/Z ནཱ་/Y མ/E །/S <utt>
བོད་/S སྐད་/S དུ/S །/S <utt>
    """
    
    # གྱིས & al. are wrongly tagged as /SS or /ES, in that case they should not
    # be split
    srcstr = re.sub(r'(^|[\n་ ])((?:གིས|ཀྱིས|ཡིས|ཅེས|ཞེས|གྱིས)་?)//?[ES]S ?', r'\2\n', srcstr)

    # splitting ra and sa before /ES and /SS
    srcstr = re.sub(r'([རས]་?)//?[ES]S ?', r'\n\1\n',srcstr)

    # remove markers
    srcstr = re.sub('//?[ES]S? ?','\n',srcstr)
    srcstr = re.sub('//?[XYZM] ?','',srcstr)

    # splitting on other affixes (and punctuation) all the time (there can be more than one so we do that twice)
    srcstr = re.sub(r'([^\n ་])(འི་?|འོ་?|འམ་?|འང་?)($|[ \n])', lambda m: cutallgroups(m), srcstr)
    srcstr = re.sub(r'([^\n ་])(འི་?|འོ་?|འམ་?|འང་?)($|[ \n])', lambda m: cutallgroups(m), srcstr)
    # relatively unambiguous particles which we want to cut too
    # cutting on the left:
    srcstr = re.sub(r'(^|[་ \n])(ཏུ|གི|ཀྱི|གིས|ཀྱིས|ཡིས|ཀྱང|སྟེ|ཏེ|མམ|རམ|སམ|ཏམ|ནོ|ཏོ|གིན|ཀྱིན|གྱིན|ཅིང|ཅིག|ཅེས|ཞེས)(?=$|[\n་])', lambda m: cutallgroups(m), srcstr)
    # cutting on the right:
    srcstr = re.sub(r'(^|[་ \n])((?:ཏུ|གི|ཀྱི|གིས|ཀྱིས|ཡིས|ཀྱང|སྟེ|ཏེ|མམ|རམ|སམ|ཏམ|ནོ|ཏོ|གིན|ཀྱིན|གྱིན|ཅིང|ཅིག|ཅེས|ཞེས)་)([^\n])', lambda m: cutallgroups(m), srcstr)

    # utterances should have their own lines
    srcstr = re.sub(r'([^\n])?(<utt>)([^\n])?', lambda m: cutallgroups(m), srcstr)

    srcstr = re.sub(r'<utt>\n([\s།༔]+<utt>)', r'\1', srcstr)
    # shrink multiple spaces into one
    srcstr = re.sub(r'[  \t]+', ' ', srcstr)

    # break between number and non-number
    srcstr = re.sub('([0-9])([^0-9\n])',r'\1\n\2',srcstr)

    # break between Tibetan number and non-number
    srcstr = re.sub('([༠-༳]་?)([^༠-༳\n])',r'\1\n\2',srcstr)
    srcstr = re.sub('([^༠-༳\n])([༠-༳])',r'\1\n\2',srcstr)

    # same with letters+tshek
    srcstr = re.sub('([ༀ་ཀ-\u0fbc])([^ༀ་ ཀ-\u0fbc\n])',r'\1\n\2',srcstr)
    srcstr = re.sub('([^ༀ་ ཀ-\u0fbc\n༠-༳])([ༀ་ཀ-\u0fbc])',r'\1\n\2',srcstr)

    srcstr = re.sub(r'(?:^|\n)[^\n]+་[^\n]+(?=$|\n)', lambda m: lexiconsegment(m.group(0)), srcstr)
    return srcstr    

def run_mbt(inputstr, settingsfile):
    """
    Runs mbt with the settings file and returns the output as a string
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, 'mbt-input.txt')
        with open(fname, 'w', encoding='utf-8') as temp:
            temp.write(inputstr)
        res = subprocess.check_output(['mbt', '-s', settingsfile, '-t', fname ])
        return res.decode('utf-8')

def format_seg_for_output(segstr):
    segstr = re.sub(r'([^>])\n',  r'\1 ', segstr)
    segstr = re.sub(r'[  \t]+', ' ', segstr)
    return segstr

def correctutts(posstr):
    posstr = re.sub(r'<utt>',r'',posstr) #delete all automatic <utt>\n before adding the following:
        #add <utt> after cv.fin + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin)\s?\n?',r'\1 <utt>',posstr)
        #add <utt> after cv.sem + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem)\s?\n?',r'\1 <utt>',posstr)
        #add <utt> after cv.ass + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass)\s?\n?',r'\1 <utt>',posstr)
        #add <utt> after cv.imp(f) + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.imp[f]?)\s?\n?',r'\1 <utt>',posstr)
        #add <utt> after cv.ques + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques)\s?\n?',r'\1 <utt>',posstr)
        #add <utt> after verbs + (double) shad
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc)\s?\n',r'\1 <utt>',posstr)

    posstr = re.sub(r'\s+',r' ',posstr)
    posstr = re.sub(r'\n+',r'',posstr)
    posstr = re.sub(r'<utt>',r'<utt>\n',posstr)
    return posstr

def createpyrrha(posstr):
    #Create Pyrrha input in columns
    posstr = re.sub(r'<utt>\n',r'<utt>\t<utt>\n\n',posstr)
    posstr = re.sub(r'//',r'/',posstr)
    posstr = re.sub(r'/([^\s]*) ',r'\t\1\n',posstr)
    posstr = re.sub(r'\%^',r'token\tPOS\n',posstr)
    return posstr

def main():
    parser = argparse.ArgumentParser(description='ACTIB Segmenter & POS Tagger')
    parser.add_argument('input-file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('output-file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('seg-output-file', nargs='?', type=argparse.FileType('w'), default=None)
    parser.add_argument('--input-format', nargs='?', choices=['txt','bdrc-tei'], default='txt')
    parser.add_argument('--pipeline', nargs='?', choices=['seg:pos','seg'], default='seg:pos')
    args = parser.parse_args()
    process(vars(args)['input-file'], vars(args)['output-file'], vars(args)['seg-output-file'], args.input_format, args.pipeline)

# segoutp is written to only in the case of seg:pos pipeline, it is otherwise ignored
# when using the seg pipeline, the segmented output goes to outp
def process(inp, pyrrhaoutp, posoutp, segoutp, input_format="txt", pipeline="seg:pos"):
    inputstr = inp.read()
    if input_format == 'bdrc-tei':
        inputstr = xmltocorpus(inputstr)
    else:
        inputstr = preprocess(inputstr)
    segstr = run_mbt(inputstr, 'conf/segmenting/segtrain.txt.settings')
    segstr = post_seg_processing_str(segstr)
    if pipeline == 'seg':
        segstr = format_seg_for_output(segstr)
        outp.write(segstr)
        return
    if segoutp is not None:
        segstr = format_seg_for_output(segstr)
        segoutp.write(segstr)
    posstr = run_mbt(segstr, 'conf/pos-tagging/TibTrain5.txt.settings')
    #posstr = run_mbt(segstr, 'conf/evaluation/TibTrain5trainsplit.txt.settings') #use this to test & evaluate the SOAS corpus
    ensureverbs()
    posstr = verblook(posstr, VERBS)
    posstr = forcedpos(posstr)
    posstr = verbcaselookup(posstr)
    posstr = correctutts(posstr)
    posoutp.write(posstr)
    posstr = createpyrrha(posstr)
    pyrrhaoutp.write(posstr)

def processtxtstr(inputstr, pipeline="seg:pos"):
    segstr = run_mbt(inputstr, 'conf/segmenting/segtrain.txt.settings')
    segstr = post_seg_processing_str(segstr)
    if pipeline == 'seg':
        segstr = format_seg_for_output(segstr)
        return segstr
    posstr = run_mbt(segstr, 'conf/pos-tagging/TibTrain5.txt.settings')
    ensureverbs()
    posstr = verblook(posstr, VERBS)
    posstr = forcedpos(posstr)
    posstr = verbcaselookup(posstr)
    return posstr

def processfiles(filename, segoutfilename, posoutfilename, pyrrhaoutfilename, pipeline="seg:pos", input_format="txt"):
    with open(segoutfilename, "w") as segoutp:
        with open(posoutfilename, "w") as posoutp:
            with open(pyrrhaoutfilename, "w") as pyrrhaoutp:
                with open(filename) as inp:
                    process(inp, pyrrhaoutp, posoutp, segoutp, input_format=input_format, pipeline=pipeline)    

def preprocesstest():
    xml_str = open("test/preprocess-bdrcxml.xml").read()
    xmlcorpus = xmltocorpus(xml_str)
    expected=open("test/preprocess-bdrcxml.expected.txt").read()
    print("error: output of xmlcorpus doesn't match expected output:")
    print(xmlcorpus)

def asserttest(srcstr,dststr):
    resstr = post_seg_processing_str(srcstr)
    if resstr != dststr:
        print("error: result of \"%s\" is \"%s\" instead of \"%s\"" % (srcstr, resstr, dststr))

def postsegtest():
    asserttest("གྱིས་/SS", "གྱིས་\n")
    asserttest("p17//X ༈//ES", "p17\n༈\n")
    asserttest("འོད་མ་འོན་", "འོད་མ་\nའོན་")
    asserttest("གྱིས/SS", "གྱིས\n")
    asserttest("ལེའུ་ཀྱིས་/S", "ལེའུ་\nཀྱིས་\n")
    asserttest("གཅིག་/S", "གཅིག་\n")
    asserttest("སེར་དང་/S", "སེར་\nདང་\n")
    asserttest("དགག་/X དབྱེ་/E དབྱར་/X དང་/S ཀོ་ln5//S", "དགག་དབྱེ་\nདབྱར་\nདང་\nཀོ་\nln5\n")
    asserttest("གཅིག/S", "གཅིག\n")
    asserttest("གཅིགས/S", "གཅིགས\n")
    asserttest("གཅིགས་/S", "གཅིགས་\n")
    asserttest("ཅིགས་/S", "ཅིགས་\n")
    asserttest("ཅིགས/S", "ཅིགས\n")
    asserttest("ལེའུ་ཅིག་ལེའུ", "ལེའུ་\nཅིག་\nལེའུ")
    asserttest("ལེའུ་ཅིག\n", "ལེའུ་\nཅིག\n")
    asserttest("ཅིག་ལེའུ\n", "ཅིག་\nལེའུ\n")
    asserttest("ལེའུའིའོ", "ལེའུ\nའི\nའོ")
    asserttest("འབྱོར་པའམ་རྒྱལ་", "འབྱོར་པ\nའམ་\nརྒྱལ་")
    asserttest("ལེའུ་འི་འོ་", "ལེའུ་\nའི་\nའོ་")
    #asserttest("ལེའུའི༔༔", "ལེའུ\nའི\n༔༔")
    asserttest("ལེའུ༢འ", "ལེའུ\n༢\nའ")
    asserttest("་ln", "་\nln")
    asserttest("་p", "་\np")
    asserttest("ལེའུ6", "ལེའུ\n6")
    asserttest("ལེའུ\u2468", "ལེའུ\n\u2468")
    asserttest("་\u232A", "་\n\u232A")
    asserttest("་<utt>༄", "་\n<utt>\n༄")
    asserttest("་ཏུ", "་\nཏུ")
    asserttest("ཀུན་ཏུ་བཟང", "ཀུན་\nཏུ་\nབཟང")
    asserttest("པར་/ES", "པ\nར་\n")
    asserttest("རིན་པོ་ཆེ་རིན་པོ་ཆེ་", "རིན་པོ་ཆེ་\nརིན་པོ་ཆེ་")
    asserttest("""༄༅/S །/S <utt>
།/S <utt>
རྒྱ་/X གར་/E སྐད་/S དུ/S །/S <utt>
རཱ་/X ཛ་/Y ནཱི་//Y ཏི་/Z ཤཱསྟྲ་//M བྷཱུ་//E མི་/S པཱ་/Y ལ་/E སྱ་//S ཨ་/X ལངྐཱ་//Y ར་/Z ནཱ་/Y མ/E །/S <utt>
བོད་/S སྐད་/S དུ/S །/S <utt>""", """༄༅
།
།
<utt>
རྒྱ་གར་
སྐད་
དུ
།
<utt>
རཱ་ཛ་
ནཱི་ཏི་ཤཱསྟྲ་
བྷཱུ་
མི་
པཱ་ལ་
སྱ་
ཨ་
ལངྐཱ་
ར་
ནཱ་མ
།
<utt>
བོད་
སྐད་
དུ
།
<utt>""")

def testverbcaserepl():
    orig = """འགྲོ་/v.fut.v.pres
ལ་/cv.all 
ཤཱཀྱ་སེང་གེ་/n.prop
ལ་/cv.all
ཤཱཀྱ་སེང་གེ་/n.prop
ལ་/case.all
འགྲོ་/v.fut.v.pres
ལ་/case.all
"""
    expected = """འགྲོ་/v.fut.v.pres 
ལ་/cv.all 
ཤཱཀྱ་སེང་གེ་/n.prop
ལ་/case.all
ཤཱཀྱ་སེང་གེ་/n.prop
ལ་/case.all
འགྲོ་/v.fut
ལ་/cv.all
"""
    res = verbcaselookup(orig)
    print("test passes: ", res==expected)

def testforcedpos():
    orig = """ཏ/test
དེ་ཏེ་/notcv.notsem
ཏེལ/notcv.notsem
ཏེ/notcv.notsem ཏེ/notcv.notsem ཏེ/notcv.notsem
ཏེ་/notcv.notsem
ལོ/notcv.notfin 
ཏུ/notcv.notterm 
ལོ/notcv.notfin 
ནས་/n.count
སྟོན་/v.pres ༣༨༥༣༨༥་//n.count པ་//n.count
《/n.count རྒྱལ་པོ/n.count 
།
"""
    expected = """ཏ/test
དེ་ཏེ་/notcv.notsem
ཏེལ/notcv.notsem
ཏེ/cv.sem ཏེ/cv.sem ཏེ/cv.sem
ཏེ་/cv.sem
ལོ/notcv.notfin 
ཏུ/cv.term 
ལོ/notcv.notfin 
ནས་/n.count
སྟོན་/v.pres ༣༨༥༣༨༥་//numeral པ་//n.count
《/punc རྒྱལ་པོ/n.count 
།
"""
    res = forcedpos(orig)
    print("test passes: ", res==expected)
    if res != expected:
        print("got ")
        print(res)

if __name__ == '__main__':
    #postsegtest()
    #testforcedpos()
    #preprocesstest()
    freeze_support()
    main()