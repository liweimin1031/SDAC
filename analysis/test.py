# coding:utf-8  
from gensim import corpora, models  
import jieba  

from unit import dbUnit  


def get_stop_words_set(file_name):  
    with open(file_name, 'r') as file:
        lines = []
        for line in file:
            line = line.decode('utf-8').strip()
            lines.append(line)
        # print lines
        return lines
        # return set([line.strip().decode('utf-8') for line in file])  
  
def get_words_list(stop_word_file):  
    stop_words_set = get_stop_words_set(stop_word_file)
    print "şı±è®¡å¯¼å…¥ %d ä¸ªåşışı¨èşı" % len(stop_words_set)  
    word_list = []  
    jieba.load_userdict("userdict.txt")
    test = dbUnit()
    text = test.getTitle()
    for line in text:  
        tmp_list = list(jieba.cut(line, cut_all=False))  
        words = []
        for term in tmp_list:
            if term not in stop_words_set:
                words.append(term.strip())
        word_list.append(words)
        # word_list.append([term for term in tmp_list if term not in stop_words_set]) #æ³¨æşıè¿™éşıtermşı¯unicodeç±»åşıï¼Œåşışıœäşıè½¬æşıstrï¼Œåˆ¤şı­äşıä¸ºåşı  
    return word_list  
  
  

stop_word_file = 'stop_words.txt'
word_list = get_words_list(stop_word_file)  # şı—è¡¨ï¼Œå…¶ä¸­æşıä¸ªåşıç´ äşışı¯äşıä¸ªåşıè¡¨ïşışı³æşıè¡Œæşıå­—åşıè¯åşıå½¢æşışı„èşıè¯­åşıè¡şı 
word_dict = corpora.Dictionary(word_list)  # şıŸæşışı‡æ¡£şı„èşışı¸ïşıæ¯ä¸ªè¯äşıä¸şı¸ªşı´åşıç´¢åşışı¼å¯¹åºşı 
corpus_list = [word_dict.doc2bow(texts) for texts in word_list]  # è¯éşıç»Ÿè®¡ï¼Œè½¬şı–æşıç©ºé—´şı‘éşışı¼åşı  
tfidf = models.TfidfModel(corpus_list)
corpus_tfidf = tfidf[corpus_list]

lda = models.ldamodel.LdaModel(corpus=corpus_list, id2word=word_dict, num_topics=10, alpha='auto')  

for pattern in lda.print_topics():  
    print  pattern[1]
 
'''   
doc_lda = lda[corpus_tfidf]
for x in doc_lda:
    print x
    
    '''
