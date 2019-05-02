from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict
import random as rand

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def containsComma(str):
    for c in str:
        if c == ',':
            return True

def csvConvert(x):
    if containsComma(x):
        x = "\"" + x + "\""
    return str(x)

'''
NOTE: if field contains comma, enclose in quotes!!!
'''
'''
def createCSV(dataset_path, csv_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    out_file = open('amt_data/' + csv_path + ".csv", 'w')
    out_str = ""

    #out_file.write('sentence,relation\n')
    out_str += 'sentence,relation\n'

    relation_types = list()
    for j in range(1, sheet.ncols):
        relation_types.append(sheet.cell_value(0,j))

    #now, get the values
    i = 1
    while i < sheet.nrows:
        # get current entity
        e1 = sheet.cell_value(i, 0)

        # get number of rows this entity takes up
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        #get list of e2s by column
        e2_vals = list()
        for j in range(1, sheet.ncols):
            e2_vals.append(sheet.cell_value(i,j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                if sheet.cell_value(i, j) != "":
                    relation = "({0}; {1}; {2})".format(str(e1), str(relation_types[j - 1]), str(e2_vals[j - 1]))
                    relation = csvConvert(relation)
                    sentence = csvConvert(sheet.cell_value(i,j))
                    #out_file.write(relation + "," + sentence + "\n")
                    out_str += relation + "," + sentence + "\n"
            i += 1
    out_str = out_str[0:-1]
    out_file.write(out_str)
    out_file.flush()
    out_file.close()
'''

'''
It should be an Excel file!!!
'''

