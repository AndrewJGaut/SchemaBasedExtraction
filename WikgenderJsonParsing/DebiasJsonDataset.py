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



def createGenderSwappedDataset(infile_name, outfile_name, swap_names=False):
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

def createGenderSwappedDatasetEntries(json_data, swap_names=False):
    '''

    :param data: data in wikigender format
    :param swap_names: true if the names should be swapped as well
    :return: json_data with all sentences gender-swapped; also writes that data to the file with outfile_name
    '''
    #overwrite with gender-swapped stuff
    json_data['train'] = genderSwapSubsetOfDataset(json_data['train'], swap_names)
    json_data['dev'] = genderSwapSubsetOfDataset(json_data['dev'], swap_names)
    json_data['male_test'] = json_data['male_test']
    json_data['female_test'] = json_data['female_test']

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
    '''
    :param old_dataset_name:
    :param new_dataset_name:
    :return:
    '''

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

    return data

def createEqualizedJsonDatasetEntries(data):
    '''
    :param data: json data from Wikigender style file
    :return: that data with equalized entries
    '''
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

    return data


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

def addNameToAnonymizationDict(input_str, dictionary, name_counter):
    '''

    :param input_str: striong representing name
    :param dictionary: names_2_anonymizaiton dicitonary mapping name to E + number (dictionary[Mary] --> E1)
    :param name_counter: tells us what number name it is (for the E + number anoymized name)
    :return: the dictionary with name added and name_counter
    '''

    # split the name up and add each thing separetly
    names = nltk.word_tokenize(input_str)
    for name in names:
        name = clean(name, engine)
        if name not in dictionary:
            dictionary[name] = "E" + str(name_counter)
            name_counter += 1

    return dictionary, name_counter



def createNameAnonymizationDict(entries):
    '''

    :param entries: json data to be anonymized later in teh foloowing format:
                                        [ {
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
    :return: A dict mapping names in input_str to anonymized names (e.g. dict[Mary] = E1, dict[John] = E2, etc.)
    Note: we assume that any entity2 for the spouse relation will be a name and any entity1 is a name! (this should alwasy be true; both of these should be people)
    '''
    names_2_anonymizations = dict()
    name_counter = 0

    for index in range(len(entries)):
        entry = entries[index] # get the current entry

        # add entity 1
        names_2_anonymizations, name_counter = addNameToAnonymizationDict(entry['entity1'], names_2_anonymizations, name_counter)

        relations = entry['relations']
        for relation in relations:
            relation_name = relation['relation_name']
            if 'spouse' in clean(relation_name, engine):
                # then, we want to get anonymization dict for entity2
                names_2_anonymizations, name_counter = addNameToAnonymizationDict(relation['entity2'], names_2_anonymizations, name_counter)

            # now get anonymization dict for all the sentences
            sentences = relation['sentences']
            for sentence_index in range(len(sentences)):
                sentence = sentences[sentence_index] # get current sentence
                pos_tags = st.tag(nltk.word_tokenize(sentence))
                for i in range(len(pos_tags)):
                    if pos_tags[i][1] == 'PERSON':
                        # then, this is a person
                        clean_name = clean(pos_tags[i][0], engine)
                        names_2_anonymizations, name_counter = addNameToAnonymizationDict(clean_name, names_2_anonymizations,name_counter)

    return names_2_anonymizations


def nameAnonymizeJson(entries, names_2_anonymizations):
    '''
    :param entries:
    :param names_2_anonymizations:
    :return:
    '''
    for index in range(len(entries)):
        entry = entries[index]  # get the current entry

        # anonymize e1
        entry['entity1'] = nameAnonymizeStr(clean(entry['entity1'], engine), names_2_anonymizations)

        relations = entry['relations']
        for relation_index in range(len(relations)):
            relation = relations[relation_index]
            relation_name = relation['name']
            if 'spouse' in clean(relation_name, engine):
                # then, anonymize entity2
                entry['relations'][relation_index] = nameAnonymizeStr(clean(entry['relations'][relation_index]['entity2'], engine), names_2_anonymizations)

            # now anonymize all the sentences
            sentences = relation['sentences']
            for sentence_index in range(len(sentences)):
                entry['relations'][relation_index]['sentences'][sentence_index] = nameAnonymizeStr(clean(sentence, engine), names_2_anonymizations)

        entries[index] = entry
    return entries

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

def nameAnonymizeSubsetOfDataset(entries):
    '''
    :param entries: colletion of json data; should be data['train'] or data[some_key], NOT data itself
    :return: those entries name anonymized
    '''
    names_2_anonymizations = createNameAnonymizationDict(entries)
    return nameAnonymizeJson(entries, names_2_anonymizations)


def createNameAnonymizedJsonDataset(infile_name, outfile_name):
    '''
    Replaces all names in dataset with E1, E2, ..., En (if there are n entities in the dataset) using a mapping
    Then returns a new dataset
    '''
    data = readFromJsonFile(infile_name)

    #now, we need to anonymize the dataset
    data['train'] = nameAnonymizeSubsetOfDataset(data['train'])
    data['dev'] = nameAnonymizeSubsetOfDataset(data['dev'])
    data['male_test'] = nameAnonymizeSubsetOfDataset(data['male_test'])
    data['female_test'] = nameAnonymizeSubsetOfDataset(data['female_test'])

    # write to file
    writeToJsonFile(data, outfile_name, True)

    # now, return the data
    return data

def createNameAnonymizedJsonDatasetEntries(data):
    '''
    :param data: data in wIkigender format
    :return: input data with name anonymization applied
    '''
    #now, we need to anonymize the dataset
    data['train'] = nameAnonymizeSubsetOfDataset(data['train'])
    data['dev'] = nameAnonymizeSubsetOfDataset(data['dev'])
    data['male_test'] = nameAnonymizeSubsetOfDataset(data['male_test'])
    data['female_test'] = nameAnonymizeSubsetOfDataset(data['female_test'])

    # now, return the data
    return data

'''end name anonymization'''


def createDebiasedDataset(infile_name, equalized=False, name_anonymized=False, gender_swapped=False, swap_names=False):
    '''
    :param infile_name: file that holds the original, unaltered json dataset (should be in Wikigender format)
    :param equalized: boolean flag; if true, the returned data will have equalized mentions
    :param name_anonymized: boolean flag; if true, the returned data will be name anonymized
    :param gender_swapped: boolean flag; if true, the returned data will be gender-swapped
    :param swap_names: boolean flag; if true, and gender_swapped is true, then returend data will be gender-swapped with names also gender-swapped
    :return: the debiased dataset, with the debiasing customized based on input flags
    '''
    data = readFromJsonFile(infile_name)
    infile_names = infile_name.split('.')

    if equalized:
        data = createEqualizedJsonDatasetEntries(data)
        infile_names[0] += "_Eq"
    else:
        infile_names[0] += "_NoEq"
    if name_anonymized:
        data = createNameAnonymizedJsonDatasetEntries(data)
        infile_names[0] += "_NA"
    else:
        infile_names[0] += "_NoNA"
    if gender_swapped:
        data = createGenderSwappedDatasetEntries(data, swap_names)
        infile_names[0] += "_GS"
        if swap_names:
            infile_names[0] += "_NS"
        else:
            infile_names[0] += "_NoNS"
    else:
        infile_names[0] += "_NoGS"

    # write the new dataset
    outfile_name = infile_names[0] + "." + infile_names[1]
    writeToJsonFile(data, outfile_name)

    return data

'''main'''
if __name__ == '__main__':
    # now, create the different datasets
