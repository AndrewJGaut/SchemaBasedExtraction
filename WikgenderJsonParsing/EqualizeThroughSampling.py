import json
import random

DataTypes = ['train', 'dev', 'male_test', 'female_test']

def writeToJsonFile(data, outfile_name, prettify=False):
    with open(outfile_name, 'w') as outfile:
        if(prettify):
            json.dump(data, outfile, indent=4, sort_keys=True)
        else:
            json.dump(data, outfile)

def readFromJsonFile(infile_name):
    with open(infile_name, 'r') as infile:
        return json.load(infile)
    return ""


def getNamesFromFileToDict(filename):
    file = open(filename, 'r')
    namesDict = set()

    for line in file.readlines():
        namesDict.add(line.strip())

    return namesDict

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

    '''
    # add all entries from smaller set twice if we have to
    number_of_additions = int(larger_entries / smaller_entries)
    for i in range(number_of_additions):
        for entry in smaller_entries:
            entries.append(entry)
    '''

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