def createCSV(dataset_path, csv_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Data')


    #out_file.write('sentence,relation\n')
    new_sheet.write(0, 0, 'sentence')
    new_sheet.write(0, 1, 'relation')


    relation_types = list()
    for j in range(1, sheet.ncols):
        relation_types.append(sheet.cell_value(0,j))

    #now, get the values
    curr_write_row = 1
    i = 1
    while i < sheet.nrows:
        # get current entity
        e1 = sheet.cell_value(i, 0)

        # get number of rows this entity takes up
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        #get list of e2s by column
        e2_vals = list()
        for j in range(1, sheet.ncols):
            e2_vals.append(sheet.cell_value(i,j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                if sheet.cell_value(i, j) != "":
                    relation = "({0}; {1}; {2})".format(str(e1), str(relation_types[j - 1]), str(e2_vals[j - 1]))
                    relation = csvConvert(relation)
                    sentence = csvConvert(sheet.cell_value(i,j))
                    #out_file.write(relation + "," + sentence + "\n")
                    new_sheet.write(curr_write_row, 0, relation)
                    new_sheet.write(curr_write_row, 1, sentence)
                    curr_write_row += 1
            i += 1
    new_dataset.save('amt_data/' + csv_path + '.xls')





def createCSV_fromtonyfile3(dataset_path, csv_path):
    # get set of names
    tsun_dataset = xlrd.open_workbook(dataset_path)
    males = tsun_dataset.sheet_by_index(0)
    females = tsun_dataset.sheet_by_index(1)

    male_names = dict()
    for i in range(males.nrows):
        curr_name = males.cell_value(i, 0)
        if curr_name not in male_names:
            male_names[curr_name] = curr_name

    female_names = dict()
    for i in range(females.nrows):
        curr_name = females.cell_value(i, 0)
        if curr_name not in female_names:
            female_names[curr_name] = curr_name


    # now open up male data
    male_dataset = xlrd.open_workbook('AttributeDatasets/nohyperym_full_train_PersonData_ttl_male_names.txt_fixed_e1e2.xls')
    male_sheet = male_dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Data')


    for j in range(20):
        if j % 2 == 0:
            new_sheet.write(0, j, "r" + str(int(j/2) + 1))
        else:
            new_sheet.write(0, j, "s" + str(int(j / 2) + 1))


    relation_types = list()
    for j in range(1, male_sheet.ncols):
        relation_types.append(male_sheet.cell_value(0,j))


    write_vals = [[0 for i in range(10)] for i in range(10)]

    #now, get the values
    curr_write_row = 1
    curr_write_cols = 0
    i = 1
    while i < male_sheet.nrows:
        # get current entity
        e1 = male_sheet.cell_value(i, 0)

        # get number of rows this entity takes up
        curr_row = i + 1
        while (curr_row < male_sheet.nrows and male_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i
        if e1 not in male_names:
            #skip this entity
            i += entity_rows
            continue

        #get list of e2s by column
        e2_vals = list()
        for j in range(1, male_sheet.ncols):
            e2_vals.append(male_sheet.cell_value(i,j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < male_sheet.nrows):
            for j in range(1, male_sheet.ncols):
                if male_sheet.cell_value(i, j) != "":
                    relation = "({0}; {1}; {2})".format(str(e1), str(relation_types[j - 1]), str(e2_vals[j - 1]))
                    #relation = csvConvert(relation)
                    #sentence = csvConvert(male_sheet.cell_value(i,j))
                    sentence = male_sheet.cell_value(i,j)
                    #out_file.write(relation + "," + sentence + "\n")
                    index1 = 0
                    index2 = 0
                    while(write_vals[index1][index2] != 0):
                        index1 = rand.randint(0,9)
                        index2 = rand.randint(0,9)
                    write_vals[index1][index2] = (relation, sentence)
                    #new_sheet.write(curr_write_row, curr_write_cols * 2, relation)
                    #new_sheet.write(curr_write_row, curr_write_cols * 2 + 1, sentence)
                    #curr_write_row += 1
                    curr_write_cols += 1
                    if curr_write_cols == 10:
                        curr_write_cols = 0
                        curr_write_row += 1
            i += 1


    # now open up female data
    female_dataset = xlrd.open_workbook('AttributeDatasets/nohypernym_full_train_PersonData_ttl_female_names.txt_fixed_e1e2.xls')
    female_sheet = female_dataset.sheet_by_index(0)

    '''
    relation_types = list()
    for j in range(1, male_sheet.ncols):
        relation_types.append(male_sheet.cell_value(0, j))
    '''

    i = 1
    curr_write_cols = 0
    while i < female_sheet.nrows:
        # get current entity
        e1 = female_sheet.cell_value(i, 0)

        # get number of rows this entity takes up
        curr_row = i + 1
        while (curr_row < female_sheet.nrows and female_sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i
        if e1 not in female_names:
            # skip this entity
            i += entity_rows
            continue

        # get list of e2s by column
        e2_vals = list()
        for j in range(1, female_sheet.ncols):
            e2_vals.append(female_sheet.cell_value(i, j))

        # now, get the tuples
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < female_sheet.nrows):
            for j in range(1, female_sheet.ncols):
                if female_sheet.cell_value(i, j) != "":
                    relation = "({0}; {1}; {2})".format(str(e1), str(relation_types[j - 1]), str(e2_vals[j - 1]))
                    #relation = csvConvert(relation)
                    #sentence = csvConvert(female_sheet.cell_value(i, j))
                    sentence = female_sheet.cell_value(i, j)
                    index1 = 0
                    index2 = 0
                    num_tries = 0
                    while (write_vals[index1][index2] != 0 and num_tries < 200):
                        index1 = rand.randint(0, 9)
                        index2 = rand.randint(0, 9)
                        num_tries += 1
                    write_vals[index1][index2] = (relation, sentence)
                    # new_sheet.write(curr_write_row, curr_write_cols * 2, relation)
                    # new_sheet.write(curr_write_row, curr_write_cols * 2 + 1, sentence)
                    # curr_write_row += 1
                    curr_write_cols += 1
                    if curr_write_cols == 10:
                        curr_write_cols = 0
                        curr_write_row += 1
            i += 1

    for i in range(len(write_vals)):
        for j in range(len(write_vals[0])):
            new_sheet.write(i+1, j*2, write_vals[i][j][0])
            new_sheet.write(i + 1, j*2+1, write_vals[i][j][1])

    new_dataset.save('amt_data/' + csv_path + '.xls')



def convertToBatches(amt_data_path, amt_splits_path, out_path):
    batch_size = 10

    splits = xlrd.open_workbook(amt_splits_path)
    splits_sheet = splits.sheet_by_index(0)
    sheet_index = 0

    amt_rels = xlrd.open_workbook(amt_data_path)
    amt_sheet = amt_rels.sheet_by_index(0)

    out_dataset = xlwt.Workbook()
    out_sheet = out_dataset.add_sheet('Data')

    for j in range(20):
        if j % 2 == 0:
            out_sheet.write(0, j, "r" + str(int(j/2) + 1))
        else:
            out_sheet.write(0, j, "s" + str(int(j / 2) + 1))

    i = 0
    curr_write_row = 1
    curr_write_cols = 0
    while True:
        '''
        if splits_sheet.cell_value(i, 0) == "":
            curr_write_cols = 0
            curr_write_row += 1
            i += 1
            continue
        '''
        if i >= splits_sheet.nrows:
            if sheet_index == 9:
                break
            curr_write_cols = 0
            curr_write_row += 1
            i = 0
            splits_sheet = splits.sheet_by_index(sheet_index)
            sheet_index += 1
            continue

        else:
            e1 = splits_sheet.cell_value(i, 0)
            e2 = splits_sheet.cell_value(i, 1)
            sentence = splits_sheet.cell_value(i,2)

            for k in range(amt_sheet.nrows):
                relation = amt_sheet.cell_value(k, 0)
                entities = relation.split(';')
                if len(entities) >= 3:
                    e1_2 = entities[0][1:].strip()
                    e2_2 = entities[2][:-1].strip()
                    sentence_2 = amt_sheet.cell_value(k, 1)


                    if e1 == e1_2 and e2 == e2_2 and sentence_2.strip() == sentence.strip():
                        out_sheet.write(curr_write_row, curr_write_cols * 2, relation)
                        out_sheet.write(curr_write_row, curr_write_cols * 2 + 1, amt_sheet.cell_value(k, 1))
                        curr_write_cols += 1
                        break
                        '''
                        if curr_write_cols >= 10:
                            curr_write_row += 1
                            curr_write_cols = 0
                        '''
            i += 1

    out_dataset.save("amt_data/FINAL PILOT SPLITS2.xls")






if __name__ == '__main__':
    #createCSV_fromtonyfile3('amt_data/AMT_pilot.xlsx', 'pilot_study2')
    createCSV('AttributeDatasets/pilot_study2.xlsx', 'NEW PILOT STUDY')
    convertToBatches('amt_data/pilot_study2.xls', 'amt_data/AMT_split.xls', '')

    #convertToBatches('amt_data/pilot_study2.xls', 'amt_data/AMT_split.xls', '')