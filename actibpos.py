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

VERBPAT = re.compile("([^/ ]+)/+[^ v]*v\.[^ ]+ ") #་this one isn't working!!! but the next one is :)
VERBCASEPAT = re.compile(r"/(?P<firsttag>[^\s]+\.)(?P<second>[^ \.]+\s+[^/ ]+/+)(?P<caseorcv>case|cv)\.")

def verbrepl(matchobj, VERBS):
    """ a function to be used in re.sub, replaces non-verbs tagged as verbs into n.count """
    entry = matchobj.group(1)
    if entry not in VERBS:
        return entry+'/n.count '
    else:
        return matchobj.group(0)

def verblook(posstr, VERBS):
    """
    Function takes two arguments (posstr, verbs), 
    and returns the output converting tags of Tibetan tokens that are tagged as verbs but don't occur in the verb lexicon
    to 'n.count' instead.
    """   
    posstr = re.sub(VERBPAT, lambda x: verbrepl(x,VERBS), posstr)
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

def forcedpos2(posstr):
    posstr = re.sub(r'(^|\s)([^\s]+)(//?)cl.quot\s([^\s]+)(//?)case.([^\s]+)\s', r'\1\2\3cl.quot \4\5cv.\6 ', posstr)
    posstr = re.sub(r'(^|\s)([^\s]+)(//?)adj\s([^\s]+)(//?)cv.([^\s]+)\s', r'\1\2\3adj \4\5case.\6 ', posstr)
    print(posstr)
    return posstr

