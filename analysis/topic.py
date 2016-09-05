# -*- coding: utf-8 -*-
from unit import dbUnit
from decorator import append
from gensim import corpora, models
import jieba
import jieba.analyse
from datetime import datetime
import jieba.posseg as pseg
# spark lib




# --test--#
# $example on$
# $example off$
test = dbUnit()

# comment=test.getContent()
# print comment

text = test.getContent()
with open('orgine.txt', 'w')as f:
    for s in text:
        for w in s:
            f.write(w.encode('utf-8'))
# cText=''.join(text)
'''
with open('dict.txt.big','a')as f,open('hkexDict_update.txt','r')as f1,open('oralDict.txt','r')as f2,open('userDict.txt','r')as f3:
    for w in f1.readlines():
        f.write(w)
    for w in f2.readlines():
        f.write(w)
    for w in f3.readlines():
        f.write(w)
'''
# --load dict--#
print'loading dict......'
jieba.load_userdict('dict.txt.big')

print'loading hkexDict......'
jieba.load_userdict('hkexDict_update.txt')
print'loading oralDict......'
jieba.load_userdict('oralDict.txt')
print'loading userDict......'
jieba.load_userdict('userDict.txt')

'''
#--set stop words--#
print'setting stop words......'
jieba.analyse.set_stop_words("stop_words.txt")
'''

'''
#-- jieba cut with word flag--#
pseg_list = pseg.cut(cText)
'''

# --set stop words--#
stopList = []
with open('oralDict.txt') as f1, open('stop_words_ch.txt')as f2, open('stop_words_custom.txt')as f3, open('stop_words_eng.txt')as f4:
    for word in f1.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f2.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f3.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f4.readlines():
        stopList.append(word.strip().decode('utf-8'))

# --set synonym dict--#
with open('hkexSynonym_update.txt') as f:
    data_list = f.readlines()
    synonymDict = {}
    for line in data_list:
        synonymList = line.strip().split(',')
        key = synonymList[0].decode('utf-8')
        value = synonymList[1].decode('utf-8')
        synonymDict[key] = value

def strQ2B(ustring):  
    rstring = ''
    for uchar in ustring:  
        inside_code = ord(uchar)  
        if inside_code == 12288:  # þý¨èþýç©ºæ ¼þý´æŽ¥è½¬æ¢              
            inside_code = 32   
        elif (inside_code >= 65281 and inside_code <= 65374):  # þý¨èþýå­—ç¬¦ï¼ˆé™¤ç©ºæ ¼ï¼‰æ ¹þý®å…³ç³»è½¬þýþý 
            inside_code -= 65248  
  
        rstring += unichr(inside_code)  
    return rstring  
# --replace synonym--#
def reSynonym(sDict, sentence):
    r_seg = []
    sum_replace = 0
    for seg in sentence:
        if sDict.has_key(seg):
            seg = sDict[seg]
            sum_replace += 1
            r_seg.append(seg)
   
# --delete stop words and replace synonym--#
def cleanWords(seg_list):
    c_seg = []
    sum_stop = 0
    sum_replace = 0

    for word in seg_list:
        if word.strip():
            seg = word.strip()
        # print seg
            if seg not in stopList:  # check stop words
                if synonymDict.has_key(seg):  # check synonym
                    seg = synonymDict[seg]       
                    sum_replace += 1
                c_seg.append(seg)
            else:
                sum_stop += 1

    return  c_seg, sum_stop, sum_replace
# --jieba cut--#
print'-' * 40
print' jieba cut'
print'-' * 40
words_list = []
sum_stop = 0
sum_replace = 0
sum_words = 0

for topic in text:
    text_analyse = ''.join(strQ2B(topic))
    seg_list = jieba.cut(strQ2B(topic), cut_all=False)
    words, n_stop, n_replace = cleanWords(seg_list)
    sum_stop = n_stop + sum_stop
    sum_replace = n_replace + sum_replace
    sum_words = sum_words + len(words)
    words_list.append(words)
