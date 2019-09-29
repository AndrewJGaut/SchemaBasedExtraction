'''
This file genderswaps datasets using the genderSwap function.
For instance, genderswapping 'He loves his mom' --> 'She loves her dad'

'''

import os
import sys
sys.path.insert(0, './')
import string
import random
import nltk
from nltk.tag import StanfordNERTagger
from NameProbs import NameProb
from subprocess import Popen
from sys import stderr

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

st = StanfordNERTagger('/Users/agaut/PycharmProjects/TestStuff/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                       '/Users/agaut/PycharmProjects/TestStuff/stanford-ner/stanford-ner-3.9.2.jar',
					   encoding='utf-8')
'''st = StanfordNERTagger('NER/classifiers/english.all.3class.distsim.crf.ser.gz',
                       'NER/stanford-ner-3.9.2.jar',
					   encoding='utf-8')'''

import inflect
engine = inflect.engine()

sys.path.insert(0, './')
from os.path import dirname, abspath, join
sys.path.insert(0, join(dirname(dirname(dirname(abspath(__file__)))), 'Utility/'))


def getTextfile(directory, filename):
    with open(os.path.join(directory, filename), 'r') as infile:
        return infile

'''
What it does:
    Removes all non-alphanumerics from word AND makes the word singular (not plural)
    Used to check if words are in the set
'''
def clean(str, infl):
    cleanStr = ""
    for char in str:
        if(char.isalpha()):
            cleanStr += char.lower()
    if(infl.singular_noun(cleanStr)):
        cleanStr = infl.singular_noun(cleanStr)

    return cleanStr

'''
Parameters:
    data - a list of data. For us, a list of NameProbs
    val - the probability we're trying to find in data
What it does:
    Finds the closest probability to val in data
'''
def binarySearch(data, val):
    lo, hi = 0, len(data) - 1
    best_ind = lo
    while lo <= hi:
        mid = int(lo + (hi - lo) / 2)
        if data[mid].getProb() < val:
            lo = mid + 1
        elif data[mid].getProb() > val:
            hi = mid - 1
        else:
            best_ind = mid
            break
        # check if data[mid] is closer to val than data[best_ind]
        if abs(data[mid].getProb() - val) <= abs(data[best_ind].getProb() - val):
            best_ind = mid
    return data[best_ind].getOcc()

'''
Parameters:
    curr_name - the name we're going to swap
    this_gender_names - the hashset mapping names to their probabilities for the gender of curr_name
    opposite_gender_names - a list of NameProbs for the opposite gender
What it does:
    Returns name of opposite gender of curr_name that has the closest probability to curr_name
'''
def getName(curr_name, this_gender_names, opposite_gender_names):
    curr_prob = this_gender_names[curr_name]
    return binarySearch(opposite_gender_names, curr_prob)


'''
What it does:
    Creates sets for male names and female names from files without probabilities attached to them
    Returns these sets 
'''
def createGenderedSets():
    maleNames = set()
    femaleNames = set()
    
    male_first_names_file = getTextfile('NamesAndSwapLists', 'male_first_names.txt')
    female_first_names_file = getTextfile('NamesAndSwapLists', 'female_first_names.txt')

    for line in male_first_names_file.readlines():
        maleNames.add(line.strip().lower())
    for line in female_first_names_file.readlines():
        femaleNames.add(line.strip().lower())


    ''''
    with open("../../NamesAndSwapLists/male_first_names.txt") as file:
        for line in file.readlines():
            maleNames.add(line.strip().lower())
    with open("../../NamesAndSwapLists/female_first_names.txt") as file:
        for line in file.readlines():
            femaleNames.add(line.strip().lower())
    '''

    return maleNames, femaleNames

