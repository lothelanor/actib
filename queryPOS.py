#!/usr/bin/env python
import re
import sys, argparse
import codecs #tested for Python3 only so far
import os
import glob
import time
from subprocess import call

def main():
    """
    Main function that goes into the directory that you enter as the main argument and reads all *.txt files.
    It then creates an output folder with a timestamp in which the cs function creates new files
    with results of examples of max 5 POS sequences per text.
    In the right folder, call 'python3 queryPOS.py 'directory_name'.
    """
    dir_name = sys.argv[1]        
    os.chdir('%s' % dir_name)
    timestamp = re.sub('[^A-Za-z0-9]','_', time.strftime('%c', time.gmtime()))
    out_dir_name = 'results_%s_%s' % (dir_name, timestamp)
    call(['mkdir', out_dir_name ])
    
    print("Enter max 5 POS tags in the right sequence (most RegExes allowed). \n\S+ for any (unknown) tag. Hit Enter to skip tags at the end.")
    POS1 = input("Enter POS1: ")
    POS2 = input("Enter POS2: ")
    POS3 = input("Enter POS3: ")
    POS4 = input("Enter POS4: ")
    POS5 = input("Enter POS5: ")
    POSsequence = POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' ' + POS5
    print('Searching for POS sequence: ' + POSsequence)

    totalhits = 0
    for file in glob.glob("*.txt"):
        totalhits = totalhits + findPOSseq(file,out_dir_name,POS1,POS2,POS3,POS4,POS5)
    print('Total hits whole directory = ' + str(totalhits) + ' ' + POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' ' + POS5)

