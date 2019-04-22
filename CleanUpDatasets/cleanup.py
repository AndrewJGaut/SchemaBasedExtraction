import xlrd
import xlwt
import sys


'''
Precondition:
    dataset_path is a valid dataset path to an Excel spreadsheet dataset
Postcondition:
    Ouptuts dataset at dataset_path_ + 'fixed' that fixes repeated sentences issue by deleting one of the two instances of that word
'''
def eliminateRepeatedSentences(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Fixed')

    for i in range(0, sheet.ncols):
        new_sheet.write(0, i, sheet.cell_value(0, i))



    curr_write_row = 1 # skip first row with column headers
    num_eliminated = [0] * sheet.ncols
    for i in range(1, sheet.nrows-1):
        if sheet.cell(i, 0) != "":
            num_eliminated = [0] * sheet.ncols
        for j in range(0, sheet.ncols):
            # check if this row same as next row
            if sheet.cell_value(i, j) != sheet.cell_value(i+1, j):
                new_sheet.write(curr_write_row - num_eliminated[j], j, sheet.cell_value(i,j))
            else:
                num_eliminated[j] += 1
        curr_write_row += 1

    for j in range(0, sheet.ncols):
        new_sheet.write(curr_write_row, j, sheet.cell_value(sheet.nrows-1, j))

    new_dataset.save(dataset_path[0:-5] + "_fixed.xls")


'''
Precondition:
    dataset_path is a relevant path to one of our DBPedia Excel datasets
Postcondition:
    Excel dataset at datset_path_e1e2.xls is output with only sentences containing BOTH entites from e1 and e2
'''
def onlyKeepDoubleEntitySentences(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Double Entity')

    curr_write_row = 1  # skip first row with column headers
    num_eliminated = [0] * sheet.ncols
    has_sentences_for_attributes = [0] * (sheet.ncols - 1)
    i = 0
    while i < sheet.nrows:
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        e1 = sheet.cell_value(i, 0)
        prev_i = i
        i += 1

        while(i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                if e1 in sheet.cell_value(i, j):
                    new_sheet.write(curr_write_row - num_eliminated[j], j, sheet.cell_value(i, j))
                    has_sentences_for_attributes[j-1] = 1
                else:
                    num_eliminated[j] += 1
            curr_write_row += 1

    new_dataset.save(dataset_path[0:-5] + "_e1e2.xls")

'''
Precondition:
    dataset_path is a relevant path to one of our DBPedia Excel datasets
Postcondition:
    Excel dataset at datset_path_e1e2.xls is output with only sentences containing BOTH entites from e1 and e2
'''
def onlyKeepDoubleEntitySentences2(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    new_dataset = xlwt.Workbook()
    new_sheet = new_dataset.add_sheet('Double Entity')

    curr_write_row = 1  # skip first row with column headers
    # num_eliminated = [0] * sheet.ncols

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
        matrix_to_write = [["" for x in range(sheet.ncols)] for y in range(entity_rows+1)]

        # first, add the header column to matrix
        for j in range(0, sheet.ncols):
            matrix_to_write[0][j] = sheet.cell_value(i, j)

        # next, get e1
        e1 = sheet.cell_value(i, 0)
        prev_i = i
        i += 1

        curr_write_row = 1
        while(i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                TEST = sheet.cell_value(i, j)
                first = e1.split()[0]
                last = e1.split()[-1]
                if first in sheet.cell_value(i, j) or last in sheet.cell_value(i, j):
                    matrix_to_write[curr_write_row][j] = sheet.cell_value(i, j)
                    has_sentences_for_attributes[j-1] = 1
                else:
                    pass
            i += 1
            curr_write_row += 1
        write = True
        for boolean in has_sentences_for_attributes:
            if boolean == 0:
                write = False
        if write:
            if already_wrote:
                prev_i += row_incr
                row_incr += 1
            for k in range(0, len(matrix_to_write)):
                for j in range(len(matrix_to_write[k])):
                    new_sheet.write(prev_i + k, j, matrix_to_write[k][j])
        already_wrote = True

    new_dataset.save(dataset_path[0:-4] + "_e1e2.xls")

def printMatrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            sys.stdout.write(matrix[i][j] + "; NEXT ENTRY: ")

        sys.stdout.write("\n")



if __name__ == '__main__':
    #eliminateRepeatedSentences('nohypernym_full_train_PersonData_ttl_female_names.txt_.xls')
    #onlyKeepDoubleEntitySentences2('test_fixed.xls')
    onlyKeepDoubleEntitySentences2('nohypernym_full_train_PersonData_ttl_female_names.txt_fixed.xls')
