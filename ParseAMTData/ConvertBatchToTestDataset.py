import xlrd
import xlwt
import sys



'''create function to go through columns for inputs and answers for one num!!!'''

class RelSentsCols:
    def __init__(self):
        self.sentence_col = 0
        self.rel_col = 0
        self.answer_col = 0

    def set_sent_col(self, sent):
        self.sentence_col = int(sent)

    def set_rel_col(self, rel):
        self.rel_col = int(rel)

    def set_answer_col(self, ans):
        self.answer_col = int(ans)

    def get_sent_col(self):
        return self.sentence_col

    def get_rel_col(self):
        return self.rel_col

    def get_answer_col(self):
        return self.answer_col

'''
write the matrix to the sheet starting at the curr_row
'''
def writeMatrix(curr_write_row, sheet, matrix):
    for i in range(len(matrix)):
        curr_write_row += 1
        for j in range(len(matrix[i])):
            sheet.write(curr_write_row, j, matrix[i][j])
    return sheet, curr_write_row

'''
Finds majority vote in answers array (returns yes or no)
'''
def majorityVote(answers):
    votes = {'yes': 0, 'no':0}
    for answer in answers:
        if answer != '':
            votes[answer] += 1
    if votes['yes'] >= votes['no']:
        return 'yes'
    else:
        return 'no'

'''
Precondition:
    sent_col is the column for this survey questionNumber's sentence
    rel_col is the column in the Excel sheet with this questionNumber's relation (i.e. (brad pitt; hyperhym; actor)
    answer_col is the column in the Excel sheet with this questionNumber's answers (i.e. yes yes no etc)
    sheet is the Excel sheet
    e1_2_rels is a dict mapping an entity to a dict mapping (relation, e2) tuples to sentences
    NOTE: we say questionNumber because each column has questions from mnay different surveys, so each column has different questions
Postcondition:
    updates e1_2_rels, the dict mapping an entity to a dict mapping relations to sentences
'''
def convertQuestion2(sent_col, rel_col, answer_col, sheet, e1_2_rels):
    for row in (1, sheet.nrows, 3):
        curr_rel = sheet.cell_value(row, rel_col)
        curr_sent = sheet.cell_value(row, sent_col)

        curr_answers = list()
        for j in range(row, row+3):
            curr_answers.append(sheet.cell_value(j, answer_col))
        curr_answer = majorityVote(curr_answers)
        if curr_answer == 'no':
            curr_rel = "NA"

        words = curr_rel.split(';')
        e1 = words[0][1:].strip()
        rel = words[1].strip()
        e2 = words[2][:-1].strip()

        if not e1 in e1_2_rels:
            e1_2_rels[e1] = dict()
        if (rel, e2) not in e1_2_rels[e1]:
            e1_2_rels[e1][(rel, e2)] = list()
        e1_2_rels[e1][(rel, e2)].append(curr_sent)

    return e1_2_rels


'''
Precondition:
    sent_col is the column for this survey questionNumber's sentence
    rel_col is the column in the Excel sheet with this questionNumber's relation (i.e. (brad pitt; hyperhym; actor)
    answer_col is the column in the Excel sheet with this questionNumber's answers (i.e. yes yes no etc)
    sheet is the Excel sheet
    e1_2_rels is a dict mapping an entity to a dict mapping (relation, e2) tuples to sentences
    NOTE: we say questionNumber because each column has questions from mnay different surveys, so each column has different questions
Postcondition:
    creates e1_2_matrix, a mapping from e1 to a matrix
'''
def convertQuestion(sent_col, rel_col, answer_col, sheet, e1_2_rels, attribs):
    for row in range(1, sheet.nrows-1, 3):
        curr_rel = sheet.cell_value(row, rel_col)
        curr_sent = sheet.cell_value(row, sent_col)
        if curr_rel == '' or curr_sent == '':
            continue

        curr_answers = list()
        for j in range(row, row + 3):
            curr_answers.append(sheet.cell_value(j, answer_col))
        curr_answer = majorityVote(curr_answers)
        if curr_answer == 'no':
            #then, we need to make the relation NA instead of what it was previously
            curr_words = curr_rel.split(';')
            curr_rel = curr_words[0] + ";" + " NA;" + curr_words[2]

        words = curr_rel.split(';')
        #print(words)
        #print("; ROW: " + str(row) + ",REL_COL:" + str(rel_col) + ", SENT_COL: " + str(sent_col))
        e1 = words[0][1:].strip()
        rel = words[1].strip()
        e2 = words[2][:-1].strip()

        if not e1 in e1_2_rels:
            # then, init the matrix
            matrix_to_write = [["" for x in range(len(attribs) + 1)] for y in range(4)]
            matrix_to_write[0][0] = e1
            e1_2_rels[e1] = matrix_to_write
        matrix_to_write = e1_2_rels[e1]

        #write values and sentences
        for j in range(len(attribs)):
            if attribs[j].strip() == rel:
                #now, we want to add e2 here
                if matrix_to_write[0][j+1] == "":
                    matrix_to_write[0][j + 1] = e2.strip()


                ''''NOTE!!!! WE NEED TO FIX THIS! NA E2S ARE OFTEN WRONG!'''
                if curr_rel.split(';')[1].strip() == 'NA':
                    if matrix_to_write[0][len(attribs)] != curr_rel.split(';')[2][:-1].strip():
                        print(str(matrix_to_write[0][len(attribs)]) + "NOTE EQUIV TO " + str(curr_rel.split(';')[2][:-1].strip()))

                #now, add sentence
                #first, find first empty column
                i = 1
                while(matrix_to_write[i][j] != ""):
                    #print('i:' + str(i) + ", j:" + str(j))
                    i+=1
                    if i == len(matrix_to_write):
                        matrix_to_write = resize(matrix_to_write, i, attribs)
                #now, we know we're at an emtpy column
                matrix_to_write[i][j+1] = curr_sent
    return e1_2_rels


