import os
from multiprocessing import Pool, cpu_count
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys
sys.path.insert(0, '../../DBPedia/')

from ParseDBPedia import *


def getArticleForPerson(name):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(chrome_options=options)

    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')


    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    browser.quit()
    return name + "\n" + curr_article_text

def createArticlesFile(names_file1, names_file2):
    names = list()
    with open(names_file1, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())
    with open(names_file2, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())

    file = open('wiki_files.txt', 'w', os.O_NONBLOCK)

    # multiple processes
    p = Pool(cpu_count() - 1)
    for result in p.map(getArticleForPerson, names):
        file.write(result)
        file.flush()


if __name__ == '__main__':
    createArticlesFile(sys.argv[1],sys.argv[2])