print 'delete %d stop words' % sum_stop
print 'replace %d synonym' % sum_replace
print 'get %d sentence and %d words' % (len(words_list), sum_words)

with open('text.txt', 'w')as f:
    for s in words_list:
        for w in s:
            f.write(w.encode('utf-8') + ' ')

# seg_list=list(seg_list)
# print 'get %d words'%len(seg_list)


'''
#--NLTK analyse--#
print('-'*40)
print(' NLTK analyse ')
print('-'*40)
from nltk import collocations
bigram_measures = collocations.BigramAssocMeasures()
bigram_finder = collocations.BigramCollocationFinder.from_words(c_seg)
# Filter to top 20 results; otherwise this will take a LONG time to analyze
bigram_finder.apply_freq_filter(20)
for bigram in bigram_finder.score_ngrams(bigram_measures.raw_freq)[:10]:
    print bigram
'''
            
# --LDA model--#
print('-' * 40)
print(' LDA model ')
print('-' * 40)
word_dict = corpora.Dictionary(words_list)  # þýŸæþýþý‡æ¡£þý„èþýþý¸ïþýæ¯ä¸ªè¯äþýä¸þý¸ªþý´åþýç´¢åþýþý¼å¯¹åºþý 
corpus_list = [word_dict.doc2bow(texts) for texts in words_list]  # è¯éþýç»Ÿè®¡ï¼Œè½¬þý–æþýç©ºé—´þý‘éþýþý¼åþý  
tfidf = models.TfidfModel(corpus_list)
corpus_tfidf = tfidf[corpus_list]
lda = models.ldamodel.LdaModel(corpus=corpus_list, id2word=word_dict, num_topics=5, alpha='auto')  
patterns = lda.print_topics()
# --get keywords--#
keywords = []

for pattern in patterns:
    print  pattern[1]
    words_bag = pattern[1].split('+')
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
            break
for word in keywords:           
    print word

# --set re_synonym dict--#
with open('hkexSynonym_update.txt') as f:
    data_list = f.readlines()
    re_synonymDict = {}
    for line in data_list:
        re_synonymList = line.strip().split(',')
        value = re_synonymList[0].decode('utf-8')
        key = re_synonymList[1].decode('utf-8')
        if re_synonymDict.has_key(key):
            re_synonymDict[key].append(value)
        else:
            re_synonymDict[key] = [value]

topic_words = []
for word in keywords:
    if re_synonymDict.has_key(word):
        words = re_synonymDict[word]
        words.append(word)
        topic_words.append(words)
    else:
        topic_words.append([word])
print 'topic words db data'
posts = []
json_data = {
           'topic':string,
           'data':{
                   'date':string,
                   'content':arrayString,
                   'times':int
                   }
           }

with open('dbData.json', 'w')as f:
    for i, keywords in enumerate(topic_words):
        result_list = test.select_keywords(keywords)
        for keyword in keywords:
            topic = ''.join(keyword.encode('utf-8'))
            
        json_data['topic'] = topic
        
        f.write('topic %s \n' % (topic))
        post_create_time = {}
        for result in result_list:
            for text in result['content']['text']:
                content = ''.join(text.strip().encode('utf-8'))
            # content=''.join(result['content']['text']).encode('utf-8')
            date = result['post_create_date'].date()
            
            if post_create_time.has_key(date):
                post_create_time[date]['title'].append(result['title'].encode('utf-8'))
            else:
                pass
            post_create_time = result['post_create_date'].date()
            title = result['title'].encode('utf-8')
            link = result['link'].encode('utf-8')
            last_status = result['last_status'].encode('utf-8')
            f.write('post_create_time: %s , title: %s , reply: %s\n' % (post_create_time, title, last_status,))
            
            
            json_data['data']['date'] = post_create_time
            json_data['data']['content'] = title
            json_data['data']['times'] = int(last_status)


