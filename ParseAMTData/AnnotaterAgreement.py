import xlrd
import numpy as np
from krippendorff_alpha import *
import itertools
#import statsmodels.stats.inter_rater


'''
I obtained this from the internet
Input:
    -matrix where rows represent different annotators and columns represent answers to different questions
    -ex: rater 1 [yes, yes, no, yes, no]
         rater 2 [yes, yes, no, yes, yes]
         ...etc
         WRONG!!!!
    -should be
                    yes no
                q1
                q2
                q3
                q4
Output:
    Fleiss Kappa score for that matrix
'''
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

'''
This function informally obtains annotator agreement for dataset at dataset_path
This DOES NOT USE FLEISS KAPPA OR KRIPPENDORFF'S ALPHA! It was just a preliminary measurement
'''
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


'''
This function obtains Fleiss Kappa for the data
It obtains Fleiss Kappa for each set of raters who rate the same questions.
It then returns the average Fleiss Kappa value
'''
def getFleissKappa2(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    f_kappas = list()

    #get fleiss kappa of each set of three annotators
    for i in range(1, sheet.nrows, 3):
        ratings = np.zeros([3, sheet.ncols], dtype=int) # matrix of ratings where each row is a different rater and each column an answer to a question
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0 # set to 0 if they say no
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1 # set to 1 if they say yes
                    ratings[curr_row][j] = curr_val
        f_kappas.append(fleiss_kappa(ratings)) # pass in ratings matrix to fleiss kappa calculator

    # get average fleiss kappa value
    ave = 0
    for num in f_kappas:
        ave += num
    return float( float(ave) / float(len(f_kappas)))

def concatMatrices(matrix1, matrix2):
    new_mat = [[0 for x in range(2)] for y in range(len(matrix1) + len(matrix2))]

    i = 0
    while i < len(matrix1):
        for j in range(len(matrix1[i])):
            new_mat[i][j] = matrix1[i][j]
        i+=1

    i2 = 0
    while i2 < len(matrix2):
        for j in range(len(matrix2[i2])):
            new_mat[i + i2][j] = matrix2[i2][j]
        i2+=1

    return new_mat


def getFleissKappa(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    matrix = [[0 for x in range(2)] for y in range(1)]

    #a = np.zeros((1,1), dtype=int)

    #get fleiss kappa of each set of three annotators
    for i in range(1, sheet.nrows, 3):
        #ratings = np.zeros([3, sheet.ncols], dtype=int) # matrix of ratings where each row is a different rater and each column an answer to a question
        #ratings = np.zeros([3,2], dtype=int)
        ratings = [[0 for x in range(2)] for y in range(3)]
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0 # set to 0 if they say no
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1 # set to 1 if they say yes
                    #ratings[curr_row][j] = curr_val
                ratings[curr_row][curr_val] += 1
        #f_kappas.append(fleiss_kappa(ratings)) # pass in ratings matrix to fleiss kappa calculator
        matrix = concatMatrices(matrix, ratings)

    # get average fleiss kappa value
    mat = np.matrix(matrix)
    return fleiss_kappa(mat)


def getKripAlpha(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    alphas = list()

    # get kripp's alpha of each set of three annotators
    for i in range(1, sheet.nrows, 3):
        ratings = np.zeros([3, sheet.ncols], dtype=int) # matrix of ratings where each row is a different rater and each column an answer to a question
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0 # set to 0 if they say no
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1 # set to 1 if they say yes
                    ratings[curr_row][j] = curr_val
        alphas.append(krippendorff_alpha(ratings)) # get kripp_alpha for current ratings matrix; NOTE: the kripp_alpha function is in krippendorff_alpha.py!

    # get average krip alpha value
    ave = 0
    for num in alphas:
        ave += num
    return float( float(ave) / float(len(alphas)))



def get_agreement_pairwise(matrix):
    num_agreements = 0
    x = range(len(matrix))
    combos = itertools.combinations(x, 2)
    for combo in combos:
        rater1 = combo[0]
        rater2 = combo[1]
        for j in range(len(matrix[0])):
            if matrix[rater1][j] == matrix[rater2][j]:
                num_agreements += 1

    return num_agreements

'''
Pairwise inter-annotator agreement as told by Mai
First, get mapping from id to reviewer object
Then, save all answers in reviewer object as some id
'''
def interAnnotatorAgreement(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    matrix = [[0 for x in range(2)] for y in range(1)]

    num_sentences = 0
    agreements = 0

    # get fleiss kappa of each set of three annotators
    for i in range(1, sheet.nrows, 3):
        num_sentences += 10


        ratings = [[0 for x in range(10)] for y in range(3)]
        for curr_row in range(0, 3):
            for j in range(0, sheet.ncols):
                curr_val = 0  # set to 0 if they say no
                if sheet.cell_value(i + curr_row, j) == 'yes':
                    curr_val = 1  # set to 1 if they say yes
                    # ratings[curr_row][j] = curr_val
                ratings[curr_row][curr_val] += 1
        agreements += get_agreement_pairwise(ratings)
        #matrix = concatMatrices(matrix, ratings)

    return agreements / (num_sentences * 3)

    '''
    num_pairs = 3 * num_sentences

    num_pairs = 3 * num_sentences  # incase you have 3 workers
    agreements = 0
    for sen in sentences:
        pair1 = agreement(w1, w2)
        pair2 = agreement(w1, w3)
        pair3 = agreement(w2, w3)

    if pair1: agreements += 1
    if pair2: agreements += 1
    if pair3: agreements += 1

% agreement = agreements / num_pairs
'''



if __name__ == '__main__':
    #getAgreement('Datasets/FullStudyResults.xls')
    #print(getFleissKappa('Datasets/FullStudyResults.xls'))
    #print(getKripAlpha('Datasets/FullStudyResults.xls'))
    print(interAnnotatorAgreement('Datasets/FullStudyResults.xls'))


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