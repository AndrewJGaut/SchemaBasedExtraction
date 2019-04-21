from multiprocessing.pool import Pool
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from itertools import product
from collections import defaultdict
import nltk
import os
import time



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





def createArticlesFile(names):
    file = open('test_out.txt', 'w', os.O_NONBLOCK)

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
    else:
        # we need to waitand do this again
        # not sure what to put here yet
        print("in else loop")
        getSentences(person_name, attrib_vals, article_file)

    return attribs_2_sentences




'''
THIS WORKS!!!!
but we still need to keep another multithread of workers going who will find the attributes faster as well!
'''
if __name__ == "__main__":
    names = ["Barack Obama", "Kobe Bryant", "Winston Churchill", "Dirk Nowitzki", "Elgin Baylor"]
    createArticlesFile(names)
    print(getSentences("Barack Obama", ['spouse', 'Michelle'], 'test_out.txt'))