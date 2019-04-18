'''
This has code which can sort through entities and determine which are decidely male and which are decidely female
It then outputs a list of the names of these entities to two files
'''

import requests
import os



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
        return person_attr
    except:
        return 'ERROR: could not find attribute'
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
Postcondition:
    returns a sorted list (which is noisy) of names gotten from DBPedia using a SPARQL query
'''
def getNamesForDBPediaEntities():
    names = list()
    with open('dbpedia_query.txt') as names_file:
        for line in names_file.readlines():
            if '<td><pre>' in line:
                names.append(line[13:-12])

    return sorted(names)

'''
Postcondition:
    For all names in the dbpedia_query file, checks if that name represents a male or female entity
    Returns a dict of all male entities first, then a dict of all female entities
'''
def getGenderedLists():
    males = dict()
    females = dict()

    names = getNamesForDBPediaEntities()

    for name in names:
        formattedName = formatName(name)
        try:
            gender = getAttributeForPerson(formattedName, 'gender')
        except:
            continue
        if(gender == 'male'):
            if name not in males:
                males[name] = name
        if(gender == 'female'):
            if name not in females:
                females[name] = name

    return males, females

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


'''
Precondition:
    males is a dict with names representing male entities
    females is a dict with names representing female entities
Postcondition:
    writes these names to files so that we have all males and all females
'''
def writeKeysToFiles(parent_dir, males, females):
    os.makedirs(parent_dir, exist_ok=True)

    with open(os.path.join(parent_dir, 'male_names.txt'), 'w') as file:
        for name in males:
            file.write(name+'\n')
    with open(os.path.join(parent_dir, 'female_names.txt'), 'w') as file:
        for name in females:
            file.write(name+'\n')









if __name__ == '__main__':
    print(getAttributeForPerson('Barack_Obama', 'gender'))
    print(getAttributeForPerson('Barack_Obama', 'spouse'))
    print(getAttributeForPerson('Britney_Spears', 'gender'))

    males, females = getGenderedLists()
    writeKeysToFiles('QueryPeople/', males, females)



'''
SPARQL query used to obtain dbpedia_query.txt:

PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE {
    ?person foaf:name ?name .
    ?person rdf:type <http://dbpedia.org/ontology/Person>
}
'''
