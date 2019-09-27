
import sys
sys.path.insert(0, "./")
from EqualizeEntries import *
import random
import xlrd
import xlwt


def getNumberOfWriteTimes(male_entries, female_entries):
    number_of_write_times = dict()

    for e1 in male_entries:
        number_of_write_times[e1] = 1


    number_of_female_write_times = int(len(male_entries) / len(female_entries))
    for e1 in female_entries:
        number_of_write_times[e1] = number_of_female_write_times

    num_females_written = len(female_entries) * number_of_female_write_times
    random_sample = random.sample(female_entries.keys(), len(female_entries))
    random_sample_index = 0

    while(num_females_written < len(male_entries)):
        curr_e1 = random_sample[random_sample_index]
        number_of_write_times[curr_e1] += 1
        num_females_written += 1

    return number_of_write_times


def equalizeEntriesWithSampling():
    book = createWorkbook('AttributeDatasets/Wikigender.xls')
    train_sheet = book.sheet_by_index(0)
    dev_sheet = book.sheet_by_index(1)

    entries = getEntries(train_sheet)

    # now, sort them into male and female
    male_names = getNamesFromFileToDict('PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('PersonData_ttl/female_names.txt')
    male_entries = getSpecificEntries(entries, male_names)
    female_entries = getSpecificEntries(entries, female_names)

    # get write times
    number_of_write_times = getNumberOfWriteTimes(male_entries, female_entries)

    # now, write to new training sheet
    new_book = xlwt.Workbook()
    new_train_sheet = new_book.add_sheet(train_sheet.name)
    new_dev_sheet = new_book.add_sheet(dev_sheet.name)

    # write the entries
    writeEntries(train_sheet, new_train_sheet, entries, number_of_write_times)
    writeEntries(dev_sheet, new_dev_sheet, entries, number_of_write_times)

    new_book.save("TESTTTT.xls")



if __name__ == '__main__':

    '''
    # this is to check
    book = xlrd.open_workbook('TESTTTT.xls')
    train_sheet = book.sheet_by_index(0)
    entries = getEntries(train_sheet)

    # now, sort them into male and female
    male_names = getNamesFromFileToDict('PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('PersonData_ttl/female_names.txt')
    male_entries = getSpecificEntries(entries, male_names)
    female_entries = getSpecificEntries(entries, female_names)

    print(len(male_entries))
    print(len(female_entries))
    '''











    '''
    book = createWorkbook("")train_sheet = book.sheet_by_index(0)

#   entries = getEntries(train_sheet)

    # now, sort them into male and female
    male_names = getNamesFromFileToDict('PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('PersonData_ttl/female_names.txt')
#    female_entries = getSpecificEntries(entries, female_names)
#    male_entries = getSpecificEntries(entries, male_names)

    # now, let's equalize them
#    number_of_write_times = getNumberOfWriteTimes(male_entries, female_entries)

    # now, let's write them out
#    writeEntries(train_sheet, new_train_sheet, entries, number_of_write_times)
'''