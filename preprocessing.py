import re
import sys, argparse
import codecs #tested for Python2 only so far
import os
import glob
import time
import pyewts
import pathlib
from pathlib import Path
from subprocess import call

def main():
    """
    Main function that goes into the directory that you enter as the main argument and reads all *.txt files.
    It then creates an output folder in which the cs functions create three different outputs: 
    standard Wylie, Old Tibetan Unicode and normalised Old Tibetan Unicode
    In the right folder, call 'postprocessing.py 'directory_name'.
    """
    dir_name = sys.argv[1]
    os.chdir('%s' % dir_name)
    out_dir_name = 'results_%s' % (dir_name)
    call(['mkdir', out_dir_name ])



    for file in glob.glob("*.txt"):
        standardWylie(file, out_dir_name)

    for file in glob.glob("**/*Wylie.txt"):

        convertToUnicode(file)

    for file in glob.glob("**/*standardUnicode.txt"):

        OT_Normalised(file)

def standardWylie(file_name,out_dir_name):

        file_name = re.sub('.txt','',file_name)
        wylie_standard = open('%s/%s_standardWylie.txt' %(out_dir_name, file_name), 'w')

        with open('%s.txt' %file_name, 'r', encoding="utf-8") as file_input:
            for line in file_input:
                    #regex to standardise the OTDO Wylie to normal Wylie (except reverse gigu which is addded at the end of the regex block
                    line = re.sub(r'\^',r'',line)
                    line = re.sub(r'v',r'w',line)
                    line = re.sub(r'[\s]*\/[\s]*',r'/',line)
                    line = re.sub(r'\\\$',r'@#',line)
                    # regex to clean editorial conventions
                    line = re.sub(r'([a-z,I,\',.]*)\[([^\s,\[,?,-]*)]([a-z,I,\',.]*)',r'*\1\2\3',line) #regex 1
                    line = re.sub(r'\[([^\s,\(,\),\[,-]+)\s([^\s,\(,\),\[,-]+)\]',r'*\1 *\2',line) #regex 7
                    line = re.sub(r'\[([^\s,\(,\),\[,-]+)\s([^\s,\(,\),\[,-]+)\s([^\s,\(,\),\[,-]+)\]',r'*\1 *\2 *\3',line) #regwx 7
                    line = re.sub(r'\*\*',r'*',line) #regex 2
                    line = re.sub(r'([a-z,I,\',.]+)\*([a-z,I,\',.]+)',r'\1\2',line) #regex 2
                    line = re.sub(r'([a-z,I,\',.]*)\[-]([a-z,I,\',.]*)',r'*\1\2',line) #regex 3
                    line = re.sub(r'([a-z,I,\',.]*)\[([^\s]*)\?]([a-z,I,\',.]*)',r'*\1\2\3',line) #regex 4
                    line = re.sub(r'\[([a-z,I,\',.]*) \(\/([a-z,I,\',.]*)\)\]',r'*\1',line) #regex 6
                    line = re.sub(r'###',r'',line)
                    line = re.sub(r'\([^0-9]+\)',r'',line)
                    line = re.sub(r'\{.*\}',r'',line)
                    line = re.sub(r'\s\(',r'(',line)
                    line = re.sub(r'\)\s',r')',line)
                    line = re.sub(r' +',r' ',line)



                    line = re.sub(r'I',r'-i',line)
                    #we need to convert * to § in order to retain trace of the editorial conventions
                    #once we convert to Unicode * is converted in tsheg so we need an alternative
                    #symbol - we receonvert § to * after with a re.sub
                    line = re.sub(r'\*',r'§',line)
                    wylie_standard.write(line)

        wylie_standard.close()

