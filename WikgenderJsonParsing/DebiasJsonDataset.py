'''This file contains different debiasing methods for the json dataset including:
- gender-swapping
- name-anonymzation
- equalization of gender mentions thorugh sampling'''
from Utility import *
from genderSwap import *
from EqualizeThroughSampling import *

from nltk.tag import StanfordNERTagger
st = StanfordNERTagger('/Users/agaut/PycharmProjects/TestStuff/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                       '/Users/agaut/PycharmProjects/TestStuff/stanford-ner/stanford-ner-3.9.2.jar',
					   encoding='utf-8')

import inflect
engine = inflect.engine()


'''genderswapping'''
def genderSwapSubsetOfDataset(entries, swap_names):
    '''

    :param entries: a list of JSON dictionary objects from the dataset
            have the following format: [ {
                                            entity1: NAME,
                                            relations: [
                                                {
                                                    name: spouse,
                                                    entity2: NAME,
                                                    sentences: [
                                                    ]
                                                }

                                            },
                                            ...
                                        ]
    :param swap_names: if true, then the names will be gender-swapped as well
    :return: entries with all SENTENCES gender-swapped only
    '''
    for index in range(len(entries)):
        entry = entries[index] # get the current entry

        relations = entry['relations']
        for relation in relations:
            sentences = relation['sentences']
            for sentence_index in range(len(sentences)):
                sentence = sentences[sentence_index] # get current sentence
                genderswapped_sentence = genderSwap(sentence, swap_names)

                # now, save that genderswapped sentence where the original sentence was previously
                entry['relations']['sentences'][index] = genderswapped_sentence

        # now, set overwrite the old entry in entries with the new entry with gender_swapped sentences
        entries[index] = entry

    return entries



def genderSwapDataset(infile_name, outfile_name, swap_names=False):
    '''

    :param outfile_name: the name of the file to write the gender-swapped json data to
    :param infile_name: the file iwth the data to be gender-swapped; data should be in wikigender format (see top of file)
    :param swap_names: true if the names should be swapped as well
    :return: json_data with all sentences gender-swapped; also writes that data to the file with outfile_name
    '''

    # get data
    json_data = readFromJsonFile(infile_name)

    #overwrite with gender-swapped stuff
    json_data['train'] = genderSwapSubsetOfDataset(json_data['train'], swap_names)
    json_data['dev'] = genderSwapSubsetOfDataset(json_data['dev'], swap_names)
    json_data['male_test'] = json_data['male_test']
    json_data['female_test'] = json_data['female_test']

    # write to file
    writeToJsonFile(json_data, outfile_name)

    return json_data

'''end genderswapping'''



'''equalize mentions'''
def getSpecificEntries(entries, names):
    '''
    Parameters:
    - entries: an object representing all the entires in dict form
    Returns:
    - an object like entires but only containing entries that have names in the names hashset passed in
    '''
    specific_entries = list()

    for entry in entries:
        name = entry['entity1']
        if name in names:
            specific_entries.append(entry)

    return specific_entries


def getEqualizedEntriesThroughSampling(entries, male_names, female_names):
    '''

    :param entries: the list of JSON dictionary entries in the dataset; includes entity1, and all entity2,sentences pairs for each attribute
    :param male_names: hashset of male names from Wikipedia
    :param female_names: hashset of female names from wikipedia
    :return: entries, but with equalized gender numbers in train and dev set
                here, for example, if there are less male datapoints than female, then we duplicate the male datapoints until there are as many male as female datapoints
                note that we randomly sample to do this duplication, so the order is randomized
    '''
    # get male and female entries
    male_entries = getSpecificEntries(entries, male_names)
    female_entries = getSpecificEntries(entries, female_names)

    # find lesser of the two
    smaller_entries = male_entries
    larger_entries = female_entries
    if(len(female_entries) < len(male_entries)):
        smaller_entries = female_entries
        larger_entries = male_entries

    # now, randomly sample until the smaller thing has as many datapoints as the larger one
    added_entries = list()
    while(len(smaller_entries) + len(added_entries) < len(larger_entries)):
        random_sample = random.sample(smaller_entries, len(smaller_entries))

        index = 0
        while (index < len(smaller_entries) and len(smaller_entries) + len(added_entries) < len(larger_entries)):
            entries.append(random_sample[index])
            added_entries.append(random_sample[index])
            index += 1

    return entries


