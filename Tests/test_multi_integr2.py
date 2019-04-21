from multiprocessing.pool import Pool
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from itertools import product
from collections import defaultdict
import nltk
import os
import time
import requests
import xlwt


def formatName(name):
    words = name.split()
    name = ""
    for i in range(len(words)):
        name += words[i]
        if i != len(words) - 1:
             name += "_"
    return name

def getArticleForPerson(name):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    return name + "\n" + curr_article_text
    #print(curr_article_text)





def createArticlesFile(names_file1, names_file2):
    names = list()
    with open(names_file1, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())
    with open(names_file2, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())

    file = open('wiki_files.txt', 'w', os.O_NONBLOCK)

    p = Pool(5)
    for result in p.map(getArticleForPerson, names):
        file.write(result)
        file.flush()



def wait_until_sentences_ready(article_file, person_name, timeout, period):
    mustend = time.time() + timeout
    while time.time() < mustend:
        # article = getArticleForPerson(person_name, browser)
        articles_file = open(article_file, 'r', os.O_NONBLOCK)
        article = ""
        for line in articles_file:
            if line.strip() == person_name:
                article = next(articles_file)
        if article != "":
            return article
        time.sleep(period)
    return "NO ARTICLE"





'''
Precondition:
    person_name is the name of the person for which you want sentences
    attrib_vals is a list of tuples (atribute, attr_value)
    browser is a selenium web browser
Postcondition:
    returns a dictionary that maps attrib --> list of sentences
'''
def getSentences(person_name, attrib_vals, article_file):
    attribs_2_sentences = defaultdict(list)

    '''
    #article = getArticleForPerson(person_name, browser)
    articles_file = open(article_file, 'r', os.O_NONBLOCK)
    article = ""
    for line in articles_file:
        if line.strip() == person_name:
            article = next(articles_file)
    if(article != ""):
    '''
    article = wait_until_sentences_ready(article_file, person_name, 100, 0.25)
    if(article != "NO ARTICLE"):
        for sentence in nltk.sent_tokenize(article):
            for attrib_val in attrib_vals:
                if attrib_val[1] in sentence:
                    attribs_2_sentences[attrib_val[0]].append(sentence)
    '''
    else:
        # we need to waitand do this again
        # not sure what to put here yet
        print("in else loop")
        getSentences(person_name, attrib_vals, article_file)
    '''

    return attribs_2_sentences


'''
Preconditions:
    url is a DBPedia url with a name at the end
Postcondition:
    Returns the name in plain English (i.e. without the preceding url and the underscore)
'''
def getNameFromUrl(url):
    words = url.split('/')
    name = words[-1]
    if '(' in name:
        name = name[0:name.rindex('(') - 1]
    name = name.replace('_', ' ')
    return name

'''
Precondition:
    date is a date from DBPedia in DBPedia format (year-month-day)
Postcondition:
    returns date in the format month day, year
'''
def formatDate(date):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                 'August', 'September', 'October', 'November', 'December']

    year, month, day = date.split('-')

    return str(months[int(month) - 1]) + " " + str(day) + ", " + str(year)

'''
Preconditions:
    person_name is a valid name for a person on Wikipedia
    attribute is a valid wikipedia attribute
Postcondition:
    returns value for that attribute for that person.
'''
def getAttributeForPerson(person_name, attribute):
    try:
        person_name = formatName(person_name)
        person_json = requests.get('http://dbpedia.org/data/' + person_name + '.json').json()
        person_data = person_json['http://dbpedia.org/resource/' + person_name]
        try:
            person_attr = person_data['http://dbpedia.org/ontology/' + attribute][0]['value']
        except:
            try:
                person_attr = person_data['http://xmlns.com/foaf/0.1/' + attribute][0]['value']
            except:
                try:
                    person_attr = person_data['http://dbpedia.org/property/' + attribute][0]['value']
                except:
                    try:
                        person_attr = person_data['http://www.w3.org/1999/02/22-rdf-syntax-ns#' + attribute][0]['value']
                    except:
                        try:
                            person_attr = person_data['http://purl.org/linguistics/gold/' + attribute][0]['value']
                        except:
                            return 'ERROR: could not find attribute'

        if('/' in person_attr or '_' in person_attr):
            person_attr = getNameFromUrl(person_attr)
        if(attribute == "birthDate"):
            person_attr = formatDate(person_attr)
        return person_attr
    except:
        return 'ERROR: could not find attribute'