# --TF-IDF--#
print('-' * 40)
print(' TF-IDF')
print('-' * 40)
for x, w in jieba.analyse.extract_tags(text_analyse, topK=20, withWeight=True):
    print('%s %s' % (x, w))
    
'''
#--Text Rank--#
print('-'*40)
print(' TextRank ')
print('-'*40)
term=jieba.analyse.textrank(text_analyse, topK=20, withWeight=True)
for x, w  in term:
    print('%s %s' % (x, w))

'''

'''
#-- jieba cut with word flag--#
words = pseg.cut(cText)
nword = []
i=0
for w in words: 
    if((w.flag == 'n'or w.flag == 'v' or w.flag == 'a') and len(w.word)>1): 
        nword.append(w.word)
        #i+=1
        #print i
'''
'''
print('-'*40)
n_key_words=[]
v_key_words=[]

print('-'*40)
print(' TF-IDF')
print('-'*40)
for x, w in jieba.analyse.extract_tags(cText, topK=15,withWeight=True,allowPOS= ('n' )):
    print('%s %s' % (x, w))
    n_key_words.append(x)

print('-'*40)
for x, w in jieba.analyse.extract_tags(cText, topK=15,withWeight=True,allowPOS= ('v','vn','a','ad')):
    print('%s %s' % (x, w))
    v_key_words.append(x)
'''
'''
print('-'*40)
print(' TextRank with freq')
print('-'*40)
#c = Counter(seg_list)

term=jieba.analyse.textrank(text, topK=10, withWeight=True,allowPOS= ('n'))
for x, w  in term:
    print('%s %s' % (x, w))
    
print('-'*40)

a_term=jieba.analyse.textrank(text, topK=10, withWeight=True,allowPOS= ('a','d','v'))
for x, w  in a_term:
    print('%s %s' % (x, w))
'''
'''
topic_list=[]
for x,w in term:
    for i,y in a_term:
        topic=    w+y
        scort=abs(int(str(x))-int(str(i)))
        topic_tuple=(topic,scort)
        topic_list.append(topic_tuple)
print('-'*40)
print topic_list
freq=OrderedDict(sorted(topic_list,key=lambda t: t[1],reverse=True))
print('-'*40)
print freq
for x, w in freq.items():
    print('%s %s' % (x.encode('gb18030'), w))
'''
'''
print('-'*40)
print(' topic span')
print('-'*40)
span=2
for title in text:
    title_cut = jieba.cut(title, cut_all=False)
    title_cut = list(title_cut)
    for key_word in n_key_words:        
        key_index=[i for i, x in enumerate(title_cut) if x == key_word]
        for i in key_index:
            if i<=span :
                _topic=title_cut[0:(i+span+1)]
            if i>span :
                _topic=title_cut[(i-span):(i+span+1)]
            print ''.join(_topic)

print('-'*40)
'''
'''
A=n_key_words
B=v_key_words
title_list=text
print len(title_list)
def PA(n,m):
    topics=[]
    for x in n:
        for y in m:
            _a=0
            _ab=0
            P=0
            #print 'x:%s, y:%s' %(x,y)
            for title in title_list:
                #print title_list.index(title)
                if x in title:
                    _a=_a+1.0
                if (x in title) and (y in title):
                    _ab=_ab+1.0
            if _a!=0 and _ab!=0:
                #print _a
                #print _ab
                P=_ab/_a
                topic=(P,x+y)
                print 'topic:%s P:%f'%(x+y,P)
                #topics.append(topic)
                #print topics
PA(A, B)

'''

'''
print('-'*40)
print(' word freq')
print('-'*40)
c = Counter(seg_list)
    
freq=OrderedDict(sorted(c.items(),key=lambda t: t[1],reverse=True))
for x, w in freq.items():
    print('%s %s' % (x.encode('gb18030'), w))
'''