'''
Returns copy of matrix with double the row count
'''
def resize(matrix, old_row_count, attribs):
    new_mat = [["" for x in range(len(attribs) + 1)] for y in range(old_row_count * 2)]

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            new_mat[i][j] = matrix[i][j]

    return new_mat

'''
Preconditoin:
    e1_2_rels is a dict mapping e1 to a dict mapping rel,e2 tuples to lists of sentences
    attribs is a list of sentences IN THE ORDER THEY SHOULD BE OUTPUT to the Excel sheet
Postcondition:
    return a mapping from e1 to the matrix that we will write for e1
'''
'''
def convertToMatrix(e1_2_rels, attribs):
    e1_2_matrix = dict()

    for e1 in e1_2_rels:
        matrix_2_write = [["" for x in range(len(attribs) + 1)] for y in range(50)]
        matrix_2_write[0][0] = e1
        for j in range(len(attribs)):

        curr_dict = e1_2_rels[e1]
'''




'''
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
'''




'''input.r1 input.s1'''
def createTestDataset(amt_data_path, out_dataset_path, attribs):
    dataset = xlrd.open_workbook(amt_data_path)
    sheet = dataset.sheet_by_index(0)

    num_column_mapping = {}
    for j in range(sheet.ncols):
        if sheet.cell_value(0,j).split('.')[0] == 'Input' or sheet.cell_value(0,j).split('.')[0] == 'Answer':
            type_num = sheet.cell_value(0,j).split('.')[1]
            type = type_num[0]
            num = int(type_num[1:])
            if num not in num_column_mapping:
                num_column_mapping[num] = RelSentsCols()
            if type == 'r':
                num_column_mapping[num].set_rel_col(j)
            if type == 's':
                num_column_mapping[num].set_sent_col(j)
            if type == 'd':
                num_column_mapping[num].set_answer_col(j)

    '''now, iterate through keys and use the function that calcs for each column'''
    e1_2_rels = dict()
    for num in num_column_mapping:
        e1_2_rels = convertQuestion(num_column_mapping[num].get_sent_col(), num_column_mapping[num].get_rel_col(), num_column_mapping[num].get_answer_col(), sheet, e1_2_rels, attribs)

    out_dataset = xlwt.Workbook()
    out_sheet = out_dataset.add_sheet('Test')

    #create initial columns
    out_sheet.write(0,0, 'Full name')
    for j in range(len(attribs)):
        out_sheet.write(0, j+1, attribs[j])

    curr_write_row = 1
    for e1 in e1_2_rels:
        #if e1 in male_writematrices:
        out_sheet, curr_write_row = writeMatrix(curr_write_row, out_sheet, e1_2_rels[e1])
        #elif e1 in female_writematrices:
        #    train_sheet, curr_write_row = writeMatrix(curr_write_row, train_sheet, female_writematrices[e1])

    out_dataset.save(out_dataset_path + '.xls')

'''for debugging'''
def printMatrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            sys.stdout.write(matrix[i][j] + "; NEXT ENTRY: ")

        sys.stdout.write("\n")


'''
relevant_cols = list()
    for j in range(sheet.ncols):
        val = sheet.cell_value(0,j)
        if '.' in val:
            if val.split('.')[0] == 'Answer':
                relevant_cols.append(j)
'''





if __name__ == '__main__':
    createTestDataset('Datasets/relevant_FullALL.xlsx', 'TEST2', ['hypernym', 'spouse', 'birthDate', 'birthPlace', 'NA'])
    #createTestDataset('Datasets/test_relfullall.xlsx', 'TEST', ['hypernym', 'spouse', 'birthDate', 'birthPlace', 'NA'])