def forcedpos(posstr):
    posstr = re.sub(r'(^|\s)((?:ཏེ|སྟེ)་?//?)([^\s]+)', r'\1\2cv.sem', posstr)
    posstr = re.sub(r'(^|\s)((?:p[0-9]+)//?)([^\s]+)', r'\1\2page.num', posstr)
    posstr = re.sub(r'(^|\s)((?:l[0-9]+)//?)([^\s]+)', r'\1\2line.num', posstr)
    posstr = re.sub(r'(^|\s)((?:[0-9༠-༳]+)་?//?)([^\s]+)', r'\1\2numeral', posstr)
    posstr = re.sub(r'(^|\s)((?:ཏུ|དུ)་?//?)([^\s]+)', r'\1\2cv.term', posstr)
    posstr = re.sub(r'(^|\s)((?:ནོ|རོ|ཏོ|འོ|དོ)་?//?)([^\s]+)', r'\1\2case.fin', posstr)
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*)\s((?:ནོ|རོ|ཏོ|འོ|དོ)་?//?)([^\s]+)', r'\1 \2cv.fin', posstr)
    posstr = re.sub(r'(^|\s)((?:ལོ|ངོ|གོ|སོ|མོ)་?//?)([^\s]+)\s།', r'\1 \2case.fin །', posstr)
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*)\s((?:ལོ|ངོ|མོ|གོ|སོ|མོ|སོ)་?//?)([^\s]+)\s།', r'\1 \2cv.fin །', posstr)
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*)\s((?:ལོ|ངོ|མོ|གོ|སོ|མོ|སོ)་?//?)([^\s]+)\s', r'\1 \2cv.fin ', posstr)
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*)\s((?:ཞིང|ཅིང|ཤིང)་?//?)([^\s]+)\s།', r'\1 \2cv.impf །', posstr)
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*)\s((?:ཞིང|ཅིང|ཤིང)་?//?)([^\s]+)\s', r'\1 \2cv.impf ', posstr)
    posstr = re.sub(r'(^|\s)((?:《|》|༈|༼|༽|༏|༑|༐|༒)//?)([^\s]+)', r'\1\2punc', posstr)
    #posstr = re.sub(r'(^|\s)((?:གང|མཆོག)་?//?)([^\s]+)', r'\1\2adj', posstr) #new SOAS pos corrections starting here
    posstr = re.sub(r'(^|\s)((?:འམ)་?//?)([^\s]+)', r'\1\2cv.ques', posstr)
    posstr = re.sub(r'(^|\s)((?:ཐག)་?//?)([^\s]+)', r'\1\2v.invar.thag', posstr)
    posstr = re.sub(r'(^|\s)((?:ཐག་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.thag', posstr)
    posstr = re.sub(r'(^|\s)((?:དགོས)་?//?)([^\s]+)', r'\1\2v.invar.dgos', posstr)
    posstr = re.sub(r'(^|\s)((?:དགོས་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.dgos', posstr)
    posstr = re.sub(r'(^|\s)((?:ནུས)་?//?)([^\s]+)', r'\1\2v.invar.nus', posstr)
    posstr = re.sub(r'(^|\s)((?:ནུས་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.nus', posstr)
    posstr = re.sub(r'(^|\s)((?:མོད)་?//?)([^\s]+)', r'\1\2v.invar.mod', posstr)
    posstr = re.sub(r'(^|\s)((?:མོད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.mod', posstr)
    posstr = re.sub(r'(^|\s)((?:འདོད)་?//?)([^\s]+)', r'\1\2v.invar.dod', posstr)
    posstr = re.sub(r'(^|\s)((?:འདོད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.dod', posstr)
    posstr = re.sub(r'(^|\s)((?:སྲིད)་?//?)([^\s]+)', r'\1\2v.invar.srid', posstr)
    posstr = re.sub(r'(^|\s)((?:སྲིད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.srid', posstr)
    posstr = re.sub(r'(^|\s)((?:ཤེས)་?//?)([^\s]+)', r'\1\2v.invar.shes', posstr)
    posstr = re.sub(r'(^|\s)((?:ཤེས་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.shes', posstr)
    posstr = re.sub(r'(^|\s)((?:རན)་?//?)([^\s]+)', r'\1\2v.invar.ran', posstr)
    posstr = re.sub(r'(^|\s)((?:རན་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.ran', posstr)
    posstr = re.sub(r'(^|\s)((?:རན)་?//?)([^\s]+)(\s(?:དོ)་?/cv.fin)', r'\1\2v.past.ran\4', posstr) #rule with sandhi and དོ as cv.fin
    posstr = re.sub(r'(^|\s)((?:རནད)་?//?)([^\s]+)', r'\1\2v.past.ran', posstr)
    posstr = re.sub(r'(^|\s)((?:རནད་པ)་?//?)([^\s]+)', r'\1\2n.v.past.ran', posstr)
    posstr = re.sub(r'(^|\s)((?:གྲགས)་?//?)([^\s]+)', r'\1\2v.invar.grags', posstr)
    posstr = re.sub(r'(^|\s)((?:གྲགས་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.grags', posstr)
    posstr = re.sub(r'(^|\s)((?:འཕོད)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.phod', posstr)
    posstr = re.sub(r'(^|\s)((?:འཕོད་པ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.phod', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕོད)་?//?)([^\s]+)', r'\1\2v.past.phod', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕོད་པ)་?//?)([^\s]+)', r'\1\2n.v.past.phod', posstr)
    posstr = re.sub(r'(^|\s)((?:ཆོག)་?//?)([^\s]+)', r'\1\2v.invar.chog', posstr)
    posstr = re.sub(r'(^|\s)((?:ཆོག་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.chog', posstr)
    posstr = re.sub(r'(^|\s)((?:ཐང)་?//?)([^\s]+)', r'\1\2v.invar.thang', posstr)
    posstr = re.sub(r'(^|\s)((?:ཐང་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.thang', posstr)
    posstr = re.sub(r'(^|\s)((?:མྱངས)་?//?)([^\s]+)', r'\1\2v.past.myong1', posstr)
    posstr = re.sub(r'(^|\s)((?:མྱངས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.myong1', posstr)
    posstr = re.sub(r'(^|\s)((?:མྱང)་?//?)([^\s]+)', r'\1\2v.fut.myong1', posstr)
    posstr = re.sub(r'(^|\s)((?:མྱང་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.myong1', posstr)
    posstr = re.sub(r'(^|\s)((?:དཀའ)་?//?)([^\s]+)', r'\1\2v.invar.dka', posstr)
    posstr = re.sub(r'(^|\s)((?:དཀའ་བ)་?//?)([^\s]+)', r'\1\2n.v.invar.dka', posstr)
    posstr = re.sub(r'(^|\s)((?:བཏུབ)་?//?)([^\s]+)', r'\1\2v.invar.thub1', posstr)
    posstr = re.sub(r'(^|\s)((?:བཏུབ་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.thub1', posstr)
    posstr = re.sub(r'(^|\s)((?:བཏུབས)་?//?)([^\s]+)', r'\1\2v.past.thub1', posstr)
    posstr = re.sub(r'(^|\s)((?:བཏུབས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.thub1', posstr)
    posstr = re.sub(r'(^|\s)((?:འདུག)་?//?)([^\s]+)', r'\1\2v.invar.dug', posstr)
    posstr = re.sub(r'(^|\s)((?:འདུག་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.dug', posstr)
    posstr = re.sub(r'(^|\s)((?:གདའ)་?//?)([^\s]+)', r'\1\2v.invar.gda', posstr)
    posstr = re.sub(r'(^|\s)((?:གདའ་བ)་?//?)([^\s]+)', r'\1\2n.v.invar.gda', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡོད)་?//?)([^\s]+)', r'\1\2v.invar.yod', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡོད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.yod', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིན)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.yin', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིན་པ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.yin', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིན་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.yin', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིན)་?//?)([^\s]+)(\s(?:དོ)་?/cv.fin)', r'\1\2v.past.yin\4', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིནད)་?//?)([^\s]+)', r'\1\2v.past.yin', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིནད་པ)་?//?)([^\s]+)', r'\1\2n.v.past.yin', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྱུར)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྱུར་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:བསྒྱུར)་?//?)([^\s]+)', r'\1\2v.fut.v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:བསྒྱུར་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:གྱུར)་?//?)([^\s]+)', r'\1\2v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:གྱུར་བ)་?//?)([^\s]+)', r'\1\2n.v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:གྱུརད)་?//?)([^\s]+)', r'\1\2v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:གྱུརད་བ)་?//?)([^\s]+)', r'\1\2n.v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:བསྒྱུརད)་?//?)([^\s]+)', r'\1\2v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:བསྒྱུརད་བ)་?//?)([^\s]+)', r'\1\2n.v.past.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྱུརད)་?//?)([^\s]+)', r'\1\2v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྱུརད་བ)་?//?)([^\s]+)', r'\1\2n.v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:སྒྱུར)་?//?)([^\s]+)', r'\1\2v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:སྒྱུར་བ)་?//?)([^\s]+)', r'\1\2n.v.pres.gyur', posstr)
    posstr = re.sub(r'(^|\s)((?:འབྱུང)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.byung', posstr)
    posstr = re.sub(r'(^|\s)((?:འབྱུང་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.byung', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱུང)་?//?)([^\s]+)', r'\1\2v.past.byung', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱུང་བ)་?//?)([^\s]+)', r'\1\2n.v.past.byung', posstr)
    posstr = re.sub(r'(^|\s)((?:ལགས)་?//?)([^\s]+)', r'\1\2v.invar.lags', posstr)
    posstr = re.sub(r'(^|\s)((?:ལགས་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.lags', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱེད)་?//?)([^\s]+)', r'\1\2v.pres.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱེད་པ)་?//?)([^\s]+)', r'\1\2n.v.pres.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱས)་?//?)([^\s]+)', r'\1\2v.past.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱ)་?//?)([^\s]+)', r'\1\2v.fut.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱ་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱོ)་?//?)([^\s]+)', r'\1\2v.ipv.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱོ་བ)་?//?)([^\s]+)', r'\1\2n.v.ipv.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱོས)་?//?)([^\s]+)', r'\1\2v.ipv.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:བྱོས་པ)་?//?)([^\s]+)', r'\1\2n.v.ipv.byed', posstr)
    posstr = re.sub(r'(^|\s)((?:ཤོག)་?//?)([^\s]+)', r'\1\2v.invar.shog', posstr)
    posstr = re.sub(r'(^|\s)((?:ཤོག་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.shog', posstr)
    posstr = re.sub(r'(^|\s)((?:ཤོག)་?//?)([^\s]+)(\s(?:ཅིག)་?/cv.ipv)', r'\1\2v.ipv.ong\4', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡོང)་?//?)([^\s]+)', r'\1\2v.invar.yong', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡོང་བ)་?//?)([^\s]+)', r'\1\2n.v.invar.yong', posstr)
    posstr = re.sub(r'(^|\s)((?:ཡིན་ལུགས)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.yinlugs', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྲོ)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:འགྲོ་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:སོང)་?//?)([^\s]+)', r'\1\2v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:སོང་བ)་?//?)([^\s]+)', r'\1\2n.v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕྱིན)་?//?)([^\s]+)', r'\1\2v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕྱིན་པ)་?//?)([^\s]+)', r'\1\2n.v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕྱིནད)་?//?)([^\s]+)', r'\1\2v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:ཕྱིནད་པ)་?//?)([^\s]+)', r'\1\2n.v.past.gro', posstr)
    posstr = re.sub(r'(^|\s)((?:མཛད)་?//?)([^\s]+)', r'\1\2v.invar.mdzad', posstr)
    posstr = re.sub(r'(^|\s)((?:མཛད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.mdzad', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱིད)་?//?)([^\s]+)', r'\1\2v.pres.bgyid', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱིད་པ)་?//?)([^\s]+)', r'\1\2n.v.pres.bgyid', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱིས)་?//?)([^\s]+)', r'\1\2v.past.bgyid', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱིས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.bgyid', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱི)་?//?)([^\s]+)', r'\1\2v.fut.bgyid', posstr)
    posstr = re.sub(r'(^|\s)((?:བགྱི་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.bgyid', posstr)


    posstr = re.sub(r'(^|\s)((?:གྱིས)་?//?)([^\s]+)(\s(?:ཤིག)་?/cv.fin)', r'\1\2v.past.min\4', posstr) #rules for གྱིས as special verb and not cases

    posstr = re.sub(r'(^|\s)((?:འོང)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.ong', posstr)
    posstr = re.sub(r'(^|\s)((?:འོང་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.ong', posstr)
    posstr = re.sub(r'(^|\s)((?:འོངས)་?//?)([^\s]+)', r'\1\2v.past.ong', posstr)
    posstr = re.sub(r'(^|\s)((?:འོངས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.ong', posstr)
    posstr = re.sub(r'(^|\s)((?:མེད)་?//?)([^\s]+)', r'\1\2v.invar.med', posstr)
    posstr = re.sub(r'(^|\s)((?:མེད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.med', posstr)
    posstr = re.sub(r'(^|\s)((?:མིན)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.min', posstr)
    posstr = re.sub(r'(^|\s)((?:མིན་པ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.min', posstr)
    posstr = re.sub(r'(^|\s)((?:མིན)་?//?)([^\s]+)(\s(?:དོ)་?/cv.fin)', r'\1\2v.past.min\4', posstr)
    posstr = re.sub(r'(^|\s)((?:མིནད)་?//?)([^\s]+)', r'\1\2v.past.min', posstr)
    posstr = re.sub(r'(^|\s)((?:མིནད་པ)་?//?)([^\s]+)', r'\1\2n.v.past.min', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲས)་?//?)([^\s]+)', r'\1\2v.past.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲས་བ)་?//?)([^\s]+)', r'\1\2n.v.past.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲ)་?//?)([^\s]+)', r'\1\2v.fut.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲ་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲོས)་?//?)([^\s]+)', r'\1\2v.ipv.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲོས་པ)་?//?)([^\s]+)', r'\1\2n.v.ipv.dra1', posstr)
    posstr = re.sub(r'(^|\s)((?:འཚལད)་?//?)([^\s]+)', r'\1\2v.past.tshal1', posstr)
    posstr = re.sub(r'(^|\s)((?:འཚལད་བ)་?//?)([^\s]+)', r'\1\2n.v.past.tshal1', posstr)
    posstr = re.sub(r'(^|\s)((?:བཙལ)་?//?)([^\s]+)', r'\1\2v.fut.v.past.tshal1', posstr)
    posstr = re.sub(r'(^|\s)((?:བཙལ་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.past.tshal1', posstr)
    posstr = re.sub(r'(^|\s)((?:འཚལ)་?//?)([^\s]+)(\s(?:དོ)་?/cv.fin)', r'\1\2v.past.tshal1\4', posstr)
    posstr = re.sub(r'(^|\s)((?:མཆི)་?//?)([^\s]+)', r'\1\2v.fut.v.pres.mchi', posstr)
    posstr = re.sub(r'(^|\s)((?:མཆི་བ)་?//?)([^\s]+)', r'\1\2n.v.fut.n.v.pres.mchi', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲག)་?//?)([^\s]+)', r'\1\2v.invar.drag', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲག་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.drag', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲགས)་?//?)([^\s]+)', r'\1\2v.past.drag', posstr)
    posstr = re.sub(r'(^|\s)((?:དྲགས་པ)་?//?)([^\s]+)', r'\1\2n.v.past.drag', posstr)
    posstr = re.sub(r'(^|\s)((?:རེད)་?//?)([^\s]+)', r'\1\2v.invar.red', posstr)
    posstr = re.sub(r'(^|\s)((?:རེད་པ)་?//?)([^\s]+)', r'\1\2n.v.invar.red', posstr)
    posstr = re.sub(r'(^|\s)((?:རེད་བ)་?//?)([^\s]+)', r'\1\2n.v.invar.red', posstr)
    posstr = re.sub(r'(^|\s)((?:བཞག)་?//?)([^\s]+)', r'\1\2v.past.bzhag', posstr)
    posstr = re.sub(r'(^|\s)((?:བཞག་པ)་?//?)([^\s]+)', r'\1\2n.v.past.bzhag', posstr)
    posstr = re.sub(r'(^|\s)((?:རྒྱུ)་?//?)([^\s]+)', r'\1\2v.invar.rgyu', posstr)
    posstr = re.sub(r'(^|\s)((?:རྒྱུ་བ)་?//?)([^\s]+)', r'\1\2n.v.invar.rgyu', posstr)
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
    # cutting on the right: (leaving out ཞེས & ཅེས because we like to have ཞེས་པ་ as one word - note 6 June 2023)
    srcstr = re.sub(r'(^|[་ \n])((?:ཏུ|གི|ཀྱི|གིས|ཀྱིས|ཡིས|ཀྱང|སྟེ|ཏེ|མམ|རམ|སམ|ཏམ|ནོ|ཏོ|གིན|ཀྱིན|གྱིན|ཅིང|ཅིག)་)([^\n])', lambda m: cutallgroups(m), srcstr)

    # utterances should have their own lines
    srcstr = re.sub(r'([^\n])?(<utt>)([^\n])?', lambda m: cutallgroups(m), srcstr)

    srcstr = re.sub(r'<utt>\n([\s།༔༑]+<utt>)', r'\1', srcstr)
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
    # delete utt and \n
    posstr = re.sub(r'<utt>',r'',posstr) #delete all automatic <utt>\n before adding the following:
    posstr = re.sub(r'\n',r'',posstr) #delete all \n before adding the following:
    #posstr = re.sub(r'\n',r' ',posstr) #delete all \n before adding the following:

    #add <utt> after cv.fin
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc)(?!\s།/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.fin)(?!\s།/punc)',r'\1 <utt>',posstr)

    #add <utt> after case.nare
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare [།༔]/punc)(?!\s།/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/case\.nare)(?!\s།/punc)',r'\1 <utt>',posstr)

    #add <utt> after cv.ass + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc)(?!\s།/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ass)(?!\s།/punc)',r'\1 <utt>',posstr)

    # add <utt> after case.ass if it's following a verbal noun (this means merging sentences with verbal nouns that are names etc.)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\sདང་?/case\.ass །/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\sདང་?/case\.ass ༔/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\sདང་?/case\.ass)(?!\s།/punc)',r'\1 <utt>',posstr)

    #add <utt> after cv.ipv + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv [།༔]/punc)(?!\s།/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ipv)(?!\s།/punc)',r'\1 <utt>',posstr)

    # add <utt> after case.ipv if it's following a verbal noun (this means merging sentences with verbal nouns that are names etc.)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ipv །/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ipv ༔/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ipv)(?!\s།/punc)',r'\1 <utt>',posstr)

    # add <utt> after verbs + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\sp[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\sln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\s[།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\s[།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\s[།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?v\.[^\s]*\s[།༔]/punc <utt> [།༔]/punc)',r'\1 <utt>',posstr) #this doesn't prevent it from going wrong later
    posstr = re.sub(r'([ༀ-࿘]//?v\.[^\s]*\s[།༔]/punc)', r'\1 <utt>',posstr)

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
    posstr = re.sub(r'([ༀ-࿘]*/cv\.sem)(?!\s།/punc)',r'\1 <utt>',posstr)

    # remove <utt> after cv.sem if it is followed by a single verb and one of the following cv's (ie. subordinating conjunctions)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.loc\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.gen\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.term\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.rung\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.odd\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.all\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.agn\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.ela\s)',r'\1 \2',posstr)
    posstr = re.sub(r'(cv\.sem\s)<utt>\s([ༀ-࿘]*//?v\.[^\s]*\s[ༀ-࿘]*//?cv\.cont\s)',r'\1 \2',posstr)

    #add <utt> after cv.ques + (double) shad
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc [།༔]/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc)(?!\s།/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*/cv\.ques)(?!\s།/punc)',r'\1 <utt>',posstr)

    # add <utt> after case.ques if it's following a verbal noun (this means merging sentences with verbal nouns that are names etc.)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ques །/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ques ༔/punc)',r'\1 <utt>',posstr)
    posstr = re.sub(r'([ༀ-࿘]*//?n\.v\.[^\s]*\s[ༀ-࿘]*་?/case\.ques)(?!\s།/punc)',r'\1 <utt>',posstr)

    #     #add <utt> after verbs + (double) shad
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',posstr)
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',posstr)
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',posstr)
    # posstr = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc)\s?\n',r'\1 <utt>',posstr)

    #remove <utt> in between double shad
    posstr = re.sub(r'([།༔]/punc)\s<utt>(\s?[།༔]/punc)',r'\1 \2',posstr)
    posstr = re.sub(r'\s+',r' ',posstr)
    posstr = re.sub(r'\n+',r'',posstr)
    posstr = re.sub(r'<utt> ',r'<utt>\n',posstr)#capture <utt> + space to ensure no space at start of the line
    #print(posstr)
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
    if segoutp is not None:
        segstr = format_seg_for_output(segstr)
        segoutp.write(segstr)
    if pipeline == 'seg':
        return
    posstr = run_mbt(segstr, 'conf/pos-tagging/TibTrain5.txt.settings')
    #posstr = run_mbt(segstr, 'conf/evaluation/TibTrain5trainsplit.txt.settings') #use this to test & evaluate the SOAS corpus
    ensureverbs()
    posstr = verblook(posstr, VERBS)
    posstr = forcedpos(posstr)
    posstr = verbcaselookup(posstr)
    posstr = forcedpos2(posstr)
    posstr = correctutts(posstr)
#    print(posstr)
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
    posstr = forcedpos2(posstr)
    print(posstr)
    return posstr

def processfiles(filename, segoutfilename, posoutfilename, pyrrhaoutfilename, pipeline="seg:pos", input_format="txt"):
    with open(segoutfilename, "w") as segoutp:
        with open(filename) as inp:
            if posoutfilename is None:
                try:
                    process(inp, None, None, segoutp, input_format=input_format, pipeline=pipeline)
                except Exception as e:
                    print(e)
                return
            with open(posoutfilename, "w") as posoutp:
                with open(pyrrhaoutfilename, "w") as pyrrhaoutp:
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