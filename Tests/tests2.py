import requests

person_json = requests.get('http://dbpedia.org/data/Barack_Obama.json').json()
person_data = person_json['http://dbpedia.org/resource/Barack_Obama']
#person_attr = person_data['http://dbpedia.org/ontology/' + attribute][0]['value']
gender = person_data['http://xmlns.com/foaf/0.1/gender'][0]['value']
print(gender)

'''
for thing in person_data:
    if 'gender' in thing or 'spouse' in thing:
        print(thing)
'''


spears_json = requests.get('http://dbpedia.org/data/Britney_Spears.json').json()
spears_data = spears_json['http://dbpedia.org/resource/Britney_Spears']
for thing in spears_data:
    print(thing)