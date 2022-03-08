#!/usr/bin/env python
import re
import sys
import os
import glob
import time
from subprocess import call
from pathlib import Path
import shutil

def main():
    """
    Main function that goes into the directory that you enter as the main argument
    and reads all names of subdirectories and their *.txt files.
    It corrects sentence boundaries and creates Pyrrha (i.e. UD connl-U) output.
    Note this script works for texts that have <utt> information to indicate sentence boundaries already. 
    Add <utt> with RegExs if necessary based on full stops. (for scraped versions)
    In the right folder, call 'python3 SentSeg.py 'directory_name'.
    """
    dir_name = sys.argv[1]        
    os.chdir('%s' % dir_name)
    timestamp = re.sub('[^A-Za-z0-9]','_', time.strftime('%c', time.gmtime()))
    out_dir_name = 'out_%s_%s' % (dir_name, timestamp)
    call(['mkdir', out_dir_name ])
    
    for file in glob.glob("*.txt"):
        
        correctutts(file,out_dir_name)
    
def correctutts(file, out_dir_name):    
    """
    Function that takes four arguments: 
    - input file
    - output file in 'w'
    - subfolder_name 
    - basename of files
    It removes awkward chars and adds SentenceIDs with
    - the date from the subfolder
    - the txtID from the basename
    - the accumulative line number
    It returns the new corpus as a str.
    """
    source_file = open('%s'  % file)
    corpus = []
    line = source_file.readline()

    #while loop through all lines in source_file to do all replacements
    while line:

    
        line = re.sub(r'<utt>',r'',line) #delete all automatic <utt>\n before adding the following:
        #add <utt> after cv.fin + (double) shad
        line = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin)\s?\n?',r'\1 <utt>',line)
        #add <utt> after cv.sem + (double) shad
        line = re.sub(r'([ༀ-࿘]*/cv\.sem p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.sem)\s?\n?',r'\1 <utt>',line)
        #add <utt> after cv.ass + (double) shad
        line = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ass)\s?\n?',r'\1 <utt>',line)
        #add <utt> after cv.imp(f) + (double) shad
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]? [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.imp[f]?)\s?\n?',r'\1 <utt>',line)
        #add <utt> after cv.ques + (double) shad
        line = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques p[0-9]*/page\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques ln[0-9]*/line\.num [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.ques)\s?\n?',r'\1 <utt>',line)
        #add <utt> after verbs + (double) shad
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc [།༔]/punc)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc p[0-9]*/page\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc ln[0-9]*/line\.num)\s?\n?',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc)\s?\n',r'\1 <utt>',line)

        line = re.sub(r'\s+',r' ',line)
        line = re.sub(r'\n+',r'',line)
        line = re.sub(r'<utt>',r'<utt>\n',line)

        #Create Pyrrha input in columns
        line = re.sub(r'<utt>\n',r'<utt>\t<utt>\n\n',line)
        line = re.sub(r'//',r'/',line)
        line = re.sub(r'/([^\s]*) ',r'\t\1\n',line)
        line = re.sub(r'\%^',r'token\tPOS\n',line)

        print(line)   #to troubleshoot: with this you can see in the Terminal at which line it goes wrong.         
        #line = '%s\n' % (line) #if you need line breaks
        corpus.append(line)   
        line = source_file.readline()
        
    #convert corpus list to string to write in output file
    outputcorpus = ''.join(corpus)        
        
        
    #write corpus to file
    file = re.sub('.txt','',file)
    output_file = open('%s/%s_CorrectUtt.txt' % (out_dir_name,file), 'w') 
    #xmloutput_file = codecs.open('%s_out.txt' % (xml_file), 'w', encoding='utf-8') 
    output_file.write(outputcorpus)
    output_file.close()
  

"""
Executing main function (so that it works as a script directly from the terminal; not just in shell interpreter)
"""

if __name__ == "__main__":
    main()