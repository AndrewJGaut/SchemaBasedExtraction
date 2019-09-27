'''
This file takes the original dataset and equalizes the number of datapoints of each gender in the training and dev sets
NOTE: !!! CURRENT EQUAL GENDER SPLIT DATASET IS Wikigender_GENDERBALANCED.XLS !!!

'''


import xlrd
import xlwt
import json
import copy
from enum import Enum
import random
from collections import defaultdict

'''
Enum for the names of the sheet indices in the datasets
'''
class Sheet(Enum):
    Training = 0
    Dev = 1
    MaleTest = 2
    FemaleTest = 3



def createWorkbook(sheetname):
    return xlrd.open_workbook(sheetname)

'''
copy all values from old_sheet to new_sheet
'''
def copyOver(old_sheet, new_sheet):
    for row_index in range(old_sheet.nrows):
        for col_index in range(old_sheet.ncols):
            new_sheet.write(row_index, col_index, old_sheet.cell_value(row_index, col_index))

    return new_sheet


def getNumberOfRowsForEntity(sheet, prev_row):
    row_counter = 0
    while (row_counter + prev_row < sheet.nrows and sheet.cell_value(row_counter + prev_row, 0) == ""):
        row_counter += 1
    return row_counter

def getEntry(sheet, i, entries):
    curr_row = i + 1

    entity_rows = getNumberOfRowsForEntity(sheet, curr_row)
    curr_row += entity_rows

    # next, get e1
    prev_i = i
    i += 1
    e1 = sheet.cell_value(prev_i, 0)

    # now, create the new dictionary etnry
    entries[e1] = list()

    # now, get the e2s for each attribute
    for col_index in range(1, sheet.ncols):
        curr_list = entries[e1]
        curr_list.append(dict())
        entries[e1][col_index - 1]['e2'] = sheet.cell_value(prev_i, col_index)

        # get sentences for thsi e2
        entries[e1][col_index - 1]['sentences'] = list()
        curr_entity_row = prev_i + 1
        while (curr_entity_row < sheet.nrows and sheet.cell_value(curr_entity_row, col_index) != ''):
            entries[e1][col_index - 1]['sentences'].append(sheet.cell_value(curr_entity_row, col_index))
            curr_entity_row += 1

    # now, go to the next entry
    i = curr_row

    return (dict, i)

'''
Paramters:
- the excel sheet (an xlrd object)
-

Returns:
- A dictionary mapping of each entry in the Excel sheet
- basically, get all the entries in a much more friendly form
dict{e1Name}[attrib0, attib1, attrib2, attrib3]
dict[e1Name][0] --> {'e2': e2Name, 'sentences':[]}
'''
def getEntries(sheet):
    entries = dict()

    i = 1

    while i < sheet.nrows:
        curr_row = i + 1

        entity_rows = getNumberOfRowsForEntity(sheet, curr_row)
        curr_row += entity_rows

        # next, get e1
        prev_i = i
        i += 1
        e1 = sheet.cell_value(prev_i, 0).strip()

        # now, create the new dictionary etnry
        entries[e1] = list()

        # now, get the e2s for each attribute
        for col_index in range(1, sheet.ncols):
            curr_list = entries[e1]
            curr_list.append(dict())
            entries[e1][col_index - 1]['e2'] = sheet.cell_value(prev_i, col_index)

            # get sentences for thsi e2
            entries[e1][col_index - 1]['sentences'] = list()
            curr_entity_row = prev_i + 1
            while (curr_entity_row < sheet.nrows and sheet.cell_value(curr_entity_row, col_index) != ''):
                entries[e1][col_index - 1]['sentences'].append(sheet.cell_value(curr_entity_row, col_index))
                curr_entity_row += 1

        # now, go to the next entry
        i = curr_row
    return entries


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
    specific_entries = dict()

    for e1 in entries:
        if e1 in names:
            specific_entries[e1] = entries[e1]

    return specific_entries

'''
get the sentences (the actual datapoints) in the entries object
'''
def getSentencesFromEntries(entries):
    sentences = list()

    #iterate through the keys
    for e1 in entries:
        #iterate trhough the attributes
        for index in range(len(entries[e1])):
            sentences.extend(entries[e1][index]['sentences'])

    return sentences


'''
Parameters:

Returns:
- the same as the entries object except only contains count number of sentences (the rest are deleted, essentially)
'''
def pruneEntries(entries, count):
    ret_entries = dict()

    num_sentences = 0 # keep track of how mnay sentences we've added to the return object; shouldn't be more than count!

    #for e1 in random.shuffle(entries.keys()): #note that the order of these is randomized
    for e1 in entries:
        # check if we have all the sentences we want
        if (num_sentences == count):
            return ret_entries

        # now, add the sentences we want to keep
        ret_entries[e1] = list()
        for index in range(len(entries[e1])):


            # add the dictionary
            ret_entries[e1].append(dict())

            # now, add in the e2 and the sentences
            ret_entries[e1][index]['e2'] = entries[e1][index]['e2']
            ret_entries[e1][index]['sentences'] = list()
            sentences = entries[e1][index]['sentences']
            for sentence in sentences:
                # check if we have all the sentences we want
                if (num_sentences == count):
                    return ret_entries

                ret_entries[e1][index]['sentences'].append(sentence)
                num_sentences += 1

    return ret_entries