def convertToUnicode(file_name):
    file_name = re.sub('_standardWylie.txt','',file_name)
    unicode_Tibetan = open('%s_standardUnicode.txt' %file_name, 'w', encoding="utf-8")

    with open('%s_standardWylie.txt' %file_name, 'r', encoding="utf-8") as file_input:
            for line in file_input:

                    converter = pyewts.pyewts()
                    unicode = converter.toUnicode(line)
                    #print(unicode,file=output_file)

                    for line in unicode:

                        line = re.sub(r'§',r'*',line) #reintroduce * for editorial conventions
                        #replace double shed with two single shed
                        line = re.sub(r'༎',r'།།',line)
                        line = re.sub(r'༎༎',r'།།།།',line)
                        #regex to convert ༼tibetandigit༽ to l+linenumber
                        line = re.sub(r'---',r'[---]',line) #not working properly in Python
                        line = re.sub(r'༼',r'(',line)
                        line = re.sub(r'༽',r')',line)
                        line = re.sub(r'༠',r'0',line)
                        line = re.sub(r'༡',r'1',line)
                        line = re.sub(r'༢',r'2',line)
                        line = re.sub(r'༣',r'3',line)
                        line = re.sub(r'༤',r'4',line)
                        line = re.sub(r'༥',r'5',line)
                        line = re.sub(r'༦',r'6',line)
                        line = re.sub(r'༧',r'7',line)
                        line = re.sub(r'༨',r'8',line)
                        line = re.sub(r'༩',r'9',line)
                        line = re.sub(r'\(',r'l',line)
                        #line = re.sub(r'་l་',r'l',line)
                        line = re.sub(r'\)',r'',line)
                        line = re.sub(r'\s+',r'',line)
                        

                        unicode_Tibetan.write(line)
                        #print(line,file=output_file)

    unicode_Tibetan.close()


