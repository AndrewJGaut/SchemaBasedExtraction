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

def getArticleForPerson2(name, queue):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    queue.put(curr_article_text)
    print(curr_article_text)
    return curr_article_text


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


names = ["Barack Obama", "Kobe Bryant", "Winston Churchill", "Dirk Nowitzki", "Elgin Baylor"]
p = Pool(5)
manager = mp.Manager()
queue = mp.Queue()
watcher = p.apply_async(listener, (queue,))
jobs = []
for name in names:
    job = p.apply_async(getArticleForPerson2, (name, queue))

for job in jobs:
    job.get()

queue.put('kill')
p.close()
p.join()