'''
Precondition:
    person_file_path is the name of a file with person names for one gender
    attribs is a list of strings that represent the attributes we want to put in the database
    dataset_name is the name of your dataset wihtout file extension
    browser is a selenium web browser
Postcondition:
    Creates an Excel spreadsheet with columns:
    PersonName Attribute1 Attribute2 ... AttributeN
    and with all entries filled in
'''
def createDataset(person_file_path, attribs, dataset_name, browser):
    # create excel spreadsheet
    dataset = xlwt.Workbook()
    dataset_sheet = dataset.add_sheet('data')
    dataset_sheet.write(0, 0, "Full Name")
    for i in range(len(attribs)):
        dataset_sheet.write(0, (i+1), attribs[i])



    # get file to read names from
    person_file = open(person_file_path, 'r')

    # elinimate issues with saving file name later
    person_file_path = person_file_path.replace('/', '_')

    #count rows in workbook so that we know where to write data
    row_counter = 1

    #run multiple processes to speed things up
    pool = Pool(3)

    for line in person_file.readlines():
        name = formatName(line.strip())
        print(name)
        curr_person_attribs = list()
        write = True
        pool_inputs = list()
        for attrib in attribs:
            pool_inputs.append((name, attrib))
        for curr_person_attrib in pool.starmap(getAttributeForPerson, pool_inputs):
            if (curr_person_attrib == "ERROR: could not find attribute"):
                # if this is true, then this person doesn't have all the attributes we want; thus, we discard this data point
                write = False
                break
            else:
                curr_person_attribs.append(getAttributeForPerson(name, attrib))
        if(write):
            #now, write person to excel sheet
            dataset_sheet.write(row_counter, 0, line.strip())
            for i in range(len(curr_person_attribs)):
                dataset_sheet.write(row_counter, (i+1), curr_person_attribs[i])
            #row_counter += 1

            '''here, we need to write all the sentences'''
            # form list of attribute_vals tuples
            attribute_vals = list()
            for i in range(0, len(attribs)):
                # attribute_vals.append((dataset_sheet.cell(0, i), (dataset_sheet.cell(row_counter, i))))
                attribute_vals.append((attribs[i], curr_person_attribs[i]))
            try:
                attribs_2_sentences = getSentences(name, attribute_vals, 'wiki_files.txt')
                max_row = 0
                temp_row_counter = row_counter + 1
                for attrib in attribs_2_sentences:
                    col = attribs.index(attrib) + 1
                    for sentence in attribs_2_sentences[attrib]:
                        dataset_sheet.write(temp_row_counter, col, sentence)
                        temp_row_counter += 1
                    if temp_row_counter > max_row:
                        max_row = temp_row_counter
                    temp_row_counter = row_counter + 1

                row_counter = max_row
            except:
                print("ERROR getting sentences for: " + str(name))
                continue

        # save intermittently
        if(row_counter % 200 == 0):
            dataset.save('AttributeDatasets/' + dataset_name + "_" + person_file_path + "_" + ".xls")
        dataset.save('AttributeDatasets/' + dataset_name + "_" + person_file_path + "_" + ".xls")




'''
THIS WORKS!!!!
but we still need to keep another multithread of workers going who will find the attributes faster as well!
'''
if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    createDataset('test_names.txt', ['hypernym', 'birthDate', 'birthPlace'], 'test.xls', browser)