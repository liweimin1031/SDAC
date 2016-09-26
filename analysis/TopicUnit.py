from gensim import corpora, models
from collections import OrderedDict
# --LDA model--#
def LDA(words_list):
    #input words_list is documents [ [ ] ,[ ], [ ]..... ]
    
    print('-' * 40)
    print(' LDA model ')
    print('-' * 40)
    word_dict = corpora.Dictionary(words_list) 
    corpus_list = [word_dict.doc2bow(texts) for texts in words_list]  
    tfidf = models.TfidfModel(corpus_list)
    corpus_tfidf = tfidf[corpus_list]
    lda = models.ldamodel.LdaModel(corpus=corpus_list, id2word=word_dict, num_topics=5, alpha='auto')  
    patterns = lda.print_topics()
    '''
    # --get keywords--#
    keywords = []
    for pattern in patterns:
        print  pattern[1]
        words_bag = pattern[1].split(' + ')
        words_list = []
        for words in words_bag:
            value_word = words.split('*')
            word = value_word[1]
            words_list.append(word)
        for w in words_list:    
            if w not in keywords:
                keywords.append(w.strip())
                break
            else:
                continue
    for word in keywords:           
        print word
        '''
        
    #--get keywords list all words--#
    keywords = []
    for pattern in patterns:
        print  pattern[1]
        words_bag = pattern[1].split(' + ')
        words_list = []
        word_value=OrderedDict()
        for words in words_bag:
            value_word = words.split('*')
            word = value_word[1]
            value=value_word[0]
            word_value[word]=value # 'weight1*word1 + weight2*word2...' ===>{'word1':'weight1','word2':'weight2'...} 
            #words_list.append(word)
        #keywords.append(words_list)
        keywords.append(word_value)
    return keywords