import xlrd
import xlwt
from SplitDataset import *

'''
Precondition:
    sheet is an Excel dataset sheet
Postcondition:
    returns mapping from entity to what we want to write in the new sheet for that entity
    mat[entity] --> [[full name, spouse, birthDate], [Jeff Smith, Sally Smith, June 4 1993]] etc.
'''
def getEntityWriteFormatting(sheet, attribs):
    e1_2_writematrix = dict()

    i = 1
    already_wrote = False
    row_incr = 1
    while i < sheet.nrows:
        has_sentences_for_attributes = [0] * (sheet.ncols - 1)
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # the matrix of values we'll write if this entity still has sentences
        matrix_to_write = [["" for x in range(sheet.ncols)] for y in range(entity_rows + 1)]

        # first, add the header column to matrix
        matrix_to_write[0][0] = sheet.cell_value(0, 0)
        for j in range(0, len(attribs)):
            matrix_to_write[0][j+1] = sheet.cell_value(i, j+1)

        # next, get e1
        e1 = sheet.cell_value(i, 0)
        prev_i = i

        curr_row = 0
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(sheet.ncols):
                matrix_to_write[curr_row][j] = sheet.cell_value(i,j)
            i += 1
            curr_row += 1

        e1_2_writematrix[e1] = matrix_to_write

    return e1_2_writematrix

def getGender(gender_names_file):
    gender_names = set()

    names_file = open(gender_names_file, 'r')
    for line in names_file.readlines():
        name = line.strip()
        gender_names.add(name)

    return gender_names

def copySheet(old_sheet, copy_sheet):
    for i in range(old_sheet.nrows):
        for j in range(old_sheet.ncols):
            copy_sheet.write(i, j, old_sheet.cell_value(i,j))
    return copy_sheet


def splitGenders(old_dataset_path, new_dataset_path, male_names_file, female_names_file, attribs):
    old_dataset = xlrd.open_workbook(old_dataset_path)
    old_train_sheet = old_dataset.sheet_by_index(0)
    old_dev_sheet = old_dataset.sheet_by_index(1)
    old_test_sheet = old_dataset.sheet_by_index(2)

    splits_set = xlwt.Workbook()
    train_sheet = splits_set.add_sheet("Train")
    dev_sheet = splits_set.add_sheet("Dev")
    male_test_sheet = splits_set.add_sheet("Male Test")
    female_test_sheet = splits_set.add_sheet("Female Test")

    #get male and female names
    male_names = getGender(male_names_file)
    female_names = getGender(female_names_file)

    #get e12writematrix
    e1_2_writematrix = getEntityWriteFormatting(old_test_sheet, attribs)

    # write the new test sheets
    male_write_row = 1
    female_write_row = 1
    for e1 in e1_2_writematrix:
        if e1 in male_names:
            male_test_sheet, male_write_row = writeMatrix(male_write_row, male_test_sheet, e1_2_writematrix[e1])
        elif e1 in female_names:
            female_test_sheet, female_write_row = writeMatrix(female_write_row, female_test_sheet, e1_2_writematrix[e1])

    # copy over the train and dev sheets
    train_sheet = copySheet(old_train_sheet, train_sheet)
    dev_sheet = copySheet(old_dev_sheet, dev_sheet)

    #save workbook
    splits_set.save('AttributeDatasets/' + new_dataset_path + '.xls')

if __name__ == '__main__':
    splitGenders('test_split.xls', 'split_splitgenders', 'PersonData_ttl/male_names.txt', 'PersonData_ttl/female_names.txt', ['hypernym', 'spouse', 'birthDate', 'birthPlace'])


