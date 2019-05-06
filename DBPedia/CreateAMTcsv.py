from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict
import random as rand

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

'''
Precondition:
    sheet is an Excel dataset sheet
Postcondition:
    returns mapping from entity to what we want to write in the new sheet for that entity
    mat[entity] --> [[full name, spouse, birthDate], [Jeff Smith, Sally Smith, June 4 1993]] etc.
'''
def getEntityMatrices(sheet):
    e1_2_writematrix = dict()

    i = 1
    already_wrote = False
    row_incr = 1
    num_sents = 0
    while i < sheet.nrows:
        has_sentences_for_attributes = [0] * (sheet.ncols - 1)
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # the matrix of values we'll write if this entity still has sentences
        matrix_to_write = [["" for x in range(sheet.ncols)] for y in range(entity_rows + 1)]

        # first, add the header column to matrix
        for j in range(0, sheet.ncols):
            matrix_to_write[0][j] = sheet.cell_value(i, j)

        # next, get e1
        e1 = sheet.cell_value(i, 0)
        prev_i = i

        curr_row = 0
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(sheet.ncols):
                matrix_to_write[curr_row][j] = sheet.cell_value(i,j)
                num_sents += 1
            i += 1
            curr_row += 1

        e1_2_writematrix[e1] = matrix_to_write

    return e1_2_writematrix, int((int(num_sents)/10 + 1))

'''randomize the matrix so samples aren't all the same for annotators'''
def randomizeMat(matrix):
    return matrix
    '''
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
    '''

'''
Preconditions:
    e1_2_matrix is a mapping from e1 to all of e1s entries in some excel sheet
    attribs is the attributes in the Excel sheet for which we have values for all the e1s. These should be in the same order as they are assumed in matrices in e1_2_matrix
Postcondition:
    Returns a matrix of relation,sentence tuples that is not randomized
'''
'''
def createAMTMatrix(e1_2_matrix, attribs, mat_size):
    #amt_mat = [["" for x in range(sheet.ncols)] for y in range(entity_rows + 1)]
    amt_mat = [list() for x in range(mat_size)]
    amt_row_counter = 0

    for e1 in e1_2_matrix:
        matrix = e1_2_matrix[e1]
        # get all entity2s for each column
        e2_vals = list()
        for i in range(1, len(matrix[0])):
            e2_vals.append(matrix[0][i])

        for i in range(1, len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] != "":
                    relation = "(" + e1 + "; " + attribs[j-1] + "; " + e2_vals[j-1] + ")"
                    sentence = matrix[i][j]
                    amt_mat[amt_row_counter].append((relation, sentence))
                #amt_mat[amt_row_counter][j] = (relation, sentence)

        amt_row_counter += 1

    amt_mat = randomizeMat(amt_mat)

    return amt_mat
'''

'''
Preconditions:
    e1_2_matrix is a mapping from e1 to all of e1s entries in some excel sheet
    attribs is the attributes in the Excel sheet for which we have values for all the e1s. These should be in the same order as they are assumed in matrices in e1_2_matrix
Postcondition:
    Returns a list of relation,sentence tuples that is not randomized
'''
def createAMTList(e1_2_matrix, attribs, mat_size):
    #amt_mat = [["" for x in range(sheet.ncols)] for y in range(entity_rows + 1)]
    tuples = list()

    for e1 in e1_2_matrix:
        matrix = e1_2_matrix[e1]
        # get all entity2s for each column
        e2_vals = list()
        for i in range(1, len(matrix[0])):
            e2_vals.append(matrix[0][i])

        for i in range(1, len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] != "":
                    relation = "(" + e1 + "; " + attribs[j-1] + "; " + e2_vals[j-1] + ")"
                    sentence = matrix[i][j]
                    tuples.append((relation, sentence))
                #amt_mat[amt_row_counter][j] = (relation, sentence)

    #amt_mat = randomizeMat(amt_mat)

    return tuples

'''
Precondition:
    dataset_path is path to releveant Excel dataset from which we are creating AMT tuples
    csv_path is path of output csv Excel with AMT data
Postcondition:
    csv_path Excel sheet has AMT data ready to be uploaded to MTurk!
'''
def createCSV(dataset_path, csv_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(2)

    new_dataset = xlwt.Workbook()
    out_sheet = new_dataset.add_sheet('Data')


    for j in range(20):
        if j % 2 == 0:
            out_sheet.write(0, j, "r" + str(int(j/2) + 1))
        else:
            out_sheet.write(0, j, "s" + str(int(j / 2) + 1))

    attribs = list()
    for j in range(1, sheet.ncols):
        attribs.append(sheet.cell_value(0,j))

    e1_2_matrix, mat_size = getEntityMatrices(sheet)

    tuples = createAMTList(e1_2_matrix, attribs, mat_size)

    curr_write_row = 1
    curr_write_col = 0
    while tuples:
        curr_tuple = tuples.pop(rand.randint(0, len(tuples)-1))
        out_sheet.write(curr_write_row, curr_write_col * 2, curr_tuple[0])
        out_sheet.write(curr_write_row, curr_write_col * 2 + 1, curr_tuple[1])
        curr_write_col += 1
        if curr_write_col >= 10:
            curr_write_col = 0
            curr_write_row += 1

    new_dataset.save('amt_data/' + csv_path + ".xls")

'''
def createCSV(dataset_path, csv_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    out_sheet = new_dataset.add_sheet('Data')


    for j in range(20):
        if j % 2 == 0:
            out_sheet.write(0, j, "r" + str(int(j/2) + 1))
        else:
            out_sheet.write(0, j, "s" + str(int(j / 2) + 1))

    attribs = list()
    for j in range(1, sheet.ncols):
        attribs.append(sheet.cell_value(0,j))

    e1_2_matrix, mat_size = getEntityMatrices(sheet)

    matrix = createAMTMatrix(e1_2_matrix, attribs, mat_size)

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            test = matrix[i][j]
            test2 = matrix[i][j][0]
            test3 = matrix[i][j][1]
            out_sheet.write(i+1, j*2, matrix[i][j][0])
            out_sheet.write(i + 1, j * 2 + 1, matrix[i][j][1])

    new_dataset.save('amt_data/' + csv_path + ".xls")
'''





if __name__ == '__main__':
    #createCSV_fromtonyfile3('amt_data/AMT_pilot.xlsx', 'pilot_study2')
    createCSV('test_split.xls', 'FULL_AMT_DATASTUDY')

    #convertToBatches('amt_data/pilot_study2.xls', 'amt_data/AMT_split.xls', '')

















