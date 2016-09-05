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
    print "���计导入 %d 个���������" % len(stop_words_set)  
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
        # word_list.append([term for term in tmp_list if term not in stop_words_set]) #注���这���term���unicode类���，���������转���str，判������为���  
    return word_list  
  
  

stop_word_file = 'stop_words.txt'
word_list = get_words_list(stop_word_file)  # ���表，其中���个���素���������个���表���������行���字���词���形���������语������ 
word_dict = corpora.Dictionary(word_list)  # ���������档������������每个词��������������索������对��� 
corpus_list = [word_dict.doc2bow(texts) for texts in word_list]  # 词���统计，转������空间������������  
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
