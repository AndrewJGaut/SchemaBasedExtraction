from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import nltk
from TextPreprocessing import *
from ParseDBPedia import *
from random import randint
import string


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
    names is a list of names of entities with Wikipedia articles
Postcondition:
    Returns a LEMMATIZED list of articles for those people
'''
def getArticlesForPeople(names):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=options)
    articles = list()

    for name in names:
        try:
            article = getArticleForPerson(name, browser)
            articles.append(lemmatize(article))
        except:
            print("NO ARTICLE FOUND FOR " + str(name))

    return articles

'''
Precondition:
    article is e1's WIkipedia article that is ALREADY LEMMATIZED
    relation is the relation between the two entities
    e1 is the entity from whose Wikipedia article we are taking sentences
    e2 is the entity that relates to e1 in the relation on DBPedia
    (e.g. Barack marriedTo Michelle --> relation:marriedTo, e1:Barack, e2:Michelle)
Postcondition:
    returns a list of tuples representing relations
'''
def getRelationTuples(article, relation, e1, e2):
    relations = list()
    e1 = lemmatize(e1)
    e2 = lemmatize(e2)
    for sentence in nltk.sent_tokenize(article):
        if e1 in sentence and e2 in sentence:
            # then we know we want this relation tuple
            sentence = opennreFormatSentence(sentence)
            relations.append((relation, e1, e2, sentence))

    return relations

'''
Precondition:
    sentence is a string of English
Postcondition:
    formats sentence for OpenNRE model
'''
def opennreFormatSentence(sentence):
    new_sentence = ""
    for word in nltk.word_tokenize(sentence):
        new_sentence += word.lower() + " "

    return new_sentence



'''
Postcondition:
    Returns an entity id for training data compatible with OpenNRE
'''
def genId():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    id = "m."

    for i in range(5):
        id += chars[randint(0, 35)]

    return id

'''
Precondition:
    relations is a list of ALL the relations we've obtained
    each relation in relations is a tuple (relation, entity1, entity2, sentence)
Postcondition:
    creates train.json and rel2id.json files
'''
def createOpenNREFiles(relations):
    # files to write to later
    training_json = open('OpenNRETrainingData/train.json', 'w')
    rel_to_id = open('OpenNRETrainingData/rel2id.json', 'w')


    names2ids = dict()
    ids_in_use = set()
    unique_relations = set()
    training_json_string = "[\n"


    id_e1 = ""
    id_e2 = ""
    for relation in relations:
        try:
            # give entities ids!
            if relation[1] not in names2ids:
                while True:
                    id_e1 = genId()
                    if id_e1 not in ids_in_use:
                        break
                names2ids[relation[1]] = id_e1
            else:
                id_e1 = names2ids[relation[1]]

            if relation[2] not in names2ids:
                id_e2 = ""
                while True:
                    id_e2 = genId()
                    if id_e2 not in ids_in_use:
                        break
                names2ids[relation[2]] = id_e2
            else:
                id_e2 = names2ids[relation[2]]

            # get relations (so we can map to ids later)
            if relation[0] not in unique_relations:
                unique_relations.add(relation[0])


            # add to the training_json string
            training_json_string += "\t{" + "\n"
            training_json_string += "\t\t\'sentence\': " + "\'" + str(relation[3]) + "\',\n"
            training_json_string += "\t\t\'head\': {\'word\': " + "\'" + str(relation[1]) + "\', \'id\': \'" + id_e1 + "\'},\n"
            training_json_string += "\t\t\'tail\': {\'word\': " + "\'" + str(relation[2]) + "\', \'id\': \'" + id_e2 + "\'},\n"
            training_json_string += "\t\t\'relation\': \'" + relation[0] + "\'\n"
            training_json_string += "\t},\n"
        except:
            print("BAD RELATION")

    training_json_string = training_json_string[0:-2]
    training_json_string += "\n]"

    # get relation to id mapping data
    relation_to_id_mapping_string = "{\n\t\'NA\': 0,\n"
    rel_counter = 1
    for rel in unique_relations:
        relation_to_id_mapping_string += "\t\'" + str(rel) + "\': " + str(rel_counter) + ",\n"
        rel_counter += 1
    relation_to_id_mapping_string = relation_to_id_mapping_string[0:-2]
    relation_to_id_mapping_string += "\n}"

    #write to files
    training_json.write(training_json_string)
    training_json.close()

    rel_to_id.write(relation_to_id_mapping_string)
    rel_to_id.close()


def formatWordVectorFile(vec_file):
    formatted_word_vecs_string = "[\n"

    file = open(vec_file, 'r')
    for line in file.readlines():
        items = line.split()
        print(items[0])
        formatted_word_vecs_string += "\t{\'word\': \'" + str(items[0]) + "\',\'vec\': ["
        for i in range(1, len(items)):
            formatted_word_vecs_string += str(items[i]) + ", "
        formatted_word_vecs_string = formatted_word_vecs_string[0:-1]
        formatted_word_vecs_string += "]},\n"

    formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
    formatted_word_vecs_string += "}\n]"

    out_file = open(vec_file + "_formatted.json", 'w')
    out_file.write(formatted_word_vecs_string)



if __name__ == '__main__':
    '''
    names = ['Michelle Obama', 'Kobe Bryant', 'Winston Churchill']
    articles = getArticlesForPeople(names)
    print(articles)
    '''
    articles = getArticlesForPeople(['Michelle Obama', 'Kobe Bryant'])
    relations = getRelationTuples(articles[0], 'spouse', 'Barack', 'Michelle')
    relations.append(getRelationTuples(articles[1], 'nationality', 'Kobe', 'American'))
    createOpenNREFiles(relations)


    #createOpenNREFiles([('spouse', 'Barack', 'Michelle', 'Barack is Michelle\'s husband'), ('father', 'John', 'Smitty', 'John fathered Smitty in 1852.'), ('father', 'Barack', 'Jeff', 'Barack fathered Jeff in 1852.')])
    #formatWordVectorFile('vectors.txt')