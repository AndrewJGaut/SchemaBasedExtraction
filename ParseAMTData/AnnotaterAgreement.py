import xlrd


def getAgreement(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    num_agreed = 0
    num_complete_agreement = 0
    num_total = 0
    per_question_agreement = list()

    relevant_cols = list()
    for j in range(sheet.ncols):
        val = sheet.cell_value(0,j)
        if '.' in val:
            if val.split('.')[0] == 'Answer':
                relevant_cols.append(j)

    for i in range(1, sheet.nrows, 3):
        for col in relevant_cols:
            TEST = sheet.cell_value(i,j)
            TEST2 = sheet.cell_value(i+1,j)
            answers = {}
            num_total += 1
            answers['yes'] = 0
            answers['no'] = 0
            answers[''] = 0
            answers[sheet.cell_value(i,j)] += 1
            answers[sheet.cell_value(i+1, j)] += 1
            answers[sheet.cell_value(i+2, j)] += 1

            if answers['yes'] == 3 or answers['no'] == 3:
                num_complete_agreement += 1

            per_question_agreement.append(max(answers['no'] / 3, answers['yes'] / 3))


    ave = 0
    for num in per_question_agreement:
        ave += num
    ave = float(float(ave) / float(len(per_question_agreement)))
    print(num_complete_agreement / num_total)
    print(ave)

if __name__ == '__main__':
    #getAgreement('Batch_3631670_batch_results.xls')
    getAgreement('batch_cheap_answers.xlsx')

