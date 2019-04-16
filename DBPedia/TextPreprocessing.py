from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.stem import LancasterStemmer
import contractions
import nltk

stemmer = LancasterStemmer()
lemmatizer = WordNetLemmatizer()


'''
Preconditions:
    sentence is a string
Postcondition:
    returns lemmatized and simplified sentence (removes all contractions, sends sentence to lowercase, lemmatizes words)
'''
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

'''
Preconditions:
    treebank_tag is a valid POS tag from Penn Treebank: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)
Postconditions:
    maps tag to a wordnet POS type that nltk's lemmatizer accepts
'''
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

'''
Precondition:
    str1 and str2 are valid strings
Postcondition:
    Returns the Jaccard ndex of str1 and str2
    Jaccard Index info: https://towardsdatascience.com/overview-of-text-similarity-metrics-3397c4601f50
'''
def get_jaccard_sim(str1, str2):
    str1 = lemmatize(str1)
    str2 = lemmatize(str2)

    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


if __name__ == '__main__':
    pass

'''
print(lemmatize("I like apples; but I also like bananas"))
print(lemmatize("I'm playing ball, but I sure ain't the GOAT"))
print(lemmatize_nltk("AI is our friend and it has been friendly"))
print(lemmatize_nltk("AI and humans have always been friendly"))
print(get_jaccard_sim("AI is our friend and it has been friendly", "AI and humans have always been friendly"))
'''