def findPOSseq(file_name,out_dir_name,POS1,POS2,POS3,POS4,POS5):
    if len(POS1) == 0:
        print('Error: You need to enter at least POS1.')
    elif len(POS1) != 0 and len(POS2) == 0 and len(POS3) == 0 and len(POS4) == 0 and len(POS5) == 0:
        source_file = open('%s'  % file_name )
        results = []
        hits = 0
        sentences = 0
        #create variable for RegEx string match:
        matchseq = re.compile(r'[^|\s][^\s]+//?' + POS1 + r' ')
        #loop through lines to find matches and count hits and append those to results
        for line in source_file:
            sentences += 1
            if matchseq.search(line):
                results.append(line)
        #convert corpus list to string to write nicely with whiteline in between in output file:
        outputcorpus = '\n'.join(results)        
        #convert matchcorpus list to string to write nicely with whiteline in between in output file:
        matchcorpus = '\n'.join(matchseq.findall(outputcorpus))
        hits += len(matchseq.findall(outputcorpus))
        #write corpus to file
        file_name = re.sub('.txt','',file_name)
        output_file = open('%s/%s_results.txt' % (out_dir_name,file_name), 'w') 
        output_file.write(str(hits) + ' result(s) for ' + POS1 + ' found in ' + str(sentences) + ' total sentences.' + '\n\n' + 'Matches only:' + '\n\n' + matchcorpus + '\n\n' + 'Matches in lines:' + '\n\n' + outputcorpus)
        output_file.close()
        print(file_name + ' ' + str(hits) + ' result(s) for ' + POS1 + ' found in ' + str(sentences) + ' total sentences.')
        return hits
    elif len(POS1) != 0 and len(POS2) != 0 and len(POS3) == 0 and len(POS4) == 0 and len(POS5) == 0:
        source_file = open('%s'  % file_name )
        results = []
        hits = 0
        sentences = 0
        #create variable for RegEx string match:
        matchseq = re.compile(r'[^|\s][^\s]+//?' + POS1 + r'\s[^\s]+//?' + POS2 + r' ')
        #loop through lines to find matches and count hits and append those to results
        for line in source_file:
            sentences += 1
            if matchseq.search(line):
                results.append(line)
        #convert corpus list to string to write nicely with whiteline in between in output file:
        outputcorpus = '\n'.join(results)        
        #convert matchcorpus list to string to write nicely with whiteline in between in output file:
        matchcorpus = '\n'.join(matchseq.findall(outputcorpus))
        hits += len(matchseq.findall(outputcorpus))
        #write corpus to file
        file_name = re.sub('.txt','',file_name)
        output_file = open('%s/%s_results.txt' % (out_dir_name,file_name), 'w') 
        output_file.write(str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' found in ' + str(sentences) + ' total sentences.' + '\n\n' + 'Matches only:' + '\n\n' + matchcorpus + '\n\n' + 'Matches in lines:' + '\n\n' + outputcorpus)
        output_file.close()
        print(file_name + ' ' + str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' found in ' + str(sentences) + ' total sentences.')
        return hits
    elif len(POS1) != 0 and len(POS2) != 0 and len(POS3) != 0 and len(POS4) == 0 and len(POS5) == 0:
        source_file = open('%s'  % file_name )
        results = []
        hits = 0
        sentences = 0
        #create variable for RegEx string match:
        matchseq = re.compile(r'[^|\s][^\s]+//?' + POS1 + r'\s[^\s]+//?' + POS2 + r'\s[^\s]+//?' + POS3 + r' ')
        #loop through lines to find matches and count hits and append those to results
        for line in source_file:
            sentences += 1
            if matchseq.search(line):
                results.append(line)
        #convert corpus list to string to write nicely with whiteline in between in output file:
        outputcorpus = '\n'.join(results)        
        #convert matchcorpus list to string to write nicely with whiteline in between in output file:
        matchcorpus = '\n'.join(matchseq.findall(outputcorpus))
        hits += len(matchseq.findall(outputcorpus))
        #write corpus to file
        file_name = re.sub('.txt','',file_name)
        output_file = open('%s/%s_results.txt' % (out_dir_name,file_name), 'w') 
        output_file.write(str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 +' found in ' + str(sentences) + ' total sentences.' + '\n\n' + 'Matches only:' + '\n\n' + matchcorpus + '\n\n' + 'Matches in lines:' + '\n\n' + outputcorpus)
        output_file.close()
        print(file_name + ' ' + str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 +' found in ' + str(sentences) + ' total sentences.')
        return hits
    elif len(POS1) != 0 and len(POS2) != 0 and len(POS3) != 0 and len(POS4) != 0 and len(POS5) == 0:
        source_file = open('%s'  % file_name )
        results = []
        hits = 0
        sentences = 0
        #create variable for RegEx string match:
        matchseq = re.compile(r'[^|\s][^\s]+//?' + POS1 + r'\s[^\s]+//?' + POS2 + r'\s[^\s]+//?' + POS3 + r'\s[^\s]+//?' + POS4 + r' ')
        #loop through lines to find matches and count hits and append those to results
        for line in source_file:
            sentences += 1
            if matchseq.search(line):
                results.append(line)
        #convert corpus list to string to write nicely with whiteline in between in output file:
        outputcorpus = '\n'.join(results)        
        #convert matchcorpus list to string to write nicely with whiteline in between in output file:
        matchcorpus = '\n'.join(matchseq.findall(outputcorpus))
        hits += len(matchseq.findall(outputcorpus))
        #write corpus to file
        file_name = re.sub('.txt','',file_name)
        output_file = open('%s/%s_results.txt' % (out_dir_name,file_name), 'w') 
        output_file.write(str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' found in ' + str(sentences) + ' total sentences.' + '\n\n' + 'Matches only:' + '\n\n' + matchcorpus + '\n\n' + 'Matches in lines:' + '\n\n' + outputcorpus)
        output_file.close()
        print(file_name + ' ' + str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' found in ' + str(sentences) + ' total sentences.')
        return hits
    elif len(POS1) != 0 and len(POS2) != 0 and len(POS3) != 0 and len(POS4) != 0 and len(POS5) != 0:
        source_file = open('%s'  % file_name )
        results = []
        hits = 0
        sentences = 0
        #create variable for RegEx string match:
        matchseq = re.compile(r'[^|\s][^\s]+//?' + POS1 + r'\s[^\s]+//?' + POS2 + r'\s[^\s]+//?' + POS3 + r'\s[^\s]+//?' + POS4 + r'\s[^\s]+//?' + POS5 + r' ')
        #loop through lines to find matches and count hits and append those to results
        for line in source_file:
            sentences += 1
            if matchseq.search(line):
                results.append(line)
        #convert corpus list to string to write nicely with whiteline in between in output file:
        outputcorpus = '\n'.join(results)        
        #convert matchcorpus list to string to write nicely with whiteline in between in output file:
        matchcorpus = '\n'.join(matchseq.findall(outputcorpus))
        hits += len(matchseq.findall(outputcorpus))
        #write corpus to file
        file_name = re.sub('.txt','',file_name)
        output_file = open('%s/%s_results.txt' % (out_dir_name,file_name), 'w') 
        output_file.write(str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' ' + POS5 + ' found in ' + str(sentences) + ' total sentences.' + '\n\n' + 'Matches only:' + '\n\n' + matchcorpus + '\n\n' + 'Matches in lines:' + '\n\n' + outputcorpus)
        output_file.close()
        print(file_name + ' ' + str(hits) + ' result(s) for ' + POS1 + ' ' + POS2 + ' ' + POS3 + ' ' + POS4 + ' ' + POS5 + ' found in ' + str(sentences) + ' total sentences.')
        return hits
    else:
        print('Invalid input.')

"""
Executing main function (so that it works as a script directly from the terminal)
"""

if __name__ == "__main__":
    main()