'''This file creates the Excel sheet that is our dataset'''

from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys



'''
Precondition:
    person_file_path is the name of a file with person names for one gender
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
    browser is a selenium web browser
Postcondition:
    Creates an Excel spreadsheet with columns:
    PersonName Attribute1 Attribute2 ... AttributeN
    and with all entries filled in
'''
def createDataset(person_file_path, attribs, dataset_name, browser):
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
                attribs_2_sentences = getSentences(browser, name, attribute_vals)
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
        '''
        if(row_counter % 200 == 0):
            dataset.save('AttributeDatasets/' + dataset_name + "_" + person_file_path + "_" + ".xls")
        '''
        if(row_counter >= 100):
            break
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
def createDatasetSortByHypernym(person_file_path, hypernym, attribs, dataset_name, browser):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    for i in range(len(attribs)):
        dataset_sheet.write(0, (i+1), attribs[i])



    # get file to read names from
    person_file = open(person_file_path, 'r')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    for line in person_file.readlines():
        name = formatName(line.strip())
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
            attribute_vals = list()
            for i in range(0, len(attribs)):
                attribute_vals.append((attribs[i], curr_person_attribs[i]))
            attribs_2_sentences = getSentences(browser, name, attribute_vals)
            for attrib in attribs_2_sentences:
                if not attribs_2_sentences[attrib]:
                    write = False
                    break
            if(write):
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
    person_name is the name of the person for which you want sentences
    attrib_vals is a list of tuples (atribute, attr_value)
    browser is a selenium web browser
Postcondition:
    returns a dictionary that maps attrib --> list of sentences
'''
def getSentences(browser, person_name, attrib_vals):
    attribs_2_sentences = defaultdict(list)

    article = getArticleForPerson(person_name, browser)
    for sentence in nltk.sent_tokenize(article):
        for attrib_val in attrib_vals:
            if attrib_val[1] in sentence:
              attribs_2_sentences[attrib_val[0]].append(sentence)

            #special rules (because often Infobox relations are more formal than Wikipedia article writing
            if attrib_val[0] == 'birthDate':
                if formatDate2(attrib_val[1]) in sentence:
                    attribs_2_sentences[attrib_val[0]].append(sentence)
            if attrib_val[0] == 'spouse':
                if attrib_val[1].split()[0] in sentence:
                    attribs_2_sentences[attrib_val[0]].append(sentence)
            if attrib_val[0] == 'birthPlace':
                if attrib_val[1].split(',')[0] in sentence:
                    attribs_2_sentences[attrib_val[0]].append(sentence)


    return attribs_2_sentences


if __name__ == '__main__':
    print('running')

    # define selenium browser for scraping
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)
    #createDataset('test_data.txt', ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'sent_test', browser)
    createDataset('PersonData_ttl/male_names.txt', ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'sent_test', browser)
    #createDataset('testdata2.txt', ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'sent_test', browser)
    #createDataset(sys.argv[1], ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'nohypernym_full_train', browser)
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Politican', ['party', 'religion', 'predecessor'], 'test_h')
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Player', ['weight', 'team','position', 'number'], 'test_h2')
    #print(sys.argv[1])

    '''test'''


    #print(getSentences(browser, 'Barack Obama', [('spouse', 'Michelle')]))
    '''seems to work'''