def createEqualizedJsonDataset(old_dataset_name, new_dataset_name):

    data = readFromJsonFile(old_dataset_name)

    male_names = getNamesFromFileToDict('../DBPedia/PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('../DBPedia/PersonData_ttl/female_names.txt')

    equalized_train_data = getEqualizedEntriesThroughSampling(data['train'], male_names, female_names)
    equalized_dev_data = getEqualizedEntriesThroughSampling(data['dev'], male_names, female_names)
    male_test_data = data['male_test']  # this stays constant
    female_test_data = data['female_test']  # this stays constant

    # just overwrite the old stuff in data
    data['train'] = equalized_train_data
    data['dev'] = equalized_dev_data
    data['male_test'] = male_test_data
    data['female_test'] = female_test_data

    # write to file
    writeToJsonFile(data, new_dataset_name)


'''end equalize mentions'''


'''name anonymization'''

def clean(str, infl):
    '''
    What it does:
        Removes all non-alphanumerics from word AND makes the word singular (not plural)
        Used to check if words are in the set
    '''
    cleanStr = ""
    for char in str:
        if(char.isalpha()):
            cleanStr += char.lower()
    if(infl.singular_noun(cleanStr)):
        cleanStr = infl.singular_noun(cleanStr)

    return cleanStr

def createNameAnonymizationDict(input_str):
    names_2_anonymizations = dict()
    name_counter = 0
    for sentence in nltk.sent_tokenize(input_str):
        pos_tags = st.tag(nltk.word_tokenize(sentence))
        for i in range(len(pos_tags)):
            if pos_tags[i][1] == 'PERSON':
                # then, this is a person
                name = clean(pos_tags[i][0], engine)
                print(str(name))
                if name not in names_2_anonymizations:
                    names_2_anonymizations[name] = "E" + str(name_counter)
                    name_counter += 1

    return names_2_anonymizations


def nameAnonymizeStr(input_str, names_2_anonymizations):
    '''
    This takes str and replaces all names in str with their corresponding anonymizations
    This function should ONLY be called after createAnonymizationDict was run on input_str, and names_2_anonymizations should be return value from CreateAnonymizationDict(input_str)
    '''
    out_str = ""

    for line in input_str.split('\n'):
        words = nltk.word_tokenize(line)
        for i in range(len(words)):
            word = clean(words[i], engine)
            if word in names_2_anonymizations:
                words[i] = names_2_anonymizations[word]
        out_str += ' '.join(words) + "\n"

    return out_str



def nameAnonymize(dataset_path, out_path):
    '''
    Replaces all names in dataset with E1, E2, ..., En (if there are n entities in the dataset) using a mapping
    Then returns a new dataset
    '''
    dataset = getTextfile('NamesAndSwapLists', dataset_path)

    # first, we need to read through the dataset and map names to anonymizations
    names_2_anonymizations = createNameAnonymizationDict(dataset.read())
    print('NAME ANONYMIZE DICT CREATED')

    #now, we need to anonymize the dataset
    new_dataset = nameAnonymizeStr(dataset.read(), names_2_anonymizations)
    print("NEW DATASET CREATED")

    #now, write to file
    #out_file = open(dataset_path[:-4] + "_nameanonymized.txt", 'w')
    out_file = open(out_path, 'w')
    out_file.write(new_dataset)

'''end name anonymization'''




'''main'''
if __name__ == '__main__':
    pass