import xlrd
import xlwt
#from sklearn.model_selection import train_test_split
import random


def normalizeDict(dict, sentencesCount):
    for e1 in dict:
        dict[e1] = dict[e1]/sentencesCount
    return dict


def addToDict(totaldict, genderDict, sheet, entityCount, sentencesCount):
    i = 1
    while i < sheet.nrows:

        # first, get the number of rows until next entity
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # now, get entity name
        e1 = sheet.cell_value(i, 0)
        print("CURR NAME: " + e1)
        entityCount += 1

        # now, get sentence counts for the entity
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                if sheet.cell_value(i, j) != "":
                    sentencesCount += 1
                    if e1 not in genderDict:
                        genderDict[e1] = 1
                    else:
                        genderDict[e1] += 1
                    if e1 not in totaldict:
                        totaldict[e1] = 1
                    else:
                        totaldict[e1] += 1
            i += 1

    return totaldict, genderDict, entity_rows, sentencesCount


def createTestDict(femaleDict, num_test, maleDict, totalDict):
    testDict = dict()

    proportion_of_gender = 0.5 * float(num_test)
    proportionOfFemales = 0
    while(proportionOfFemales < proportion_of_gender and femaleDict):
        e1, proportion = random.choice(list(femaleDict.items()))
        del femaleDict[e1]
        del totalDict[e1]
        proportionOfFemales += proportion
        testDict[e1] = e1

    proportionOfMales = 0
    while (proportionOfMales < proportion_of_gender and maleDict):
        e1, proportion = random.choice(list(maleDict.items()))
        del maleDict[e1]
        del totalDict[e1]
        proportionOfMales += proportion
        testDict[e1] = e1

    return testDict, femaleDict, maleDict, totalDict


def createOtherDatasetDicts(totalDict, proportion):
    dictionary = dict()
    proportionOfThisDict = 0

    while proportionOfThisDict < proportion and totalDict:
        e1, proportion2 = random.choice(list(totalDict.items()))
        del totalDict[e1]
        proportionOfThisDict += proportion2
        dictionary[e1] = e1

    return dictionary, totalDict



def getSplits(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    male_sheet = dataset.sheet_by_index(0)
    female_sheet = dataset.sheet_by_index(1)

    totalDict = dict() #dict with all entities
    maleDict = dict() #dict with only male entities
    femaleDict = dict() #dict with only female entities
    entityCount = 0
    sentencesCount = 0

    #get dicts
    totalDict, maleDict, entityCount, sentencesCount = addToDict(totalDict, maleDict, male_sheet, entityCount, sentencesCount)
    totalDict, femaleDict, entityCount, sentencesCount = addToDict(totalDict, femaleDict, female_sheet, entityCount,sentencesCount)

    #normalize
    totalDict = normalizeDict(totalDict, sentencesCount)
    maleDict = normalizeDict(maleDict, sentencesCount)
    femaleDict = normalizeDict(femaleDict, sentencesCount)


    '''now, start getting the splits'''
    #splits numbers
    #num_test = float(sentencesCount) * 0.10
    #num_dev = float(sentencesCount) * 0.10
    #num_train = float(sentencesCount) * 0.80

    #get all the splits set
    testDict, maleDict, femaleDict, totalDict = createTestDict(femaleDict, 0.1, maleDict, totalDict)
    devDict, totalDict = createOtherDatasetDicts(totalDict, 0.1)
    trainDict, totalDict = createOtherDatasetDicts(totalDict, 0.8)

    print(testDict)
    print(devDict)
    print(trainDict)

    return trainDict, devDict, testDict

def getEntityWriteFormatting(sheet):
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
        for j in range(0, sheet.ncols):
            matrix_to_write[0][j] = sheet.cell_value(i, j)

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


def writeMatrix(curr_write_row, sheet, matrix):
    for i in range(len(matrix)):
        curr_write_row += 1
        for j in range(len(matrix[i])):
            sheet.write(curr_write_row, j, matrix[i][j])
    return sheet, curr_write_row

def createSplitDataset(trainDict, devDict, testDict, oldDatasetPath, newDatasetPath):
    dataset = xlrd.open_workbook(oldDatasetPath)
    male_sheet = dataset.sheet_by_index(0)
    female_sheet = dataset.sheet_by_index(1)

    male_writematrices = getEntityWriteFormatting(male_sheet)
    female_writematrices = getEntityWriteFormatting(female_sheet)

    #now, start writing
    splits_set = xlwt.Workbook()
    train_sheet = splits_set.add_sheet("Train")
    dev_sheet = splits_set.add_sheet("Dev")
    test_sheet = splits_set.add_sheet("Test")

    curr_write_row = 1
    for e1 in trainDict:
        if e1 in male_writematrices:
            train_sheet, curr_write_row = writeMatrix(curr_write_row, train_sheet, male_writematrices[e1])
        elif e1 in female_writematrices:
            train_sheet, curr_write_row = writeMatrix(curr_write_row, train_sheet, female_writematrices[e1])

    curr_write_row = 1
    for e1 in devDict:
        if e1 in male_writematrices:
            dev_sheet, curr_write_row = writeMatrix(curr_write_row, dev_sheet, male_writematrices[e1])
        elif e1 in female_writematrices:
            dev_sheet, curr_write_row = writeMatrix(curr_write_row, dev_sheet, female_writematrices[e1])

    curr_write_row = 1
    for e1 in testDict:
        if e1 in male_writematrices:
            test_sheet , curr_write_row = writeMatrix(curr_write_row, test_sheet, male_writematrices[e1])
        elif e1 in female_writematrices:
            test_sheet, curr_write_row = writeMatrix(curr_write_row, test_sheet, female_writematrices[e1])

    splits_set.save(newDatasetPath)




if __name__ == '__main__':
    #getSplits('hypernyms_dataset.xlsx')
    trainDict, devDict, testDict = getSplits('test2.xlsx')
    createSplitDataset(trainDict, devDict, testDict, 'test2.xlsx', 'split.xls')
    # next up: use train_test_split to split the data correctly!
    # need to look at # of entities total and get ratios so know how to correctly split male and female so 50/50 for test set
