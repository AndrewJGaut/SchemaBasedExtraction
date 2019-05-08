from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import nltk
from TextPreprocessing import *
from ParseDBPedia import *
from random import randint
import string
import xlrd
from collections import defaultdict


'''
Precondition:
    name is the name of a person with a Wikipedia article
    browser is a Chrome, Selenium webdriver
Postcondition:
    Returns the full text of that person's Wikipedia article
'''
def getArticleForPerson(name, browser):
    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    return curr_article_text




'''
Precondition:
    sentence is a string of English
Postcondition:
    formats sentence for OpenNRE model
'''
def opennreFormatSentence(sentence):
    new_sentence = ""
    for word in nltk.word_tokenize(sentence):
        new_sentence += word + " "

    return new_sentence



'''
Postcondition:
    Returns an entity id for training data compatible with OpenNRE
'''
def genId():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    id = "m."

    for i in range(5):
        id += chars[randint(0, 35)]

    return id


'''
Create the actual train or test or dev file from list of relations tuples
'''
def createOpenNRESplitFile(relations, split_type):
    # files to write to later
    training_json = open('OpenNRETrainingData/' + split_type + '.json', 'w')

    names2ids = dict()
    ids_in_use = set()
    unique_relations = set()
    training_json_string = "[\n"


    id_e1 = ""
    id_e2 = ""
    for relation in relations:
        try:
            # give entities ids!
            if relation[1] not in names2ids:
                while True:
                    id_e1 = genId()
                    if id_e1 not in ids_in_use:
                        break
                names2ids[relation[1]] = id_e1
            else:
                id_e1 = names2ids[relation[1]]

            if relation[2] not in names2ids:
                id_e2 = ""
                while True:
                    id_e2 = genId()
                    if id_e2 not in ids_in_use:
                        break
                names2ids[relation[2]] = id_e2
            else:
                id_e2 = names2ids[relation[2]]

            # get relations (so we can map to ids later)
            if relation[0] not in unique_relations:
                unique_relations.add(relation[0])


            # add to the training_json string
            training_json_string += "\t{" + "\n"
            training_json_string += "\t\t\"sentence\": " + "\"" + str(relation[3]) + "\",\n"
            training_json_string += "\t\t\"head\": {\"word\": " + "\"" + str(relation[1]) + "\", \"id\": \"" + id_e1 + "\"},\n"
            training_json_string += "\t\t\"tail\": {\"word\": " + "\"" + str(relation[2]) + "\", \"id\": \"" + id_e2 + "\"},\n"
            training_json_string += "\t\t\"relation\": \"" + relation[0] + "\"\n"
            training_json_string += "\t},\n"
        except:
            print("BAD RELATION")

    training_json_string = training_json_string[0:-2]
    training_json_string += "\n]"

    # write to files
    training_json.write(training_json_string)
    training_json.close()

    return unique_relations

'''
Precondition:
    relations is a list of ALL the relations we've obtained
    each relation in relations is a tuple (relation, entity1, entity2, sentence)
Postcondition:
    creates train.json and rel2id.json files
'''
def createOpenNREFiles(relations):
    #create splits files
    unique_relations = createOpenNRESplitFile(relations[0], 'train')
    createOpenNRESplitFile(relations[1], 'dev')
    createOpenNRESplitFile(relations[2], 'test')

    #training_json = open('OpenNRETrainingData/dev.json', 'w')
    rel_to_id = open('OpenNRETrainingData/rel2id.json', 'w')


    # get relation to id mapping data
    relation_to_id_mapping_string = "{\n\t\"NA\": 0,\n"
    rel_counter = 1
    for rel in unique_relations:
        if rel == 'NA': continue
        relation_to_id_mapping_string += "\t\"" + str(rel) + "\": " + str(rel_counter) + ",\n"
        rel_counter += 1
    relation_to_id_mapping_string = relation_to_id_mapping_string[0:-2]
    relation_to_id_mapping_string += "\n}"



    rel_to_id.write(relation_to_id_mapping_string)
    rel_to_id.close()

'''
Precondition:
    vec_file is a word vector file of the form word num1 num2 ... numn \n word2 num1 ...etc
Postcondition:
    formats vector file so it works for OpenNRE
'''
def formatWordVectorFile(vec_file):
    formatted_word_vecs_string = "[\n"

    file = open(vec_file, 'r')
    for line in file.readlines():
        items = line.split()
        print(items[0])
        formatted_word_vecs_string += "\t{\"word\": \"" + str(items[0]) + "\",\"vec\": ["
        for i in range(1, len(items)):
            formatted_word_vecs_string += str(items[i]) + ", "
        formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
        formatted_word_vecs_string += "]},\n"

    formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
    formatted_word_vecs_string += "}\n]"

    out_file = open(vec_file + "_formatted.json", 'w')
    out_file.write(formatted_word_vecs_string)


