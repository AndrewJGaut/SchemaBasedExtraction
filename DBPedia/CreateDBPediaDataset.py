'''This file creates the Excel sheet that is our dataset'''

from ParseDBPedia import *
import xlrd
import xlwt


'''
Precondition:
    person_file_path is the name of a file with person names for one gender
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
'''
def createDataset(person_file_path, attribs, dataset_name):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    for i in range(len(attribs)):
        dataset_sheet.write(0, (i+1), attribs[i])



    # get file to read names from
    person_file = open(person_file_path, 'r')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    for line in person_file.readlines():
        name = formatName(line.strip())
        curr_person_attribs = list()
        write = True
        for attrib in attribs:
            curr_person_attrib = getAttributeForPerson(name, attrib)
            if(curr_person_attrib == "ERROR: could not find attribute"):
                # if this is true, then this person doesn't have all the attributes we want; thus, we discard this data point
                write = False
                break
            curr_person_attribs.append(getAttributeForPerson(name, attrib))

        if(write):
            #now, write person to excel sheet
            dataset_sheet.write(row_counter, 0, line.strip())
            for i in range(len(curr_person_attribs)):
                dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
            row_counter += 1
    dataset.save('AttributeDatasets/' + dataset_name + ".xls")

if __name__ == '__main__':
    createDataset("test_data.txt", ['hypernym', 'spouse', 'birthDate', 'birthPlace'], 'test')





