from gensim.models import Word2Vec
import nltk
# define training data


def getSentences(datapath):
    sent_file = open(datapath, 'r')
    sentences = list()

    i = 0
    for sent in sent_file.readlines():
        sentences.append(nltk.word_tokenize(sent))
        i+=1

    print(i)
    return sentences

'''
Precondition:
    vec_file is a word vector file of the form word num1 num2 ... numn \n word2 num1 ...etc
Postcondition:
    formats vector file so it works for OpenNRE
'''
'''
def formatWordVectorFile(model):
    formatted_word_vecs_string = "[\n"

    for word in model.wv.vocab:
        print(str(word))
        formatted_word_vecs_string += "\t{\"word\": \"" + str(word) + "\",\"vec\": ["
        for item in model[word]:
            formatted_word_vecs_string += str(item) + ", "
        formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
        formatted_word_vecs_string += "]},\n"

    formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
    formatted_word_vecs_string += "}\n]"

    out_file = open('word_vec.json', 'w')
    out_file.write(formatted_word_vecs_string)
    out_file.close()
'''

def formatWordVectorFile(vec_file):
    formatted_word_vecs_string = "[\n"

    file = open(vec_file, 'r')
    for line in file.readlines():
        line = line.strip()
        if line == '': continue
        items = line.split()
        for i in range(len(items)):
            if items[i] == '':
                items.pop(i)
        print(items[0])
        formatted_word_vecs_string += "\t{\"word\": \"" + str(items[0]) + "\",\"vec\": ["
        for i in range(1, len(items)):
            formatted_word_vecs_string += str(items[i]) + ", "
        formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
        formatted_word_vecs_string += "]},\n"

    formatted_word_vecs_string = formatted_word_vecs_string[0:-2]
    formatted_word_vecs_string += "\n]"

    out_file = open(vec_file + "_formatted.json", 'w')
    out_file.write(formatted_word_vecs_string)

def preprocessDebiasedFile(str1):
    #wordvec = open(file_name, 'r')
    new_str = ""
    counter = 0
    for vec in str1.split(']'):
        print(str(counter))
        counter += 1
        vec = vec.replace('\n', ' ')
        curr_vec = vec.replace('[', ' ')
        #words = nltk.word_tokenize(vec)
        #curr_vec = ' '.join(words[1:])
        new_str = '\n'.join([new_str,curr_vec])

    out_file = open('debiased_prepr.txt', 'w')
    out_file.write(new_str)
    return new_str




if __name__=='__main__':
    wordvecstr = open('debiased_word_vec.txt', 'r').read()
    #x = preprocessDebiasedFile('the [0.234324 0.123432\n 0.1234 \n ] \n I [0.12344 0.12343 0.1234 \n 0.5232 \n ]')
    x = preprocessDebiasedFile(wordvecstr)
    print(x)
    formatWordVectorFile('debiased_prepr.txt')
    '''
    #get sentences
    sentences = getSentences('datasets/all_sentences.txt')

    # train model
    model = Word2Vec(sentences, min_count=1)

    print(model)

    # summarize vocabulary
    words = list(model.wv.vocab)
    print(words)
    # access vector for one word
    #print(model['sentence'])
    # save model
    #model.save('model.bin')
    print(model[model.wv.vocab])
    model.wv.save_word2vec_format('word_vec.txt')
    #model = Word2Vec.load('model.bin')

    #print(model[model.wv.vocab])
    #model.wv.save_word2vec_format('model.txt')
    #formatWordVectorFile('model.txt')

    #now, load model and parse it
    '''
