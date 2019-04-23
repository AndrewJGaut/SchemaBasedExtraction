import os
from multiprocessing import Pool, cpu_count, Queue, Manager
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys
sys.path.insert(0, '../../DBPedia/')

from ParseDBPedia import *

def writeToArticleFile(queue):
    file = open('wiki_files.txt', 'w', os.O_NONBLOCK)

    while True:
        next = queue.get()
        if(next == "DONE"):
            #then we're done writing to file
            break
        file.write(next + "\n")
        file.flush()

    file.close()


def getArticleForPerson(name, queue):
    options = Options()
    options.add_argument("--headless")
    #options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(chrome_options=options)

    name = formatName(name)
    browser.get('https://en.wikipedia.org/wiki/' + name)
    p_tags = browser.find_elements_by_tag_name('p')


    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    browser.quit()
    queue.put(name + "\n" + curr_article_text + "\n")
    #writeToArticle(name + "\n" + curr_article_text, queue)

def createArticlesFile(names_file1, names_file2):
    names = list()
    with open(names_file1, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())
    with open(names_file2, 'r') as file:
        for line in file.readlines():
            names.append(line.strip())


    manager = Manager()
    queue = manager.Queue()



    # multiple processes
    '''
    NOTE!!!!: POOL.MAP FUNCTION CALL BLOCKS UNTIL ALLLLLL VALUES ARE RETURNED!
    THIS, DOESN'T SPEED ANYTHING UP AT ALL!!!!
    '''
    p = Pool(cpu_count() - 1)
    p.apply_async(writeToArticleFile, (queue,))
    tuples = list()
    for name in names:
        tuples.append((name, queue))
    # do this with multiple processes
    p.starmap(getArticleForPerson, tuples)

    print("PAST PROCESSES")
    queue.put("DONE")




if __name__ == '__main__':
    createArticlesFile(sys.argv[1],sys.argv[2])