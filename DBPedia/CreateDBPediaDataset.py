'''This file creates the Excel sheet that is our dataset'''

from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options



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

        if(write):
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
            attribs_2_sentences = getSentences(browser, name, attribute_vals)
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

        # save intermittently
        if(row_counter % 200 == 0):
            dataset.save('AttributeDatasets/' + dataset_name + ".xls")
    dataset.save('AttributeDatasets/' + dataset_name + ".xls")


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

        if(write):
            #now, write person to excel sheet
            dataset_sheet.write(row_counter, 0, line.strip())
            for i in range(len(curr_person_attribs)):
                dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
            #row_counter += 1

            '''here, we need to write all the sentences'''
            # form list of attribute_vals tuples
            attribute_vals = list()
            for i in range(0, len(attribs)):
                #attribute_vals.append((dataset_sheet.cell(0, i), (dataset_sheet.cell(row_counter, i))))
                attribute_vals.append((attribs[i], curr_person_attribs[i]))
            attribs_2_sentences = getSentences(browser, name, attribute_vals)
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



            # save intermittently
            if (row_counter % 200 == 0):
                dataset.save('AttributeDatasets/' + hypernym + "_" + dataset_name + ".xls")
    dataset.save('AttributeDatasets/' + hypernym + "_" + dataset_name + ".xls")



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

    return attribs_2_sentences



'''
NOTE: this is more efficient that just sorting by a single hypernym each time
Precondition:
    person_file_path is the name of a file with person names for one gender
    ***hypernyms is a LIST of categories the person fits into
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
Postcondition:
    Creates an Excel spreadsheet with columns:
    PersonName Attribute1 Attribute2 ... AttributeN
    and with all entries filled in
def createDatasetSortByHypernyms(person_file_path, hypernym, attribs, dataset_name):
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
        print("processing person: " + str(line))
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

        if(write):
            #now, write person to excel sheet
            dataset_sheet.write(row_counter, 0, line.strip())
            for i in range(len(curr_person_attribs)):
                dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
            row_counter += 1

        # just testing it out for now
        if(row_counter >= 200):
            break
    dataset.save('AttributeDatasets/' + hypernym + "_" + dataset_name + ".xls")
'''


if __name__ == '__main__':
    print('running')

    # define selenium browser for scraping
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)
    #createDatasetSortByHypernym("test_data.txt", 'Politican', ['party', 'religion', 'predecessor'], 'sent_test_h', browser)
    createDataset('test_data.txt', ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'sent_test', browser)
    #createDataset("PersonData_ttl/male_names.txt", ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'test')
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Politican', ['party', 'religion', 'predecessor'], 'test_h')
    #createDatasetSortByHypernym("PersonData_ttl/male_names.txt", 'Player', ['weight', 'team','position', 'number'], 'test_h2')



    '''test'''


    #print(getSentences(browser, 'Barack Obama', [('spouse', 'Michelle')]))
    '''seems to work'''





