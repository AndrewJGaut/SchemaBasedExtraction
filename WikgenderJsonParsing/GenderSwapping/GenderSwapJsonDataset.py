'''
What this file does:
    - Take in a JSON dataset (one for Wikigender)
    - Then, genderswap that JSON dataset
    - write to a new genderswapped file

Wikigender format:
{
'train':
 [ {
    entity1: NAME,
    relations: [
        {
            name: spouse,
            entity2: NAME,
            sentences: [
            ]
        }

    ]
} ],
'dev' : [ {
    entity1: NAME,
    relations: [
        {
            name: spouse,
            entity2: NAME,
            sentences: [
            ]
        }

    ]
}, ... ], ...
}
'''

import sys
sys.path.insert(0, './') # so we can get to genderSwap
sys.path.insert(0, '../') # so we can get to utility
from Utility import *
from genderSwap import *


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



if __name__ == '__main__':
    genderSwapDataset('../JsonData/Wikigender.json', '../JsonData/Wikigender_GenderSwapped.json')

