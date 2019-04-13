from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.stem import LancasterStemmer
import contractions
import nltk

stemmer = LancasterStemmer()
lemmatizer = WordNetLemmatizer()


def lemmatize(sentence):
    sentence = contractions.fix(sentence)
    pos_tags = pos_tag(nltk.word_tokenize(sentence))
    new_sentence = ""

    for i in range(len(pos_tags)):
        if not pos_tags[i][0].isalpha():
            new_sentence += pos_tags[i][0]
        else:
            stem = stemmer.stem(pos_tags[i][0])
            tag = get_wordnet_pos(pos_tags[i][1])

            '''
            print("----")
            print(stem)
            print(tag)
            print("----")
            '''

            lemma = pos_tags[i][0]
            if(tag != ''):
                #lemma = lemmatizer.lemmatize(stem, pos=tag)
                lemma = lemmatizer.lemmatize(pos_tags[i][0], pos=tag)
            new_sentence += " "
            new_sentence += lemma.lower()


    return new_sentence

def get_positions(sentence):
    pos_tags = pos_tag(nltk.word_tokenize(sentence))
    return pos_tags # returns list [(word, pos_tag), (), ()]

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

def get_jaccard_sim(str1, str2):
    str1 = lemmatize(str1)
    str2 = lemmatize(str2)

    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


print(lemmatize_nltk("I like apples; but I also like bananas"))
print(lemmatize_nltk("I'm playing ball, but I sure ain't the GOAT"))
print(lemmatize_nltk("AI is our friend and it has been friendly"))
print(lemmatize_nltk("AI and humans have always been friendly"))
print(get_jaccard_sim("AI is our friend and it has been friendly", "AI and humans have always been friendly"))