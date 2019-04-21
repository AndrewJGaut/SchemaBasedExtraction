import xlrd
import xlwt



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


if __name__ == '__main__':
    eliminateRepeatedSentences('nohypernym_full_train_PersonData_ttl_female_names.txt_.xls')
