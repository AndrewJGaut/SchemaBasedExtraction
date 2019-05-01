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

'''
Precondition:
    curr_dataset is a normal AttributeDataset
    neg_examples_dataset is a dataset with format FullName NA and otherwise in normal format
    new_dataset_name is name of dataset after integrating negative examples
Postcondition:
    new_dataset_name is a dataset with all examples plus negative examples integrated
'''
def integrateNegExamples(curr_dataset_name, neg_examples_dataset_name, new_dataset_name):
    full_dataset = xlrd.open_workbook(curr_dataset_name)
    full_data_sheet = full_dataset.sheet_by_index(0)

    negatives_dataset = xlrd.open_workbook(neg_examples_dataset_name)
    negatives_data_sheet = negatives_dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Fixed')



    '''get negative examples in dict'''
    i = 1
    e1_2_negatives = defaultdict(list)

    while i < negatives_data_sheet.nrows:
        curr_row = i + 1
        while (curr_row < negatives_data_sheet.nrows and negatives_data_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        e1 = getName(negatives_data_sheet.cell_value(i, 0))
        e2 = getName(negatives_data_sheet.cell_value(i, 1))
        #e1_2_negatives[e1].append(e2)
        prev_i = i
        i += 1

        for j in range(i, i+entity_rows-1):
            if e1 not in e1_2_negatives:
                e1_2_negatives[e1].append((e2,negatives_data_sheet.cell_value(j,1)))
            elif e1_2_negatives[e1][0][0] == e2:
                e1_2_negatives[e1].append((e2, negatives_data_sheet.cell_value(j, 1)))
            else:
                pass

        i = prev_i + entity_rows



    '''now, write these to new sheet'''
    for j in range(0, full_data_sheet.ncols):
        new_sheet.write(0, j, full_data_sheet.cell_value(0, j))
    new_sheet.write(0, full_data_sheet.ncols, 'NA')

    i = 1
    row_incr = 0
    while i < full_data_sheet.nrows:
        curr_row = i + 1
        while (curr_row < full_data_sheet.nrows and full_data_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        e1 = getName(full_data_sheet.cell_value(i, 0))
        print(e1)

        if e1 in e1_2_negatives and len(e1_2_negatives[e1]) >= 1:
            #we want to write negative example as well
            new_sheet.write(i+row_incr, full_data_sheet.ncols, e1_2_negatives[e1][0][0])

        '''
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < full_data_sheet.nrows):
            for j in range(0, full_data_sheet.ncols):
                print('writing positive')
                new_sheet.write(i, j, full_data_sheet.cell_value(i, j))
            if e1 in e1_2_negatives and len(e1_2_negatives[e1]) > (prev_i + entity_rows - i):
                print('writing negative')
                new_sheet.write(i + 1, full_data_sheet.ncols, e1_2_negatives[e1][prev_i + entity_rows - i][1])
            i += 1
        '''
        for k in range(i, i+entity_rows):
            for j in range(0, full_data_sheet.ncols):
                print('writing positive')
                new_sheet.write(k + row_incr,j,full_data_sheet.cell_value(k, j))
            if e1 in e1_2_negatives and len(e1_2_negatives[e1]) > k-i :
                print('writing negative')
                new_sheet.write(k+row_incr+1, full_data_sheet.ncols, e1_2_negatives[e1][k-i][1])

        i += entity_rows
        row_incr += 1

    new_dataset.save('AttributeDatasets/' + new_dataset_name + '.xls')






if __name__ == '__main__':
    # define selenium browser for scraping
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    #genNegExamples('test_data.txt', 'negative_examples', browser)
    #genNegExamples('PersonData_ttl/male_names.txt', 'negative_examples', browser)

    #integrateNegExamples('AttributeDatasets/nohypernym_full_train_PersonData_ttl_female_names.txt_fixed_e1e2.xls', 'AttributeDatasets/female_negative_examples.xls', 'FULL_DATASET_FEMALE.xls')
    integrateNegExamples('AttributeDatasets/nohyperym_full_train_PersonData_ttl_male_names.txt_fixed_e1e2.xls',
                         'AttributeDatasets/male_negative_examples.xls', 'FULL_DATASET_MALE.xls')


