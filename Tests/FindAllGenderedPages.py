from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def getNames(browser):
    names = list()
    rows = browser.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        try:
            data = row.find_element_by_tag_name('pre')
            name = data.split('@')[0]
            name = name[1:-1]
            names.append(name)
        except:
            print("ERROR")

    return sorted(names)

'''
def getNames(browser):
    names = list()
    try:
        names_tags = browser.find_elements(By.TAG_NAME, 'pre')
        for name in names_tags:
            name = name.text.split('@')[0]
            name = name[1:-1]
            names.append(name)
    except:
        print("ERROR")

    return sorted(names)
'''


if __name__ == '__main__':
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)

    #browser.get('http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=PREFIX+foaf%3A++%3Chttp%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F%3E%0D%0ASELECT+%3Fname%0D%0AWHERE+%7B%0D%0A++++%3Fperson+foaf%3Aname+%3Fname+.%0D%0A++++%3Fperson+rdf%3Atype+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPerson%3E%0D%0A%7D%0D%0A&format=text%2Fhtml&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+')
    browser.get('http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=PREFIX+foaf%3A++%3Chttp%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F%3E%0D%0ASELECT+%3Fname%0D%0AWHERE+%7B%0D%0A++++%3Fperson+foaf%3Aname+%3Fname+.%0D%0A++++%3Fperson+rdf%3Atype+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPerson%3E%0D%0A%7D%0D%0A&format=text%2Fx-html%2Btr&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+')
    nameList = getNames(browser)
    print(nameList)