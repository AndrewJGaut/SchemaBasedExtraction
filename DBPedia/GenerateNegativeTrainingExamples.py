from ParseDBPedia import *
import xlrd
import xlwt
import nltk
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def genNegExamples(person_file_path, dataset_name, browser):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    dataset_sheet.write(0, 1, "NA")



    # get file to read names from
    person_file = open(person_file_path, 'r')

    # elinimate issues with saving file name later
    person_file_path = person_file_path.replace('/', '_')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    for line in person_file.readlines():
        pass