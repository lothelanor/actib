import nltk
import argparse
import re
import pprint
import sys
import os
from pathlib import Path

#Note that this OLD grammar was the one designed in 2019.
grammarOLD = r"""
    LineP: {<line.num>}
    PageP: {<page.num>}
    NP: {<n.count|n.mass>}
    NUMP: {<num.card|numeral>}
    ADJP: {<adj|num.ord>}
    DP: {<d.dem|d.det|d.emph|d.emph|d.plural|d.tsam>?<NP><LineP>?<PageP>?<NP>?<skt|p.indef|p.interrog|p.pers|p.refl|n.prop>?<ADJP>?<ADJP>?<ADJP>?<d.dem|d.det|d.emph|d.emph|d.plural|d.tsam>?}
    DP: {<DP><LineP>?<PageP>?<case.gen><LineP>?<PageP>?<DP>}
    SubjDP: {<NP|DP><LineP>?<PageP>?<case.agn>}
    P: {<case.gen><LineP>?<PageP>?<n.rel><LineP>?<PageP>?<case.term|case.loc|case.all>}
    PP: {<DP|ADJP><LineP>?<PageP>?<P|case.term|case.ela|case.loc|case.abl|case.ass|case.all|case.nare|case.comp>}
    PP: {<NP|DP><case.gen><n.rel><case.term>}
    VNP: {<n.v.cop|v.cop|v.cop.neg>?<n.v.cop|v.cop|v.cop.neg|cl.quot|cl.quot|n.v.aux|n.v.fut|n.v.fut.n.v.past|n.v.fut.n.v.pres|n.v.imp|n.v.invar|n.v.neg|n.v.past|n.v.past.n.v.pres|n.v.pres>}
    VP: {<v.aux|v.fut|v.fut.v.past|v.fut.v.pres|v.imp|v.invar|v.neg|v.past|v.past.v.pres|v.pres>}
    bigVP: {<VP><LineP>?<PageP>?<VP>}
    NEGP: {<neg>}
    ADVP: {<adv.dir|adv.intense|adv.mim|adv.proclausal|adv.temp>}
    """

#This is the NEW grammar updated in 2021. All in NLTK chunkparsing format.
#Grammar designed to be looped through multiple times if necessary (2 = default).
grammar = r"""
    CODEP: {<line.num>} #because CODE nodes can be ignored by Cesax
    CODEP: {<page.num>} 
    ID: {<ID>}
    EDIT: {<edit>}
    QP: {<d.plural|d.det>} #because I do not get why these are not quantifiers
    ADVP: {<adj|d.plural|n.rel><CODEP>?<case.term>}
    ADVP: {<adv|adv.dir|n.temp|adv.mim|adv.proclausal|adv.intense|adv.temp>}
    ADJP: {<adj><CODEP>?<adj|ADVP|num.ord>?<adj|ADVP|num.ord>?}
    NEGP: {<neg>} #because we want all heads to project
    NUMP: {<numeral|num.card>} #num.ord is with the adjectives
    NVP: {<n.v.aux|n.v.cop|n.v.fut|n.v.fut.n.v.past|n.v.fut.n.v.pres|n.v.imp|n.v.invar|n.v.neg|n.v.past|n.v.past.n.v.pres|n.v.pres><ADJP|NUMP>?<d.plural|d.det|d.dem|d.emph|d.indef|d.tsam>?}
    NP: {<n.count|n.mass|d.dem><CODEP>?<ADJP|NUMP>?<CODEP>?<QP|d.plural|d.det|d.dem|d.emph|d.indef|d.tsam>?}
    NP-PRO: {<p.indef|p.interrog|p.pers|p.refl><d.plural>?}
    VP: {<v.aux|v.cop|v.cop.neg|v.fut|v.fut.v.past|v.fut.v.pres|v.imp|v.invar|v.neg|v.past|v.past.v.pres|v.pres>}
    CP-SUB: {<VP><CODEP>?<cv.abl|cv.all|cv.gen|cv.are|cv.ass|cv.cont|cv.ela|cv.loc|cv.sem|cv.term><punc>?}
    CP-REL: {<NVP><CODEP>?<case.gen>}
    NP: {<NP><case.gen><CODEP>?<NP|NVP>}
    NP: {<NP><CODEP>?<n.rel><CODEP>?<case.gen><CODEP>?<NP>}
    NP-NPR: {<n.prop><CODEP>?<case.gen><CODEP>?<n.son>}
    NP-NPR: {<n.prop>}
    NP-WH: {<p.interrog>}
    NP-SBJ: {<NP|NVP|NP-PRO|NP-NPR><CODEP>?<case.agn>}
    NP-TOP: {<NP|NVP|NP-PRO|NP-NPR|NP-SBJ><CODEP>?<cl.top>}
    NP-FOC: {<NP|NVP|NP-NPR|NP-SBJ><CODEP>?<cl.focus>}
    PP: {<NP|NVP|NP-PRO><CODEP>?<case.abl|case.all|case.ela|case.loc|case.term>}
    NP-CONJ: {<NP|NVP><CODEP>?<case.ass>}
    """