'''
Paramters:
- list_of_entries_objects: a list of entries objects
Returns:
- a single entries object with all the netires in each of the entries objects
'''
def combineEntries(list_of_entries_objects):
    entries = dict()

    for entries_object in list_of_entries_objects:
        for e1 in entries_object:
            entries[e1] = entries_object[e1]

    return entries

'''
This function writes all entries to a sheet
we copy the top columns in the old sheet as well
'''
def writeEntries(old_sheet, new_sheet, entries, number_of_write_times = None):
    for col_index in range(old_sheet.ncols):
        new_sheet.write(0, col_index, old_sheet.cell_value(0, col_index))

    curr_row = 1


    for e1 in entries:
        curr_number_of_write_times = 1
        if(number_of_write_times != None and e1 in number_of_write_times):
            curr_number_of_write_times = number_of_write_times[e1]

        i = 0
        for i in range(curr_number_of_write_times):
            max_num_rows = 0

            new_sheet.write(curr_row, 0, e1)
            for index in range(len(entries[e1])):
                new_sheet.write(curr_row, index+1, entries[e1][index]['e2'])

                sentences = entries[e1][index]['sentences']
                curr_write_row = curr_row + 1
                for sentence in sentences:
                    new_sheet.write(curr_write_row, index+1, sentence)
                    curr_write_row += 1

                curr_entity_rows = curr_write_row - curr_row
                if curr_entity_rows > max_num_rows:
                    max_num_rows = curr_entity_rows

            curr_row += max_num_rows + 2

    return new_sheet

'''
Add a new gender equalized sheet to the new_book
copy over and create gender_equalized thing from sheet at sheet_index in the old book (book)
'''
def addNewGenderEqualizedSheet(book, new_book, male_names, female_names, sheet_index):
    sheet = book.sheet_by_index(sheet_index)

    entries = getEntries(sheet)  # get a dictionary with info for all the entities
    #json_dataset = json.dumps(entries)

    female_entries = getSpecificEntries(entries, female_names)
    male_entries = getSpecificEntries(entries, male_names)

    # get just the sentences for the entries
    female_sentences = getSentencesFromEntries(female_entries)
    male_entries = pruneEntries(male_entries, len(female_sentences))

    # now, all the female datapoints we want to use (for an equal split) are in female_entries and male in male_entries
    # so, let's write them back to a new sheet
    new_sheet = new_book.add_sheet(sheet.name)
    writeEntries(sheet, new_sheet, combineEntries([male_entries, female_entries]))


#def addNewCountAdjustedTestData(book, new_book, sheet_index_for_train_data_from_old_book):



'''
Parametes:
- olddatasetname is the dataset we're copying data from
- newdatasetnamei st he name of the dataset we're creatingwith the qualized gender counts in the training set
'''
def createGenderEqualizedDataset(old_dataset_name, new_dataset_name):
    male_names = getNamesFromFileToDict('PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('PersonData_ttl/female_names.txt')


    book = createWorkbook(old_dataset_name)
    new_book = xlwt.Workbook()
    addNewGenderEqualizedSheet(book, new_book, male_names, female_names, 0)
    #addNewGenderEqualizedSheet(book, new_book, male_names, female_names, 1)


    # for test data, we just want to take enough so that 5% is that.
    #addNewCountAdjustedTestData(book, new_book, 0)





    # now, copy over all other sheets from the old book.
    for sheet_index in range(2, len(book.sheet_names())):
        old_sheet = book.sheet_by_index(sheet_index)
        new_sheet = new_book.add_sheet(old_sheet.name)
        copyOver(old_sheet, new_sheet)

    new_book.save(new_dataset_name)

'''
Parameters:
- workbook_name is the name of the workbook we want to open
What it does:
- This function will check what proportion of the total data items (which are the sentences) are made up in each sheet
- basically, we can see if our datasets splits are correct; train should have 80% of the sentences, dev 10%, etc.
'''
def checkPercentages(workbook_name):
    new_book = xlrd.open_workbook(workbook_name)

    total_sentences = 0
    for sheet_index in range(new_book.nsheets):
        curr_sheet = new_book.sheet_by_index(sheet_index)

        entries = getEntries(curr_sheet)
        sentences = getSentencesFromEntries(entries)
        total_sentences += len(sentences)

    for sheet_index in range(new_book.nsheets):
        curr_sheet = new_book.sheet_by_index(sheet_index)

        entries = getEntries(curr_sheet)
        sentences = getSentencesFromEntries(entries)
        percentage = (len(sentences) / total_sentences) * 100
        print("{} has percent: {}%".format(sheet_index, percentage))



if __name__ == '__main__':
    #createGenderEqualizedDataset('AttributeDatasets/WG_for_resplit.xls', 'AttributeDatasets/WG_GEqual_AllTrain.xls')



    # now, let's check the percentages
    checkPercentages('AttributeDatasets/WG_GEqual_Split.xls')



