'''
This converts the Excel dataset into a JSON dataset with a format like so:
{
'train':
 [ {
    entity1: NAME,
    relations: [
        {
            name: spouse,
            entity2: NAME,
            sentences: [
            ]
        }

    ]
} ], ...

'''
import json
import xlrd

def getNumberOfRowsForEntity(sheet, prev_row):
    row_counter = 0
    while (row_counter + prev_row < sheet.nrows and sheet.cell_value(row_counter + prev_row, 0) == ""):
        row_counter += 1
    return row_counter


def convertExcelDatasetToJson(excelbook_name, outfile_name, prettify=False):
    book = xlrd.open_workbook(excelbook_name)

    # create the json
    data = dict()
    data['train'] = convertExcelSheetToJsonObject(book.sheet_by_index(0))
    data['dev'] = convertExcelSheetToJsonObject(book.sheet_by_index(1))
    data['male_test'] = convertExcelSheetToJsonObject(book.sheet_by_index(2))
    data['female_test'] = convertExcelSheetToJsonObject(book.sheet_by_index(3))

    # create the file
    with open(outfile_name, 'w') as outfile:
        if(prettify):
            json.dump(data, outfile, indent=4, sort_keys=True)
        else:
            json.dump(data, outfile)

'''
Paramters:
- sheet: the xlrd Sheet object that you want to convert to JSON
Returns:
- the sheet in object format READY TO BE transofmred in json (but not yet json)
'''
def convertExcelSheetToJsonObject(sheet):
    # get the attributes
    attributes = list()
    for i in range(1, sheet.ncols):
        cell_val = sheet.cell_value(0, i).strip()
        if(cell_val != ''):
            attributes.append(cell_val)

    entries = list()

    i = 1

    while i < sheet.nrows:
        entries.append(dict())
        curr_entry = entries[-1]

        curr_row = i + 1

        entity_rows = getNumberOfRowsForEntity(sheet, curr_row)
        curr_row += entity_rows

        # next, get e1
        prev_i = i
        i += 1
        e1 = sheet.cell_value(prev_i, 0).strip()

        # start creating the json object
        curr_entry['entity1'] = e1

        # now, get the e2s for each attribute
        curr_entry['relations'] = list()
        for index in range(len(attributes)):
            curr_entry['relations'].append(dict())

            curr_entry['relations'][index]['relation_name'] = attributes[index]
            curr_entry['relations'][index]['entity2'] = sheet.cell_value(prev_i, index+1)

            # get sentences for thsi e2
            curr_entry['relations'][index]['sentences'] = list()
            curr_entity_row = prev_i + 1
            while (curr_entity_row < sheet.nrows and sheet.cell_value(curr_entity_row, index+1) != ''):
                curr_entry['relations'][index]['sentences'].append(sheet.cell_value(curr_entity_row, index+1))
                curr_entity_row += 1


        # now, go to the next entry
        i = curr_row

    '''
    with open(out_file, 'w') as outfile:
        json.dump(entries, outfile, indent=4, sort_keys=True)
    '''
    return entries
    #return json.dumps(entries)

if __name__ == '__main__':
    convertExcelDatasetToJson('AttributeDatasets/Wikigender.xls', 'Wikigender.json', True)