def main():
    parser = argparse.ArgumentParser(description='Parser')
    parser.add_argument('input-file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('output-file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()
    line = vars(args)['input-file'].readline()
    textID = Path(sys.argv[1]).stem
#    source_file = open('%s'  % file ,encoding='utf-8')
    corpus = []
#    line = source_file.readline()
    linenumber = 0

    #while loop through all lines in source_file to do all replacements
    while line:
        linenumber = linenumber+1
        #NOTE for python3.9 % no longer works so we need .format()
        line = re.sub("<utt>",textID + "_l{}/ID <utt>".format(linenumber),line) #add sentence IDs
        #print(line)   #to troubleshoot: with this you can see in the Terminal at which line it goes wrong.         
        #line = '%s\n' % (line) #if you need line breaks
        corpus.append(line)   
        line = vars(args)['input-file'].readline()

    #convert corpus list to string to write in output file
    outputcorpus = ''.join(corpus)
    #make input nltk readable
    text = make_nltk_readable(outputcorpus)
    #Train chunkparser on grammar (loop=2 to get embedded structure)
    cp = nltk.RegexpParser(grammar)
    #print(grammar) optional print of the grammar
    results = []
    i = 0
    for t in text:
        result = cp.parse(t)
        #print(t)
        result = result.pformat()
        result += '\n'
        #testing the postprocessing to prepare for Cesax input:
        result = re.sub('( [^\s]*)/([aA-zZ\.]+)',r' (\2\1)',result)
#        vars(args)['output-file'].write(result) #this can be used if you want a different name for your output file
        i += 1
        #print(i)
        results += result
    
    outputcorpus = ''.join(results)
    output_file = open('%s.psd' % (textID), 'w', encoding='utf-8') 
    output_file.write(outputcorpus)
    output_file.close()

def make_nltk_readable(all_text):
    """
        function takes one argument (all_text), and returns a list
        containing (for every sentence) a list of word-pos pairs
    """
    corpus = []
    i = 0
    for line in all_text.splitlines():
        sentence = []
        pairstrings = re.split(r"\s", line)
        # splits je regel in woord-pos-paar-strings WPPS
        # haal de laatste eraf
        for p in pairstrings:
            sentence.append(tuple(re.split(r"\/{1,2}", p)))
        # voor iedere WPPS, splits 'm in woord en pos en voeg toe aan de zin
        #print sentence
        sentence = sentence[:-1] #-2 if you want to cut of sentenceIDs
        i += 1
        #print(i)
        corpus.append(sentence) # voeg de zin toe aan het corpus
    return corpus

#TROUBLESHOOT:

#>>>for t in text:
#...    results = cp.parse(t)
#...    results
#(enter, enter) so it prints in terminal until the error

main()
