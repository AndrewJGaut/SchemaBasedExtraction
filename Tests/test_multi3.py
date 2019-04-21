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



names = ["Barack Obama", "Kobe Bryant", "Winston Churchill", "Dirk Nowitzki", "Elgin Baylor"]
def createArticlesFile(names):
    file = open('test_out.txt', 'w')

    p = Pool(5)
    for result in p.map(getArticleForPerson, names):
        file.write(result)

    for attrib in p.map(getAttributeForPerson, )
