import xlrd
import nltk
import sys


'''
def getGenderStats(dataset_path, sheet_num):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(sheet_num)
'''




'''
Postcondition:
    Returns a tuple representing #entities, #attributes, #sentences per entity, #sentences per attribute, average token length of sentence
'''
def getStats(dataset_path, sheet_num):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(sheet_num)

    attribs_2_sentencenums = dict()
    attribs = list()
    entities_2_sentencenums = dict()

    num_entities = 0
    num_sentences = 0
    total_token_length = 0

    # init attribs_2_sentencenums
    for j in range(1,sheet.ncols):
        attribs_2_sentencenums[sheet.cell_value(0,j)] = 0
        attribs.append(sheet.cell_value(0,j))

    curr_entity = ""
    for i in range(1, sheet.nrows):
        if sheet.cell_value(i, 0) != "":
            #then, we started a new entity
            entities_2_sentencenums[sheet.cell_value(i, 0)] = 0
            curr_entity = sheet.cell_value(i,0)
            num_entities += 1
        else:
            # we want to increment all other counts
            for j in range(1, sheet.ncols):
                if sheet.cell_value(i,j) != "":
                    attribs_2_sentencenums[attribs[j-1]] += 1
                    entities_2_sentencenums[curr_entity] += 1
                    num_sentences += 1
                    total_token_length += len(nltk.word_tokenize(sheet.cell_value(i,j)))

    # get sents per attrib


    # get num sentences per attribute
    print("num entities: " + str(num_entities))
    print("num sentencess: " + str(num_sentences))
    print("num sent/entity: " + str(float(num_sentences) / float(num_entities)))
    print("ave token len per sentence: " + str(float(total_token_length) / float(num_sentences)))


    sys.stdout.write("num sents per attrib: ")
    for j in range(len(attribs)):
        sys.stdout.write(attribs[j] + ": " + str(attribs_2_sentencenums[attribs[j]]) + "; ")
    sys.stdout.write("\n")
    sys.stdout.flush()

    sys.stdout.write("proportion of sents per attrib: ")
    for j in range(len(attribs)):
        proportion = float(attribs_2_sentencenums[attribs[j]]) / float(num_sentences)
        sys.stdout.write(attribs[j] + ": " + str(proportion) + "; ")
    sys.stdout.write("\n")
    sys.stdout.flush()

if __name__ == '__main__':
    #getStats('test_split.xls')
    #getStats('AttributeDatasets/split_splitgenders.xls', 1)
    getStats('AttributeDatasets/FULL_DATASET_FEMALE.xls.xls', 0)