'''
Returns the list of tuples of the relations found in the sheet passed in as a parameter
'''
def getRelationsFromSheet(dataset_sheet, relation_types):
    relations = list()  # list of relations
    i = 1
    while i < dataset_sheet.nrows:

        # first, get the number of rows until next entity
        curr_row = i + 1
        while (curr_row < dataset_sheet.nrows and dataset_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # now, get entity name
        e1 = dataset_sheet.cell_value(i, 0)
        print("CURR NAME: " + e1)

        # get list of e2s by column
        e2_vals = list()
        for j in range(1, dataset_sheet.ncols):
            e2_vals.append(dataset_sheet.cell_value(i, j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < dataset_sheet.nrows):
            for j in range(1, dataset_sheet.ncols):
                if dataset_sheet.cell_value(i, j) != "":
                    print("getting sentence...")
                    relation = (
                    relation_types[j - 1], e1, e2_vals[j - 1], opennreFormatSentence(dataset_sheet.cell_value(i, j)))
                    relations.append(relation)
            i += 1

    print("done getting relations")

    return relations


'''
Returns the list of tuples of the relations found in the sheet passed in as a parameter
BUT this function works with multiple e2s for NA relations which is found in AMT data!
'''
def getRelationsFromAMTTestSheet(dataset_sheet, relation_types):
    relations = list()  # list of relations
    i = 1
    while i < dataset_sheet.nrows:

        # first, get the number of rows until next entity
        curr_row = i + 1
        while (curr_row < dataset_sheet.nrows and dataset_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # now, get entity name
        e1 = dataset_sheet.cell_value(i, 0)
        print("CURR NAME: " + e1)

        # get list of e2s by column
        e2_vals = list()
        for j in range(1, dataset_sheet.ncols):
            e2_vals.append(dataset_sheet.cell_value(i, j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < dataset_sheet.nrows):
            for j in range(1, dataset_sheet.ncols):
                if dataset_sheet.cell_value(i, j) != "":
                    print("getting sentence...")
                    if e1 == 'John Key':
                        test = 1

                    rel_type = ""
                    if j >= len(relation_types) - 1:
                        rel_type = "NA"
                    else:
                        rel_type = relation_types[j - 1]
                    relation = (rel_type, e1, e2_vals[j - 1], opennreFormatSentence(dataset_sheet.cell_value(i, j)))
                    relations.append(relation)
            i += 1

    print("done getting relations")

    return relations

'''
Precondition:
    dataset_path is path to a dataset obtained from labelled AMT data (i.e. it can have multiple e2 values for NA relation)
Postcondition:
    creates JSON testing file for OpenNRE from AMT labelled data
'''
def getOpenNRETestDataFromAMT(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    test_sheet = dataset.sheet_by_index(0)

    # get the types of relations
    relation_types = list()
    for i in range(1, test_sheet.ncols):
        relation_types.append(test_sheet.cell_value(0, i))

    rels = getRelationsFromAMTTestSheet(test_sheet, relation_types)
    createOpenNRESplitFile(rels, 'test')

'''
Precondition:
    dataset_path is a path to an Excel dataset with sturctured data from a KB
    that dataset must also have 3 sheets, the first being the training set, second being dev, and 3rd being test
Postcondition:
    returns a 3 lists of tuples (relation_type, entity1, entity2, sentence) from that dataset, one for training, one for dev,and one for testing
'''
def readDataFromDBPediaDataset(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    train_sheet = dataset.sheet_by_index(0)
    dev_sheet = dataset.sheet_by_index(1)
    test_sheet = dataset.sheet_by_index(2)

    # get the types of relations
    relation_types = list()
    for i in range(1, train_sheet.ncols):
        relation_types.append(train_sheet.cell_value(0, i))

    train_rels = getRelationsFromSheet(train_sheet, relation_types)
    dev_rels = getRelationsFromSheet(dev_sheet, relation_types)
    test_rels = getRelationsFromSheet(test_sheet, relation_types)
    return [train_rels, dev_rels, test_rels]




if __name__ == '__main__':

    #get relations from the dataset with the train, dev, test splits
    relations = readDataFromDBPediaDataset('test_split.xls')

    # create training files for OpenNRE
    createOpenNREFiles(relations)

    # rewrite test data so it has ground truth distribution from AMT annotations
    getOpenNRETestDataFromAMT('AttributeDatasets/TEST2.xls')