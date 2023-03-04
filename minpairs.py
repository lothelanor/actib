import pyewts
from tqdm import tqdm
import re
import sys, argparse
import os
import glob
import time
from typing import List, Dict, Tuple
from subprocess import call

"""Script to create a list of Tibetan minimal pairs with initial consonant clusters
e.g. "ཟླ་རྒྱལ་" & "ཟླ་རྒྱད", or, in Wylie "zla rgyal" & "zla rgyad" etc
It generates a list of absolute minimal pairs AND minimal pairs where initial clusters
with two consonants, e.g. zl~ld are treated as one sound, e.g. zla~lda.
It also lists minimal pairs with zero-initials or zero-finals, e.g. zla~zlam.
In addition, it creates lists of certain specific pairs, e.g. zl~d, ld~d, etc.
Finally, it uses pyewts to convert Tibetan Unicode to Wylie, but takes Wylie digraphs into account,
counting them as one sound, e.g. phab~pab, tshun~tsun~tun.
In the folder where the Tibetan Unicode dictionary file 'monlamexport-cleaned.txt' is:
python minpairs.py directory_name to create results file in that directory."""

def main():
	dir_name = sys.argv[1]
	os.chdir('%s' % dir_name)
	converter = pyewts.pyewts()

	#Create variables for empty strings to be filled with outputs
	output1 = '' #true minimal pairs
	output2 = '' #entire cluster (if cluster = two letters)
	output3a = '' #zero_start pairs W2
	output3b = '' #zero_start pairs W1
	output4a = '' #zero_end pairs W2
	output4b = '' #zero_end pairs W1
	output5a = '' #zl~d pairs
	output5b = '' #d~zl pairs
	output6a = '' #ld~d pairs
	output6b = '' #d~ld pairs
	output7a = '' #zl~l pairs
	output7b = '' #l~zl pairs
	output8a = '' #ld~l pairs
	output8b = '' #l~ld pairs

	tokencounter=0

	#Open the relevant dictionary file(s) in the chosen folder
	for filename in glob.glob('*.txt'):
		with open(os.path.join(os.getcwd(), filename), 'r') as f:
			#read all lines into a string
			wyliestring = f.read()
			#convert string to Wylie
			wyliestring = converter.toWylie(wyliestring)
			#delete previous tsheg now spaces
			wyliestring = re.sub(' \n','\n',wyliestring)
			#change space to hyphen to preserve words
			wyliestring = re.sub(' ','_',wyliestring)
			wyliestring = re.sub('_\n','\n',wyliestring)
			#remove Sanskrit words (capital letters in Wylie and +-* etc)
			wyliestring = re.sub(r'(^|\s)([^\s]*)([A-Z\+\-\*]+)([^\s]*)','\n',wyliestring)
			wyliestring = re.sub(r'(^|\s)([^\s]*)([A-Z\+\-\*]+)','\n',wyliestring)
			wyliestring = re.sub(r'(^|\s)([A-Z\+\-\*]+)([^\s]*)','\n',wyliestring)
			#remove empty lines
			wyliestring = re.sub(r'\n+','\n',wyliestring)
			#convert _ to - and -- to -
			wyliestring = re.sub('_','-',wyliestring)
			wyliestring = re.sub('--','-',wyliestring)
			#get rid of potential non-breaking tsheg at the end of the file
			wyliestring = re.sub(r'-$','',wyliestring)

			#Write vocab list to file
			filename = re.sub('.txt','',filename)
			output_file = open('%s_results-vocablist.txt' % (filename), 'w') 
			output_file.write("List of tokens in " + filename + ".txt after removing some Sanskrit:\n" + wyliestring)
			output_file.close()
			print("\nList of tokens after removing some Sanskrit:\n" + wyliestring)

			#convert <ng> temporarily to Y to treat as one sound
			wyliestring = re.sub('ng','Y',wyliestring)
			#convert <dz> temporarily to Z to treat as one sound
			wyliestring = re.sub('dz','Z',wyliestring)
			#convert <ts> temporarily to T to treat as one sound
			wyliestring = re.sub('tsh','S',wyliestring)
			#convert <th> temporarily to M to treat as one sound
			wyliestring = re.sub('ts','T',wyliestring)
			#convert <tsh> temporarily to S to treat as one sound
			wyliestring = re.sub('th','Q',wyliestring)
			#convert <zh> temporarily to H to treat as one sound
			wyliestring = re.sub('zh','H',wyliestring)
			#convert <sh> temporarily to H to treat as one sound
			wyliestring = re.sub('sh','L',wyliestring)
			#convert <ch> temporarily to C to treat as one sound
			wyliestring = re.sub('ch','C',wyliestring)
			#convert <ph> temporarily to P to treat as one sound
			wyliestring = re.sub('ph','P',wyliestring)
			#convert string to list of words
			wyliewordlist = wyliestring.splitlines()

			#remove duplicates
			wyliewordlist = list(dict.fromkeys(wyliewordlist))

			#If tqdm progress marker doesn't work, activate below token counter
			#Count total tokens to keep track of how fast your computer is getting through it
			total_tokens = len(wyliewordlist)
			numberlist=[]
			for i in range(total_tokens,-1,-1):
				numberlist.append(i)
			total=sum(numberlist)-total_tokens
			print("Number of tokens to compare: " + str(total_tokens) + "\nNumber of pair-wise comparisons: " + str(total) + "...")

			#loop through list comparing each word to the next word
			for n1,word1 in enumerate(tqdm(wyliewordlist)): #tqdm will show progress bar
				for word2 in wyliewordlist[n1+1:]:
					#Show progress in the terminal (useful for big files)
					#print token counter (if the tqdm progress thingy doesn't work)
					tokencounter+=1
					# print("Comparing token " + str(tokencounter) + " out of " + str(total) + "...")

					#Define initial cluster variables
					cl_Word1 = word1[:4]
					cl_Word2 = word2[:4]
					cl_Word1 = re.sub(r'(^)(.+)[aeiouAEIOU].*',r"\2",cl_Word1)
					cl_Word1 = re.sub(r'(^)(.)[aeiouAEIOU].*',r"\2",cl_Word1)
					cl_Word1 = re.sub(r'(^)[aeiouAEIOU].*',"vowel",cl_Word1)
					cl_Word2 = re.sub(r'(^)(.+)[aeiouAEIOU].*',r"\2",cl_Word2)
					cl_Word2 = re.sub(r'(^)(.)[aeiouAEIOU].*',r"\2",cl_Word2)
					cl_Word2 = re.sub(r'(^)[aeiouAEIOU].*',"vowel",cl_Word2)

					#Check if the length of the words that are compared is the same
					if len(word1)==len(word2):
						ndiff=0
						#if the length is the same, check if characters are the same
						for n,letter in enumerate(word1):
							if word2[n]!=letter:
								ndiff+=1
								if ndiff > 2:
									break
						#if only one letter is different, it is a minimal pair
						if ndiff==1:
							output1 += "minpair:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
							output1 = re.sub("Y", "ng", output1)
							output1 = re.sub("H", "zh", output1)
							output1 = re.sub("L", "sh", output1)
							output1 = re.sub("P", "ph", output1)
							output1 = re.sub("C", "ch", output1)
							output1 = re.sub("Q", "th", output1)
							output1 = re.sub("Z", "dz", output1)
							output1 = re.sub("T", "ts", output1)
							output1 = re.sub("S", "tsh", output1)
							output1 = re.sub("\tX", "\t", output1)
							# print(output1)
							#Write results to new file
							output_file = open('%s_results-minpairs.txt' % (filename), 'w') 
							output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output1)
							output_file.close()

						elif ndiff==2 and len(word1)>2:
							# check if both first and second of initial cluster are different
							if word1[0]!=word2[0] and word1[1]!=word2[1] and word1[1] not in 'aeiou':
								output2 += "entire_init_cluster:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output2 = re.sub("Y", "ng", output2)
								output2 = re.sub("H", "zh", output2)
								output2 = re.sub("L", "sh", output2)
								output2 = re.sub("P", "ph", output2)
								output2 = re.sub("C", "ch", output2)
								output2 = re.sub("Q", "th", output2)
								output2 = re.sub("Z", "dz", output2)
								output2 = re.sub("T", "ts", output2)
								output2 = re.sub("S", "tsh", output2)
								output2 = re.sub("\tX", "\t", output2)
								# print(output2a)
								#Write results to new file
								filename = re.sub('.txt','',filename)
								output_file = open('%s_results-entire_init_cluster.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output2)
								output_file.close()

					#Check with word2 zero word-initially or -finally
					elif len(word1)-len(word2)==1:
						#Add X as char place holder to be able to compare
						word2a = "X" + word2 #zero word-initially
						word2b = word2 + "X" #zero word-finally
						cdiff=0
						qdiff=0
						xdiff=0
						wdiff=0
						zdiff=0
						#check for zl~d pairs separately
						if word1[:2]==r"zl" and word2a[:2]==r"Xd":
							for n,letter in enumerate(word1):
								if word2a[n]!=letter:
									cdiff+=1
									if cdiff > 2:
										break
							if cdiff==2:
								output5a += "zl~d:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output5a = re.sub("Y", "ng", output5a)
								output5a = re.sub("H", "zh", output5a)
								output5a = re.sub("L", "sh", output5a)
								output5a = re.sub("P", "ph", output5a)
								output5a = re.sub("C", "ch", output5a)
								output5a = re.sub("Q", "th", output5a)
								output5a = re.sub("Z", "dz", output5a)
								output5a = re.sub("T", "ts", output5a)
								output5a = re.sub("S", "tsh", output5a)
								output5a = re.sub("\tX", "\t", output5a)
								# print(output5a)

								#Write results to new file
								output_file = open('%s_results-zl_d.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output5a)
								output_file.close()

						#check for ld~d pairs separately
						elif word1[:2]==r"ld" and word2a[:2]==r"Xd":
							for n,letter in enumerate(word1):
								if word2a[n]!=letter:
									xdiff+=1
									if xdiff > 1:
										break
							if xdiff==1:
								output6a += "ld~d:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output6a = re.sub("Y", "ng", output6a)
								output6a = re.sub("H", "zh", output6a)
								output6a = re.sub("L", "sh", output6a)
								output6a = re.sub("P", "ph", output6a)
								output6a = re.sub("C", "ch", output6a)
								output6a = re.sub("Q", "th", output6a)
								output6a = re.sub("Z", "dz", output6a)
								output6a = re.sub("T", "ts", output6a)
								output6a = re.sub("S", "tsh", output6a)
								output6a = re.sub("\tX", "\t", output6a)
								# print(output6a)

								#Write results to new fil
								output_file = open('%s_results-ld_d.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output6a)
								output_file.close()

						#check for zl~l pairs separately
						elif word1[:2]==r"zl" and word2a[:2]==r"Xl":
							for n,letter in enumerate(word1):
								if word2a[n]!=letter:
									wdiff+=1
									if wdiff > 1:
										break
							if wdiff==1:
								output7a += "zl~l:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output7a = re.sub("Y", "ng", output7a)
								output7a = re.sub("H", "zh", output7a)
								output7a = re.sub("L", "sh", output7a)
								output7a = re.sub("P", "ph", output7a)
								output7a = re.sub("C", "ch", output7a)
								output7a = re.sub("Q", "th", output7a)
								output7a = re.sub("Z", "dz", output7a)
								output7a = re.sub("T", "ts", output7a)
								output7a = re.sub("S", "tsh", output7a)
								output7a = re.sub("\tX", "\t", output7a)
								# print(output7a)

								#Write results to new file
								filename = re.sub('.txt','',filename)
								output_file = open('%s_results-zl_l.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output7a)
								output_file.close()

						else:
							for n,letter in enumerate(word1):
								if word2a[n]!=letter:
									cdiff+=1
									if cdiff > 1:
										break
							if cdiff==1:
								output3a += "zero_start_W2:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output3a = re.sub("Y", "ng", output3a)
								output3a = re.sub("H", "zh", output3a)
								output3a = re.sub("L", "sh", output3a)
								output3a = re.sub("P", "ph", output3a)
								output3a = re.sub("C", "ch", output3a)
								output3a = re.sub("Q", "th", output3a)
								output3a = re.sub("Z", "dz", output3a)
								output3a = re.sub("T", "ts", output3a)
								output3a = re.sub("S", "tsh", output3a)
								output3a = re.sub("\tX", "\t", output3a)
								# print(output3)

								#Write results to new file
								filename = re.sub('.txt','',filename)
								output_file = open('%s_results-zero_start_W2.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output3a)
								output_file.close()
							for n,letter in enumerate(word1):
								if word2b[n]!=letter:
									qdiff+=1
									if qdiff > 1:
										break
							if qdiff==1:
								output4a += "zero_end_W2:\t" + cl_Word1 + "\t" + word1 + "\t" + cl_Word2 + "\t" + word2 + "\n"
								output4a = re.sub("Y", "ng", output4a)
								output4a = re.sub("H", "zh", output4a)
								output4a = re.sub("L", "sh", output4a)
								output4a = re.sub("P", "ph", output4a)
								output4a = re.sub("C", "ch", output4a)
								output4a = re.sub("Q", "th", output4a)
								output4a = re.sub("Z", "dz", output4a)
								output4a = re.sub("T", "ts", output4a)
								output4a = re.sub("S", "tsh", output4a)
								output4a = re.sub("\tX", "\t", output4a)
								# print(output4)

								#Write results to new file
								filename = re.sub('.txt','',filename)
								output_file = open('%s_results-zero_end_W2.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W1\tWord1\tcluster-W2\tWord2\n" + output4a)
								output_file.close()

					#Check with word1 zero word-initially or -finally
					elif len(word2)-len(word1)==1:
						#Add X as char place holder to be able to compare
						word1a = "X" + word1 #zero word-initially
						word1b = word1 + "X" #zero word-finally
						tdiff=0
						pdiff=0
						sdiff=0
						zdiff=0
						rdiff=0
						hdiff=0
						bdiff=0
						#check for d~zl pairs separately
						if word2[:2]==r"zl" and word1a[:2]==r"Xd":
							for n,letter in enumerate(word2):
								if word1a[n]!=letter:
									tdiff+=1
									if tdiff > 2:
										break
							if tdiff==2:
								output5b += "d~zl:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output5b = re.sub("Y", "ng", output5b)
								output5b = re.sub("H", "zh", output5b)
								output5b = re.sub("L", "sh", output5b)
								output5b = re.sub("P", "ph", output5b)
								output5b = re.sub("C", "ch", output5b)
								output5b = re.sub("Q", "th", output5b)
								output5b = re.sub("Z", "dz", output5b)
								output5b = re.sub("T", "ts", output5b)
								output5b = re.sub("S", "tsh", output5b)
								output5b = re.sub("\tX", "\t", output5b)
								# print(output5)

								#Write results to new file
								output_file = open('%s_results-d_zl.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output5b)
								output_file.close()

						#check for d~ld pairs separately
						elif word2[:2]==r"ld" and word1a[:2]==r"Xd":
							for n,letter in enumerate(word2):
								if word1a[n]!=letter:
									sdiff+=1
									if sdiff > 1:
										break
							if sdiff==1:
								output6b += "d~ld:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output6b = re.sub("Y", "ng", output6b)
								output6b = re.sub("H", "zh", output6b)
								output6b = re.sub("L", "sh", output6b)
								output6b = re.sub("P", "ph", output6b)
								output6b = re.sub("C", "ch", output6b)
								output6b = re.sub("Q", "th", output6b)
								output6b = re.sub("Z", "dz", output6b)
								output6b = re.sub("T", "ts", output6b)
								output6b = re.sub("S", "tsh", output6b)
								output6b = re.sub("\tX", "\t", output6b)
								# print(output6)

								#Write results to new file
								output_file = open('%s_results-d_ld.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output6b)
								output_file.close()

						#check for l~zl pairs separately
						elif word2[:2]==r"zl" and word1a[:2]==r"Xl":
							for n,letter in enumerate(word2):
								if word1a[n]!=letter:
									sdiff+=1
									if sdiff > 1:
										break
							if sdiff==1:
								output7b += "l~zl:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output7b = re.sub("Y", "ng", output7b)
								output7b = re.sub("H", "zh", output7b)
								output7b = re.sub("L", "sh", output7b)
								output7b = re.sub("P", "ph", output7b)
								output7b = re.sub("C", "ch", output7b)
								output7b = re.sub("Q", "th", output7b)
								output7b = re.sub("Z", "dz", output7b)
								output7b = re.sub("T", "ts", output7b)
								output7b = re.sub("S", "tsh", output7b)
								output7b = re.sub("\tX", "\t", output7b)
								# print(output7b)

								#Write results to new file
								output_file = open('%s_results-l_zl.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output7b)
								output_file.close()

						#check for l~ld pairs separately
						elif word2[:2]==r"ld" and word1a[:2]==r"Xl":
							for n,letter in enumerate(word2):
								if word1a[n]!=letter:
									rdiff+=1
									if rdiff > 1:
										break
							if rdiff==1:
								output8b += "l~ld:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output8b = re.sub("Y", "ng", output8b)
								output8b = re.sub("H", "zh", output8b)
								output8b = re.sub("L", "sh", output8b)
								output8b = re.sub("P", "ph", output8b)
								output8b = re.sub("C", "ch", output8b)
								output8b = re.sub("Q", "th", output8b)
								output8b = re.sub("Z", "dz", output8b)
								output8b = re.sub("T", "ts", output8b)
								output8b = re.sub("S", "tsh", output8b)
								output8b = re.sub("\tX", "\t", output8b)
								# print(output8b)

								#Write results to new file
								output_file = open('%s_results-l_ld.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output8b)
								output_file.close()

						else:
							for n,letter in enumerate(word2):
								if word1a[n]!=letter:
									hdiff+=1
									if hdiff > 1:
										break
							if hdiff==1:
								output3b += "zero_start_W1:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output3b = re.sub("Y", "ng", output3b)
								output3b = re.sub("H", "zh", output3b)
								output3b = re.sub("L", "sh", output3b)
								output3b = re.sub("P", "ph", output3b)
								output3b = re.sub("C", "ch", output3b)
								output3b = re.sub("Q", "th", output3b)
								output3b = re.sub("Z", "dz", output3b)
								output3b = re.sub("T", "ts", output3b)
								output3b = re.sub("S", "tsh", output3b)
								output3b = re.sub("\tX", "\t", output3b)
								# print(output3b)

								#Write results to new file
								output_file = open('%s_results-zero_start_W1.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output3b)
								output_file.close()

							for n,letter in enumerate(word2):
								if word1b[n]!=letter:
									bdiff+=1
									if bdiff > 1:
										break
							if bdiff==1:
								output4b += "zero_end_W1:\t" + cl_Word2 + "\t" + word2 + "\t" + cl_Word1 + "\t" + word1 + "\n"
								output4b = re.sub("Y", "ng", output4b)
								output4b = re.sub("H", "zh", output4b)
								output4b = re.sub("L", "sh", output4b)
								output4b = re.sub("P", "ph", output4b)
								output4b = re.sub("C", "ch", output4b)
								output4b = re.sub("Q", "th", output4b)
								output4b = re.sub("Z", "dz", output4b)
								output4b = re.sub("T", "ts", output4b)
								output4b = re.sub("S", "tsh", output4b)
								output4b = re.sub("\tX", "\t", output4b)
								# print(output4)

								#Write results to new file
								output_file = open('%s_results-zero_end_W1.txt' % (filename), 'w') 
								output_file.write("type\tcluster-W2\tWord2\tcluster-W1\tWord1\n" + output4b)
								output_file.close()

"""
Executing main function (so that it works as a script directly from the terminal)
"""

if __name__ == "__main__":
	main()