def OT_Normalised(file_name):
    file_name = re.sub('_standardUnicode.txt','',file_name)
    Normalised_OT = open('%s_normalUnicode.txt' %file_name, 'w', encoding="utf-8")

    with open('%s_standardUnicode.txt' %file_name, 'r', encoding="utf-8") as file_input:
            
            for line in file_input:

                count = 0
                #Old Tibetan genitive - diphthong  ོེ་ replace with ོའི་
                line = re.sub(r'(.*)ོེ(་?)',r'\1ོའི\2',line)

                #Merged syllables - specific cases: 
                line = re.sub(r'བགྱིསྣ(་?)',r'བགྱིས་ན\1',line)
                line = re.sub(r'རབ༹ལ(་?)',r'རབ༹་ལ\1',line)
                line = re.sub(r'མཆིསྣ(་?)',r'མཆིས་ན\1',line)
                line = re.sub(r'མོལ(་?)',r'མོ་ལ\1',line)
                line = re.sub(r'ཐོགསླ(་?)',r'ཐོགས་ལ\1',line)
                line = re.sub(r'ལྕེབསའོ(་?)',r'ལྕེབས་སོ\1',line)
                line = re.sub(r'གཤེགསའོ(་?)',r'གཤེགས་སོ\1',line)
                line = re.sub(r'བཏགསའོ(་?)',r'བཏགས་སོ\1',line)
                line = re.sub(r'ལསྩོགསྟེ(་?)',r'ལ་སྩོགས་སྟེ\1',line)
                line = re.sub(r'མའང(་?)',r'མ་འང\1',line)
                line = re.sub(r'མྱིངདུ(་?)',r'མྱིང་དུ\1',line)
                line = re.sub(r'རིགསྣ(་?)',r'རིགས་ན\1',line)
                line = re.sub(r'ཤུལྡུ(་?)',r'ཤུལ་དུ\1',line)
                line = re.sub(r'བདགིས(་?)',r'བདག་གིས\1',line)


                #Merged syllables - Rule for cases such as དྲངསྟེ > དྲངས་ཏེ
                line = re.sub(r'([^་\n\s།]+)སྟེ(་?)',r'\1ས་ཏེ\2',line)
            
                #Merged Syllables - Rule for cases as གཅལྟོ > གཅལད་ཏོ
                line = re.sub(r'([^་\n\s།]+)((.)ྟ([ོ,ེ]་?))',r'\1\3ད་ཏ\4',line)

                #Merged Syllables - Rule for cases as པགི་ > པག་གི་
                line = re.sub(r'([^དའ*་\n\s།])((ག)([ྀ,ི]་?))',r'\1ག་ག\4',line)

                #Merged Syllables - Generic rule
                line = re.sub(r'([^་\n\s།]{2,6})(([^ྲ,ྱ,ྩ,ྒ,ླ,ྡ,ྕ,ྟ,ྙ,ྐ,ྗ,དི,འ,ཨ])([ོ,ེ,ུ,ི,ྀ]་?))',r'\1\3་\3\4',line)
                
                # Reverse Gigu:
                line = re.sub(r'([^་\n\s།]*)འྀ་',r'\1འི་',line) #for genitive          
                line = re.sub(r'([^་\n\s།]*)ྀ([^་\n\s།]*)',r'\1ི\2',line) #general rule

                # Ma Ya Btags
                line = re.sub(r'([^་\n\s།]*)མྱི([^་\n\s།]*)',r'\1མི\2',line)
                line = re.sub(r'([^་\n\s།]*)མྱེ([^་\n\s།]*)',r'\1མེ\2',line)

                # Changing སྩ with ས
                line = re.sub(r'གསྩན(་?)',r'གསན\1',line)
                line = re.sub(r'གསྩང(་?)',r'གསང\1',line)
                line = re.sub(r'གསྩནད(་?)',r'གསནད\1',line)
                line = re.sub(r'གསྩན(་?)',r'གསན\1',line)
                line = re.sub(r'སྩོགས(་?)',r'སོགས\1',line)
                line = re.sub(r'སྩུབ(་?)',r'སུབ\1',line)
                line = re.sub(r'སྩང(་?)',r'སང\1',line)
                line = re.sub(r'སྩངས(་?)',r'སངས\1',line)
                line = re.sub(r'གསྩུག(་?)',r'གསུག\1',line)
                line = re.sub(r'བསྩག་(་?)',r'བསག\1',line)
                
                #Normalise Anusvara symbol ཾ with མ:
                line = re.sub(r'([^་\n\s།]*)ཾ([^་\n\s།]*)',r'\1མ\2',line)

                # 'a rten
                line = re.sub(r'ཡི་གེའ(་?)',r'ཡི་གེ\1',line)
                line = re.sub(r'དུའ(་?)',r'དུ\1',line)
                line = re.sub(r'པའ(་?)',r'པ\1',line)
                line = re.sub(r'ལའ(་?)',r'ལ\1',line)
                line = re.sub(r'ནའ(་?)',r'ན\1',line)
                line = re.sub(r'སྟེའ(་?)',r'སྟེ\1',line)
                line = re.sub(r'བའ(་?)',r'བ\1',line)
                line = re.sub(r'མའ(་?)',r'མ\1',line)
                line = re.sub(r'འདྲའ(་?)',r'འདྲ\1',line)

                # ད / ན suffix variation
                # Background: The ད / ན suffix variation is another feature of Old Tibetan. Common forms are ཆེད་པོ་ and ཅེད་པོ་
                # Rule: Normalize ཆེད་པོ་(པོའི་/པོར་/པོས་) and ཅེད་པོ་(པོའི་/པོར་/པོས་) as ཆེན་པོ་(པོའི་/པོར་/པོས་)
                line = re.sub(r'(ཅེ|ཆེ)(ད|ན)་((པོ|ཕོ)(འི|ར|ས)?(་?))',r'ཆེན་\3',line)

                # Medial འ
                line = re.sub(r'([^་\n\s།]+)འ(ས|ད|ར)་',r'\1\2',line)

                # Alternation between aspirated and unaspirated voiceless consonants
                line = re.sub(r'པོ་ཉ(་?)',r'ཕོ་ཉ\1',line)
                line = re.sub(r'དམག་ཕོན(་?)',r'དམག་དཔོན\1',line)
                line = re.sub(r'པྱག(་?)',r'ཕྱག\1',line)
                line = re.sub(r'པོག(་?)',r'ཕོག\1',line)
                line = re.sub(r'པོ་བྲང(་?)',r'ཕོ་བྲང\1',line)
                line = re.sub(r'པོ་དང་ཕོ(་?)',r'པོ་དང་པོ\1',line)
                line = re.sub(r'བལ་ཕོ(་?)',r'བལ་པོ\1',line)
                line = re.sub(r'ཕལ་ཕོ(་?)',r'ཕལ་པོ\1',line)
                line = re.sub(r'རྩང་ཅེན(་?)',r'རྩང་ཆེན\1',line)
                line = re.sub(r'ཕར་ལོ(་?)',r'པར་ལོ\1',line)
                line = re.sub(r'བློན་ཅེན(་?)',r'བློན་ཆེན\1',line)
                line = re.sub(r'ཞལ་ཅེ(་?)',r'ཞལ་ཆེ\1',line)
                line = re.sub(r'མེར་ཁེ(་?)',r'མེར་ཀེ\1',line)
                line = re.sub(r'ལོ་ཆིག(་?)',r'ལོ་གཅིག\1',line)
                line = re.sub(r'པྱི(་?)',r'ཕྱི\1',line)
                line = re.sub(r'པྱིར(་?)',r'ཕྱིར\1',line)
                line = re.sub(r'སྙེད་ཆིག(་?)',r'སྙེད་ཅིག\1',line)
                line = re.sub(r'པུལ(་?)',r'ཕུལ\1',line)
                line = re.sub(r'བདག་ཆག(་?)',r'བདག་ཅག\1',line)
                line = re.sub(r'པུར(་?)',r'ཕུར\1',line)
                
                # Alternation between aspirated and unaspirated voiceless consonants: ཕ / ཕོ vs པ / པོ
                line = re.sub(r'(སྐྱེས་|བགྱིས་|བཏབ་|སོགས་|གསོལད་)ཕ((འི|ས|ར)?་?)',r'\1པ\2',line)
                line = re.sub(r'(རྒྱལ་|བློན་|བཚན་|ཆེན་|བཟང་|བདག་|བོན་|རྒན་|བཙན་|དྲག་|དམར་|མང་|མྱེས་|མྱེས་|མེས་|བསྩན་)ཕ((འི|ས|ར)?་?)',r'\1པ\2',line)
                line = re.sub(r'(རྒྱལ་|བློན་|བཚན་|ཆེན་|བཟང་|བདག་|བོན་|རྒན་|བཙན་|དྲག་|དམར་|མང་|མྱེས་|མྱེས་|མེས་|བསྩན་)ཕོ((འི|ས|ར)?་?)',r'\1པོ\2',line)

                # Aspirated Voiceless Consonants
                line = re.sub(r'མཀ(་?)',r'མཁ\1',line)
                line = re.sub(r'མཅ(་?)',r'མཆ\1',line)
                line = re.sub(r'མཏ(་?)',r'མཐ\1',line)
                line = re.sub(r'མཙ(་?)',r'མཚ\1',line)
                line = re.sub(r'འཀ(་?)',r'འཁ\1',line)
                line = re.sub(r'འཅ(་?)',r'འཆ\1',line)
                line = re.sub(r'འཏ(་?)',r'འཐ\1',line)
                line = re.sub(r'འཔ(་?)',r'འཕ\1',line)
                line = re.sub(r'འཙ(་?)',r'འཚ\1',line)
                
                # Unaspirated Voiceless Consonants
                line = re.sub(r'དཁ(་?)',r'དཀ\1',line)
                line = re.sub(r'དཕ(་?)',r'དཔ\1',line)
                line = re.sub(r'གཆ(་?)',r'གཅ\1',line)
                line = re.sub(r'གཐ(་?)',r'གཏ\1',line)
                line = re.sub(r'གཚ(་?)',r'གཙ\1',line)
                line = re.sub(r'བཁ(་?)',r'བཀ\1',line)
                line = re.sub(r'བཆ(་?)',r'བཅ\1',line)
                line = re.sub(r'བཐ(་?)',r'བཏ\1',line)
                line = re.sub(r'བཚ(་?)',r'བཙ\1',line)
                line = re.sub(r'སྑ(་?)',r'སྐ\1',line)
                line = re.sub(r'སྠ(་?)',r'སྟ\1',line)
                line = re.sub(r'སྥ(་?)',r'སྤ\1',line)
                line = re.sub(r'སྪ(་?)',r'སྩ\1',line)
                line = re.sub(r'རྑ(་?)',r'རྐ\1',line)
                line = re.sub(r'རྠ(་?)',r'རྟ\1',line)
                line = re.sub(r'རྪ(་?)',r'རྩ\1',line)
                line = re.sub(r'ལྑ(་?)',r'ལྐ\1',line)
                line = re.sub(r'ལྖ(་?)',r'ལྕ\1',line)
                line = re.sub(r'ལྠ(་?)',r'ལྟ\1',line)
                line = re.sub(r'ལྥ(་?)',r'ལྤ\1',line)
                

                Normalised_OT.write(line)

    Normalised_OT.close()


"""
Executing main function (so that it works as a script directly from the terminal)
"""

if __name__ == "__main__":
    main()
