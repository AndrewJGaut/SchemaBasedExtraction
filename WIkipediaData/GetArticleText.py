from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys


'''
Precondition:
    name is an unformatted string representing a name
Postcondition:
    returns that name formatted in DBPedia style
'''
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
def getArticleForPerson(name, browser):
    browser.get('https://en.wikipedia.org/wiki/' + formatName(name))
    p_tags = browser.find_elements_by_tag_name('p')

    curr_article_text = ""
    for p_tag in p_tags:
        curr_article_text += p_tag.text

    return curr_article_text



if __name__ == '__main__':
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)

    names = ["Michelle Obama"] #currently just for testing

    for name in names:
        print(getArticleForPerson('Michelle Obama', browser))