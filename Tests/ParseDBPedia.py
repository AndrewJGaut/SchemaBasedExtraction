import requests

'''
def getJsonForPerson(person_name):
    return requests.get('http://dbpedia.org/data/' + person_name + '.json').json()
'''


'''
Preconditions:
    url is a DBPedia url with a name at the end
Postcondition:
    Returns the name in plain English (i.e. without the preceding url and the underscore)
'''
def getNameFromUrl(url):
    words = url.split('/')
    name = words[-1]
    fname, lname = name.split('_')
    return fname + " " + lname


'''
Preconditions:
    person_name is a valid name for a person WITH ALL SPACES IN THE NAME SEPERATED BY UNDERSCORES
    attribute is a valid wikipedia attribute
Postcondition:
    returns value for that attribute for that person.
'''
def getAttributeForPerson(person_name, attribute):
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
                return 'ERROR: could not find attribute'

    if('/' in person_attr or '_' in person_attr):
        person_attr = getNameFromUrl(person_attr)
    return person_attr


if __name__ == '__main__':
    print(getAttributeForPerson('Barack_Obama', 'gender'))
    print(getAttributeForPerson('Barack_Obama', 'spouse'))
    print(getAttributeForPerson('Britney_Spears', 'gender'))

