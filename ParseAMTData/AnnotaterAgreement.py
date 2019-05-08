import xlrd
import numpy as np
from krippendorff_alpha import *
#import statsmodels.stats.inter_rater



def fleiss_kappa(M):
  """
  See `Fleiss' Kappa <https://en.wikipedia.org/wiki/Fleiss%27_kappa>`_.
  :param M: a matrix of shape (:attr:`N`, :attr:`k`) where `N` is the number of subjects and `k` is the number of categories into which assignments are made. `M[i, j]` represent the number of raters who assigned the `i`th subject to the `j`th category.
  :type M: numpy matrix
  """
  N, k = M.shape  # N is # of items, k is # of categories
  n_annotators = float(np.sum(M[0, :]))  # # of annotators

  p = np.sum(M, axis=0) / (N * n_annotators)
  P = (np.sum(M * M, axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
  Pbar = np.sum(P) / N
  PbarE = np.sum(p * p)

  kappa = (Pbar - PbarE) / (1 - PbarE)

  return kappa

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


def getFleissKappa(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    f_kappas = list()

    #get fleiss kappa of each set of three annotators
    for i in range(1, sheet.nrows, 3):
        ratings = np.zeros([3, sheet.ncols], dtype=int)
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1
                    ratings[curr_row][j] = curr_val
        f_kappas.append(fleiss_kappa(ratings))

    # get average fleiss kappa value
    ave = 0
    for num in f_kappas:
        ave += num
    return float( float(ave) / float(len(f_kappas)))


def getKripAlpha(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    alphas = list()

    for i in range(1, sheet.nrows, 3):
        ratings = np.zeros([3, sheet.ncols], dtype=int)
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1
                    ratings[curr_row][j] = curr_val
        alphas.append(krippendorff_alpha(ratings))

    # get average fleiss kappa value
    ave = 0
    for num in alphas:
        ave += num
    return float( float(ave) / float(len(alphas)))


if __name__ == '__main__':
    #getAgreement('FullStudyResults.xls')
    #print(getFleissKappa('Datasets/FullStudyResults.xls'))
    #print(getKripAlpha('Datasets/FullStudyResults.xls'))

    '''
    dataset = xlrd.open_workbook("Datasets/test_please_tell_not_true.xlsx")
    sheet = dataset.sheet_by_index(0)

    for i in range(1, sheet.nrows, 3):
        #ratings = np.zeros([3, sheet.ncols], dtype=str)
        ratings = [['' for x in range(sheet.ncols)] for y in range(3)]
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                ratings[curr_row][j] = sheet.cell_value(i + curr_row, j)
        print(ratings)
    '''