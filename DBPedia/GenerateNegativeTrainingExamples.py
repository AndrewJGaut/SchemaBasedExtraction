from ParseDBPedia import *
from CreateDBPediaDataset import *
import xlrd
import xlwt
import nltk
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


'''
Generate negative training examples by finding entities that do NOT hold one
of the relations hypernym, spouse, birthDate, or birthPlace (ie they have no
relation, as far as the model is concerned)


We use parent as a negative for spouse
We use deathDate as a negative for birthDate
We use almaMater as a negative since it has nothing to do with our relations

It works!!!
'''
def genNegExamples(person_file_path, dataset_name, browser):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    dataset_sheet.write(0, 1, "NA")


    attribs = ['parents', 'deathDate', 'almaMater'] #do we want to add any others?


    # get file to read names from
    person_file = open(person_file_path, 'r')

    # elinimate issues with saving file name later
    person_file_path = person_file_path.replace('/', '_')

    #count rows in workbook so that we know where to write data
    curr_write_row = 1

    for line in person_file.readlines():
        name = formatName(line.strip())

        for attrib in attribs:
            e2 = getAttributeForPerson(name, attrib)
            if e2 != "ERROR: could not find attribute":
                attribute_vals = [(attrib, e2)]
                attribs_2_sentences = getSentences(browser, name, attribute_vals)
                if attribs_2_sentences[attrib]:
                    #then, we add the entry
                    print('adding entry for ' + str(name))

                    sentences = attribs_2_sentences[attrib]
                    dataset_sheet.write(curr_write_row, 0, name)
                    dataset_sheet.write(curr_write_row, 1, e2)
                    curr_write_row += 1
                    #write sentences below
                    for sentence in sentences:
                        dataset_sheet.write(curr_write_row, 1, sentence)
                        curr_write_row += 1

        if curr_write_row % 300 == 0:
            dataset.save('AttributeDatasets/' + dataset_name + ".xls")

    dataset.save('AttributeDatasets/' + dataset_name + ".xls")


if __name__ == '__main__':
    # define selenium browser for scraping
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    genNegExamples('test_data.txt', 'negative_examples', browser)
    #genNegExamples('PersonData_ttl/male_names.txt', 'negative_examples', browser)