'''
What it does:
    Reads in all the files from the U.S. Census Bureau data that has names and their probabilities
    Creates dictionaries -- maleNames and femaleNames -- that map names to their probabilities. These probabilities are averaged over 8 years of data.
    Creates lists -- maleNamesList and femaleNamesList -- that contain NameProbs with names and their probabilities
'''
def createGenderedSetsAndLists():
    os.chdir(dirname(abspath(__file__)))

    maleNames = dict()
    femaleNames = dict()
    maleNamesList = list()
    femaleNamesList = list()

    for i in range(8):
        curr_names_file = getTextfile('NamesAndSwapLists', 'yob201' + str(i) + '.txt')
        for line in curr_names_file.readlines():
            name, gender, probability = line.split(',')
            name = clean(name.strip().lower(), engine)
            probability = int(probability.strip())
            if(gender == 'M'):
                if name not in maleNames:
                    maleNames[name] = probability
                else:
                    maleNames[name] += probability
            elif(gender == 'F'):
                if name not in femaleNames:
                    femaleNames[name] = probability
                else:
                    femaleNames[name] += probability
            else:
                print("GENDER NOT VALID")
        curr_names_file.close()


    #normalize the counts
    for name in maleNames:
        maleNames[name] /= 8
        maleNamesList.append(NameProb(name, maleNames[name]))
    for name in femaleNames:
        femaleNames[name] /= 8
        femaleNamesList.append(NameProb(name, femaleNames[name]))

    return maleNames, femaleNames, sorted(maleNamesList), sorted(femaleNamesList)

'''
What it does:
    Creates a dictionary that maps a gendered word to its swap word (an equivalent word for the other gender)
'''
def createSwapDict():
    genderPairs = dict()
    gender_pairs_file = getTextfile('NamesAndSwapLists', 'swap_list_norepeats.txt') 
    for line in gender_pairs_file.readlines():
        word1, word2 = line.split()

        #put both pairs in so search is faster
        #space still won't be too big
        genderPairs[word1] = word2
        genderPairs[word2] = word1

    return genderPairs

'''
Parameters:
    replacement - the word to use as the replacement for curr_word
    curr_word - the word to be replaced in the line
    index_before_word - the index before the index on which curr_word starts
    line - the line we're replacing words in
What it does:
    replace curr_word with replacement and return the new line
    Ex: replaceInStr(was, am, 1, I was there) --> I am there
'''
def replaceInStr(replacement, curr_word, index_before_word, line):
    if not curr_word[-1].isalpha():
        replacement += curr_word[-1]
    new_line1 = line[0:index_before_word]
    new_line2 = line[index_before_word:].replace(curr_word, replacement, 1)
    new_line = new_line1 + new_line2
    return new_line


def join_punctuation(seq, characters='.,;?!:\\()-\''):
    characters = set(characters)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if nxt in characters:
            current += nxt
        else:
            yield current
            current = nxt

    yield current

'''
Parameters
    in_str - the file containing the strin we're genderswapping
    swap_names: true iff you want the function to swap the names as well using our name-swapping method
What it does:
    genderswaps the dataset and returns that genderswapped string
'''
def genderSwap(in_str, swap_names = False):
    #first, create necessary sets and lists
    maleNames, femaleNames, maleNamesList, femaleNamesList = createGenderedSetsAndLists()
    genderPairs = createSwapDict()

    lines = in_str.split('\n')
    out_str = ""
    # start reading in lines from the dataset
    for line in lines:
        i = 0
        print(line)
        words = word_tokenize(line)
        pos_tags = st.tag(words)
        for i in range(len(words)):
            word = clean(words[i], engine)
            if pos_tags[i][1] == 'PERSON':
                #then, this might be a name!
                #only try to swap that name if the swap_names parameter is True
                if(swap_names):
                    if word in maleNames and word in femaleNames:
                        if maleNames[word] > femaleNames[word]:
                            words[i] = getName(word, maleNames, femaleNamesList)
                        else:
                            words[i] = getName(word, femaleNames, maleNamesList)
                    elif word in maleNames:
                        words[i] = getName(word, maleNames, femaleNamesList)
                    elif word in femaleNames:
                        words[i] = getName(word, femaleNames, maleNamesList)
            elif word in genderPairs:
                words[i] = genderPairs[word]
        line = ' '.join(join_punctuation(words))
        out_str += line + "\n"
    return out_str

