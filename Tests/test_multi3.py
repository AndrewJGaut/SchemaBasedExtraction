'''THIS WORKS!!!!'''


from multiprocessing.pool import Pool
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from itertools import product


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

    return curr_article_text
    #print(curr_article_text)



names = ["Barack Obama", "Kobe Bryant", "Winston Churchill", "Dirk Nowitzki", "Elgin Baylor"]
def createArticlesFile(names):
    file = open('test_out.txt', 'w')

    p = Pool(5)
    for result in p.map(getArticleForPerson, names):
        file.write(result)
