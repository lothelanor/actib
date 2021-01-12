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
    It corrects sentence boundaries.
    Note this script works for texts that have <utt> information to indicate sentence boundaries already. Add <utt> with RegExs if necessary based on full stops. (for scraped versions)
    In the right folder, call 'python3 CorrectUtts.py 'directory_name'.
    Note that currently, this script additionally corrects a number of tagging errors.
    """
    if len(sys.argv) < 2:
        print("error: you must pass a directory as argument to the script")
        sys.exit(1)

    dst_dir_name = "AllOutput"
    if len(sys.argv) > 2:
        dst_dir_name = sys.argv[2]

    print("write files in "+dst_dir_name)

    src_dir_name = sys.argv[1]
    src_dir = Path(src_dir_name)

    dst_dir = Path(dst_dir_name)
    dst_dir.mkdir(parents=True, exist_ok=True)

    list_subfolders_with_paths = [f.path for f in os.scandir(src_dir) if f.is_dir()]

    for subfolder_name in list_subfolders_with_paths:
        subfolder = Path(subfolder_name)
        filenames = subfolder.rglob('*.txt')

        for filename in sorted(filenames, key=lambda fn: str(fn)):
            basename = os.path.basename(filename)
            if basename.startswith("_"):
                continue
            noext = os.path.splitext(basename)[0]
            #IDoutputfilename = os.path.join(subfolder_name, noext+".txt")
            outpath = dst_dir/Path("output"+subfolder.stem) #use this one when testing
            #outpath = dst_dir/Path(subfolder.stem)
            outpath.mkdir(parents=True, exist_ok=True)
            IDoutputfilename = os.path.join(outpath, noext+".txt")

            with open(IDoutputfilename, "w") as outp:
                with open(filename) as inp:
                    corpus = correctutts(inp,outp,subfolder_name,basename)  
                    outp.write(corpus)

def correctutts(inp, outp, subfolder_name, basename):    
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

    # reads the file and creates lines:
    line = inp.readline() #must use 'readline' ipv 'read' or else %s won't work!
    
    corpus = []
    dir_years = Path(subfolder_name).stem
    #print(dir_years)
    filename = basename.rsplit('.', 1)[0]
    print(filename)

    linenumber = 0
    editionnumber = 0 #only if there are editions
    folionumber = 0 #not currently implemented, but pages are tagged 'page.num'
    
    while line:

        linenumber = linenumber + 1
        folionumber = folionumber + 1
        editionnumber = editionnumber + 1
        
        #fix utterance boundaries with page/line numbers
        line = re.sub(r'<utt>',r'',line) #delete all automatic <utt>\n before adding the following:
        line = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num [།༔]/punc)\s?\n',r'\1 <utt>',line)    
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin p[0-9]*/page\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc p[0-9]*/page\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) p[0-9]*/page\.num [ༀ-࿘]*/cv\.ass [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass p[0-9]*/page\.num [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass [།༔]/punc p[0-9]*/page\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) p[0-9]*/page\.num [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc p[0-9]*/page\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([།༔]/punc p[0-9]*/page\.num [།༔]/punc )\n',r'\1 <utt>',line)
        line = re.sub(r'([།༔]/punc [།༔]/punc p[0-9]*/page\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([།༔]/punc [།༔]/punc)\s?\n',r'\1 <utt>',line)

        line = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num [།༔]/punc)\s?\n',r'\1 <utt>',line)    
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin ln[0-9]*/line\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([ༀ-࿘]*/cv\.fin [།༔]/punc ln[0-9]*/line\.num)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) ln[0-9]*/line\.num [ༀ-࿘]*/cv\.ass [།༔]/punc) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass ln[0-9]*/line\.num [།༔]/punc) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass [།༔]/punc ln[0-9]*/line\.num) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [ༀ-࿘]*/cv\.ass [།༔]/punc) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) ln[0-9]*/line\.num [།༔]/punc) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc ln[0-9]*/line\.num) \n',r'\1 <utt>',line)
        line = re.sub(r'((v\.aux|v\.cop\.neg|v\.cop|v\.fut\.v\.past|v\.fut\.v\.pres|v\.fut|v\.imp|v\.invar|v\.neg|v\.past\.v\.pres|v\.past|v\.pres) [།༔]/punc) \n',r'\1 <utt>',line)
        line = re.sub(r'([།༔]/punc ln[0-9]*/line\.num [།༔]/punc)\s?\n',r'\1 <utt>',line)
        line = re.sub(r'([།༔]/punc [།༔]/punc ln[0-9]*/line\.num)\s?\n',r'\1 <utt>',line)
                
        line = re.sub(r'\s+',r' ',line)
        line = re.sub(r'\n',r'',line)
        line = re.sub(r'<utt>',r'<utt>\n',line)
        
        
        #line = re.sub(r'\Z','<utt>',line)
        #line = re.sub(r'([^(<utt>)]\Z)',r'\1 <utt>',line) #this works in Sublime, but not here because it remembers the lines...

        #print(line)   #to troubleshoot: with this you can see in the Terminal at which line it goes wrong.         
        
        corpus.append(line)   
        line = inp.readline()
        
    #convert corpus list to string to write in output file
    outputcorpus = ''.join(corpus)    

    

    #add final <utt> if the file doesn't end in <utt>
    if not outputcorpus.endswith("<utt>"):
        outputcorpus = outputcorpus + '<utt>'
    
    #deletes empty sentences at the end of the file
    if outputcorpus.endswith("\n<utt>"):
        outputcorpus = outputcorpus[:-6]


    #return output
    return outputcorpus   

"""
Executing main function (so that it works as a script directly from the terminal; not just in shell interpreter)
"""

if __name__ == "__main__":
    main()