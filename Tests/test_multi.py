from multiprocessing.pool import Pool
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


'''
Precondition:
    name is the name of a person with a Wikipedia article
    browser is a Chrome, Selenium webdriver
Postcondition:
    Returns the full text of that person's Wikipedia article
'''
'''
def getArticleForPerson(name, browser):
    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    #return curr_article_text
    print(curr_article_text)
'''

def listener(queue):
    '''listens for messages on the queue, writes to file. '''

    f = open('test_file.txt', 'wb')
    while 1:
        m = queue.get()
        if m == 'kill':
            break
        f.write(str(m) + '\n')
        f.flush()
    f.close()


def getArticleForPerson(name):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    #return curr_article_text
    print(curr_article_text)



options = Options()
options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=options)

#names = [("Barack Obama", browser), ("Kobe Bryant", browser), ("Winston Churchill",browser), ("Dirk Nowitzki", browser), ("Elgin Baylor",browser)]
names = ["Barack Obama", "Kobe Bryant", "Winston Churchill", "Dirk Nowitzki", "Elgin Baylor"]

from time import time

curr_time = time()


with Pool(5) as p:
    p.map(getArticleForPerson, names)

'''
for name in names:
    getArticleForPerson(name, browser)
'''

print(str(time() - curr_time))


'''
POOL SYNTAX:
with Pool(4) as p
    p.map(FUNCTION_TO_EXECUTE, DATA_TO_EXECUTE_ON)
'''


def getArticleForPerson2(name):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    #return curr_article_text
    print(curr_article_text)

manager = Pool.Manager()
queue = manager.Queue()
p.apply_async(listener, (queue,))
jobs = []
for name in names:
    job = p.apply_async(getArticleForPerson2, (name, queue))

for job in jobs:
    job.get()

queue.put('kill')
p.join()
p.close()