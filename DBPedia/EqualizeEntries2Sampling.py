

from EqualizeEntries import *


def equalizeEntriesThroughSampling(male_entries, female_entries):
    number_of_write_times = dict()

    for e1 in male_entries:
        number_of_write_times[e1] = 1


    number_of_female_write_times = int(len(male_entries.keys()) / len(female_entries.keys()))
    for e1 in female_entries:
        number_of_write_times[e1] = number_of_female_write_times



if __name__ == '__main__':
    book = createWorkbook("")
    train_sheet = book.sheet_by_index(0)

    entries = getEntries(train_sheet)

    # now, sort them into male and female
    male_names = getNamesFromFileToDict('PersonData_ttl/male_names.txt')
    female_names = getNamesFromFileToDict('PersonData_ttl/female_names.txt')
    female_entries = getSpecificEntries(entries, female_names)
    male_entries = getSpecificEntries(entries, male_names)

    # now, let's equalize them