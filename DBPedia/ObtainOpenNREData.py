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
        new_sentence += word.lower() + " "

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
Precondition:
    relations is a list of ALL the relations we've obtained
    each relation in relations is a tuple (relation, entity1, entity2, sentence)
Postcondition:
    creates train.json and rel2id.json files
'''
def createOpenNREFiles(relations):
    # files to write to later
    training_json = open('OpenNRETrainingData/train.json', 'w')
    rel_to_id = open('OpenNRETrainingData/rel2id.json', 'w')


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

    # get relation to id mapping data
    relation_to_id_mapping_string = "{\n\t\"NA\": 0,\n"
    rel_counter = 1
    for rel in unique_relations:
        relation_to_id_mapping_string += "\t\"" + str(rel) + "\": " + str(rel_counter) + ",\n"
        rel_counter += 1
    relation_to_id_mapping_string = relation_to_id_mapping_string[0:-2]
    relation_to_id_mapping_string += "\n}"

    #write to files
    training_json.write(training_json_string)
    training_json.close()

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
Precondition:
    dataset_path is a path to an Excel dataset with sturctured data from a KB
Postcondition:
    returns a list of tuples (relation_type, entity1, entity2, sentence) from that dataset
'''
def readDataFromDBPediaDataset(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    dataset_sheet = dataset.sheet_by_index(0)

    # get the types of relations
    relation_types = list()
    for i in range(1, dataset_sheet.ncols):
        relation_types.append(dataset_sheet.cell_value(0, i))

    relations = list() # list of relations
    i = 1
    while i < dataset_sheet.nrows:

        #first, get the number of rows until next entity
        curr_row = i + 1
        while(curr_row < dataset_sheet.nrows and dataset_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        #now, get entity name
        e1 = dataset_sheet.cell_value(i,0)
        print("CURR NAME: " + e1)

        #get list of e2s by column
        e2_vals = list()
        for j in range(1, dataset_sheet.ncols):
            e2_vals.append(dataset_sheet.cell_value(i,j))

        #now, get the tuples
        prev_i = i
        i += 1
        while(i < prev_i + entity_rows and i < dataset_sheet.nrows):
            for j in range(1, dataset_sheet.ncols):
                if dataset_sheet.cell_value(i, j) != "":
                    print("getting sentence...")
                    relation = (relation_types[j-1], e1, e2_vals[j-1], opennreFormatSentence(dataset_sheet.cell_value(i,j)))
                    relations.append(relation)
            i += 1

    print("done getting relations")

    return relations


'''
Precondition:
    e1_2_relation is a dict mapping entities to relations found from THEIR DBPedia page! e.g. if I find a relation on Barack Obama's DBPedia page, then e1_2_rel[Barack Obama] should give a list of relation tuples
    browser is a selenium browser used for web scarping
Postcondition:
    returns a list of full relation tuples (i.e. relation tuples that contain the sentence that gives that relation)
    Relation tuples are of the form: (relation, entity1, entity2, sentence)
NOTE!!!: make more efficient by only looping through article once for each e1 (i.e. look for all e2s in each sentence and map e2 to its relation)
'''
def getFullRelationTuples(e1_2_relation, browser):
    relations = list()

    for e1, relation_list in e1_2_relation.items():
        article = getArticleForPerson(e1, browser)

        for relation in relation_list:
            try:
                e1 = lemmatize(relation[1])
                e2 = lemmatize(relation[2])
                #e1 = relation[1]
                #e2 = relation[2]

                for sentence in nltk.sent_tokenize(article):
                    if(e2 in sentence): #we ONLY check if e2 in sentence since this Obama's article!
                        sentence = opennreFormatSentence(sentence)
                        relations.append((relation[0], e1, e2, sentence))
            except:
                print("BAD RELATION")

    return relations



if __name__ == '__main__':
    # get entities and abridged relations from dataset
    #relations = readDataFromDBPediaDataset('AttributeDatasets/Politican_test_h.xls')
    relations = readDataFromDBPediaDataset('AttributeDatasets/nohypernym_full_train_PersonData_ttl_female_names.txt_fixed.xls')

    # create training files for OpenNRE
    createOpenNREFiles(relations)


    #createOpenNREFiles([('spouse', 'Barack', 'Michelle', 'Barack is Michelle\'s husband'), ('father', 'John', 'Smitty', 'John fathered Smitty in 1852.'), ('father', 'Barack', 'Jeff', 'Barack fathered Jeff in 1852.')])
   # formatWordVectorFile('vectors.txt')