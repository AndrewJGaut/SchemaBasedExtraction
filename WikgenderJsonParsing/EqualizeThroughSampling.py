import json
import random
from Utility import *

DataTypes = ['train', 'dev', 'male_test', 'female_test']


'''
Parameters:
- entries: an object representing all the entires in dict form
Returns:
- an object like entires but only containing entries that have names in the names hashset passed in
'''
def getSpecificEntries(entries, names):
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




if __name__ == '__main__':
    createEqualizedJsonDataset('JsonData/Wikigender.json', 'JsonData/Wikigender_GenderEqualized.json')

    data = readFromJsonFile('JsonData/Wikigender_GenderEqualized.json')
    male_names = getNamesFromFileToDict('../DBPedia/PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('../DBPedia/PersonData_ttl/female_names.txt')
    male_entries = getSpecificEntries(data['train'], male_names)
    female_entries = getSpecificEntries(data['train'], female_names)

    print(len(male_entries))
    print(len(female_entries))

