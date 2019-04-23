'''This file creates the Excel sheet that is our dataset'''

import sys
sys.path.insert(0, '../../DBPedia/')

from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options




'''
Precondition:
    person_file_path is the name of a file with person names for one gender
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
    article_file is the path to the file containing all the Wiki articles
Postcondition:
    Creates an Excel spreadsheet with columns:
    PersonName Attribute1 Attribute2 ... AttributeN
    and with all entries filled in
'''
def createDataset(person_file_path, attribs, dataset_name, article_file):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    for i in range(len(attribs)):
        dataset_sheet.write(0, (i+1), attribs[i])



    # get file to read names from
    person_file = open(person_file_path, 'r')

    # elinimate issues with saving file name later
    person_file_path = person_file_path.replace('/', '_')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    for line in person_file.readlines():
        name = formatName(line.strip())
        print(name)
        curr_person_attribs = list()
        write = True
        for attrib in attribs:
            curr_person_attrib = getAttributeForPerson(name, attrib)
            if(curr_person_attrib == "ERROR: could not find attribute"):
                # if this is true, then this person doesn't have all the attributes we want; thus, we discard this data point
                write = False
                break
            curr_person_attribs.append(getAttributeForPerson(name, attrib))

        try:
            if(write):
                print(str(name) + "HAS ALL ATTRIBUTES")
                attribute_vals = list()
                for i in range(0, len(attribs)):
                    attribute_vals.append((attribs[i], curr_person_attribs[i]))
                attribs_2_sentences = getSentences(article_file, name, attribute_vals)
                for attrib in attribs:
                    if not attribs_2_sentences[attrib]:
                        write = False
                        break
            if(write):
                print(str(name) + "HAS ALL SENTENCES")
                #now, write person to excel sheet
                dataset_sheet.write(row_counter, 0, line.strip())
                for i in range(len(curr_person_attribs)):
                    dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
                row_counter = row_counter + 1

                max_row = 0
                temp_row_counter = row_counter
                for attrib in attribs_2_sentences:
                    col = attribs.index(attrib) + 1
                    for sentence in attribs_2_sentences[attrib]:
                        dataset_sheet.write(temp_row_counter, col, sentence)
                        temp_row_counter += 1
                    if temp_row_counter > max_row:
                        max_row = temp_row_counter
                    temp_row_counter = row_counter

                row_counter = max_row
        except Exception as e:
            print("ERROR  for " + str(name) + ": " + str(e))
            continue

        # save intermittently
        if(row_counter % 200 == 0):
            dataset.save('AttributeDatasets/' + dataset_name + "_" + person_file_path + "_" + ".xls")
    dataset.save('AttributeDatasets/' + dataset_name + "_" + person_file_path + "_" + ".xls")


'''
Precondition:
    person_file_path is the name of a file with person names for one gender
    hypernym is the category the person fits into
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
Postcondition:
    Creates an Excel spreadsheet with columns:
    PersonName Attribute1 Attribute2 ... AttributeN
    and with all entries filled in
'''
def createDatasetSortByHypernym(person_file_path, hypernym, attribs, dataset_name, article_file):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    for i in range(len(attribs)):
        dataset_sheet.write(0, (i+1), attribs[i])



    # get file to read names from
    person_file = open(person_file_path, 'r')

    # elinimate issues with saving file name later
    person_file_path = person_file_path.replace('/', '_')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    for line in person_file.readlines():
        name = formatName(line.strip())
        print(name)
        curr_person_attribs = list()
        write = True
        for attrib in attribs:
            curr_person_attrib = getAttributeForPerson(name, attrib)
            if(curr_person_attrib == "ERROR: could not find attribute"):
                # if this is true, then this person doesn't have all the attributes we want; thus, we discard this data point
                write = False
                break
            curr_person_attribs.append(getAttributeForPerson(name, attrib))

        if(write):
            print("HAS ALL ATTRIBUTES")
            #now, write person to excel sheet
            dataset_sheet.write(row_counter, 0, line.strip())
            for i in range(len(curr_person_attribs)):
                dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
            #row_counter += 1

            '''here, we need to write all the sentences'''
            # form list of attribute_vals tuples
            attribute_vals = list()
            for i in range(0, len(attribs)):
                # attribute_vals.append((dataset_sheet.cell(0, i), (dataset_sheet.cell(row_counter, i))))
                attribute_vals.append((attribs[i], curr_person_attribs[i]))
            try:
                attribs_2_sentences = getSentences(article_file, name, attribute_vals)
                max_row = 0
                temp_row_counter = row_counter + 1
                for attrib in attribs_2_sentences:
                    col = attribs.index(attrib) + 1
                    for sentence in attribs_2_sentences[attrib]:
                        dataset_sheet.write(temp_row_counter, col, sentence)
                        temp_row_counter += 1
                    if temp_row_counter > max_row:
                        max_row = temp_row_counter
                    temp_row_counter = row_counter + 1

                row_counter = max_row
            except:
                print("ERROR getting sentences for: " + str(name))
                continue
            # save intermittently
            if (row_counter % 200 == 0):
                dataset.save('AttributeDatasets/' + hypernym + "_" + dataset_name + "_" + person_file_path + ".xls")
    dataset.save('AttributeDatasets/' + hypernym + "_" + dataset_name + "_" + person_file_path + ".xls")



'''
Precondition:
    article_file is the file with all Wiki articles for all entities which can be in the process of being created when function is called
    person_name is name of entity
    period is amount of time to sleep between queries
'''
def wait_until_sentences_ready(article_file, person_name, timeout, period):
    print("waiting...")
    mustend = time.time() + timeout
    while time.time() < mustend:
        # article = getArticleForPerson(person_name, browser)
        articles_file = open(article_file, 'r', os.O_NONBLOCK)
        article = ""
        for line in articles_file:
            if line.strip() == person_name:
                article = next(articles_file)
        if article != "":
            return article
        time.sleep(period)
    print("NO ARTICLE FOUND")
    return "NO ARTICLE"


'''
Precondition:
    article_file is the name of the file with all WIkipedia articles
    person_name is the name of the person for which you want sentences
    attrib_vals is a list of tuples (atribute, attr_value)
Postcondition:
    returns a dictionary that maps attrib --> list of sentences
'''
def getSentences(article_file, person_name, attrib_vals):

    attribs_2_sentences = defaultdict(list)

    try:
        article = wait_until_sentences_ready(article_file, person_name, 90, 0.5)
        if (article != "NO ARTICLE"):
            #print("ARTICLE EXISTS: " + str(article))
            for sentence in nltk.sent_tokenize(article):
                for attrib_val in attrib_vals:
                    if attrib_val[1] in sentence:
                        attribs_2_sentences[attrib_val[0]].append(sentence)
        else:
            print("ARTICLES NOT FOUND FOR " + str(person_name))
        return attribs_2_sentences
    except Exception as e:
        print("ERROR GETTING SENTENCES FOR " + str(person_name) + "; error: " + str(e))



if __name__ == '__main__':
    print('running')

    # define selenium browser for scraping
    '''
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(chrome_options=options)
    '''
    createDataset('largescale_test.txt', ['hypernym', 'spouse','birthDate', 'birthPlace'], 'test_multi_proc', 'wiki_files.txt')
    #createDataset(sys.argv[1], ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'sent_test', browser)
    #createDataset(sys.argv[1], ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'nohypernym_full_train', browser)
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Politican', ['party', 'religion', 'predecessor'], 'test_h')
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Player', ['weight', 'team','position', 'number'], 'test_h2')





