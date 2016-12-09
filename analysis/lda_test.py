# -*- coding: utf-8 -*-
from gensim import corpora, models
import time
import pymongo
from pymongo import MongoClient
import jieba
import jieba.analyse
import json
import re
from collections import OrderedDict
import TopicUnit
import copy
import numpy

#---set db select date---#
global_start_date='2016-9-1'
global_end_date='2016-10-1'

# --load dict--#
print'loading dict......'
jieba.load_userdict('./dict/dict.txt.big')
print'loading hkexDict......'
jieba.load_userdict('./dict/hkexDict_update.txt')
print'loading oralDict......'
jieba.load_userdict('./dict/oralDict.txt')
print'loading SDAC......'
jieba.load_userdict('./dict/SDAC segmentation.txt')
print'loading userDict......'
jieba.load_userdict('./dict/userDict.txt')
# --set stop words--#
stopList = []
#-- set removed number dict--#
removed_num={}
with open('./dict/oralDict.txt') as f1, open('./dict/stop_words_ch.txt')as f2, open('./dict/stop_words_custom.txt')as f3, open('./dict/stop_words_eng.txt')as f4:
    for word in f1.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f2.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f3.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f4.readlines():
        stopList.append(word.strip().decode('utf-8'))

# --set synonym dict--#
with open('./dict/hkexSynonym_update.txt') as f:
    data_list = f.readlines()
    synonymDict = {}
    for line in data_list:
        synonymList = line.strip().split(',')
        key = synonymList[0].decode('utf-8')
        value = synonymList[1].decode('utf-8')
        synonymDict[key] = value
def datetime_timestamp(dt):
    #dt is string
    date=time.strptime(dt, '%Y-%m-%d')
    s = time.mktime(date)
    return int(s)
    
def strQ2B(ustring):  
    rstring = ''
    for uchar in ustring:  
        inside_code = ord(uchar)  
        if inside_code == 12288:   
            inside_code = 32   
        elif (inside_code >= 65281 and inside_code <= 65374):
            inside_code -= 65248  
  
        rstring += unichr(inside_code)  
    return rstring
    
def Regex(sen):
    #sen=re.sub(r'\.{2,}','',sen)
    
    while 1:
        mm = re.search(u'([\u4e00-\u9fa5] [\u4e00-\u9fa5])', sen)
        if mm:
            mm = mm.group()
            sen = sen.replace(mm, mm.replace(" ", ""))
        else:
            break
    sen=re.sub(ur'(\.{2,})|(\d+\-\d+\-\d+)|(\d+\:\d+(am|pm)?)|(\$?\d+\.?\d+[\u6708\u5e74\u65e5\u868a])|(\$\d+\.?\d+)|(\$?\d+\.\d+)','',sen)
    return sen
    
# --delete stop words and replace synonym--#
def cleanWords(seg_list):
    c_seg = []
    for word in seg_list:
        if len(word.strip())>1:
            seg = word.strip()

            if seg not in stopList:  # check stop words
                if synonymDict.has_key(seg):  # check synonym
                    seg = synonymDict[seg]
                if re.search(r'\d+',seg):    #record the number of removed
                    if removed_num.has_key(seg):
                        removed_num[seg]+=1
                    else:
                        removed_num[seg]=1
                    seg=''
                if seg.strip():
                    c_seg.append(seg)
    return  c_seg


def doText(text):
    #text is a string 
    text=strQ2B(text)
    text=Regex(text)
    words = jieba.cut(text,cut_all=False)  #segmentation method use by jieba
    #words_position=jieba.tokenize(text)  #return words with position ("word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2]))
    #words=[tk[0] for tk in words_position]
    clean_word=cleanWords(words)
    clean_word=list(clean_word)    
    return clean_word   #clean_word is a cut list segmentation 

    
def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs
    

def getDB():
    post=conDB('youngspiration')
    start_date = datetime_timestamp(global_start_date)
    end_date = datetime_timestamp(global_end_date)
    date_query={'$gte':start_date, '$lt':end_date}
    query={'created_time':date_query}
    objs=post.find({}).sort([('created_time',1)])
    #find post_create_date and group comments.create_time
    
    #objs=post.find({},{'_id':0}).limit(50)
    return objs
    
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
    #print list(corpus_tfidf)
    lsi = models.hdpmodel.HdpModel(corpus=corpus_tfidf, id2word=word_dict)  
    
    topics=lsi.show_topics(num_topics=-1, num_words=10)
    print lsi.optimal_ordering()
    print len(topics)
    for topic in topics:
        print topic[1]
    #corpus_lsi = lsi[corpus_tfidf]


    
if __name__=='__main__':
    docs=[
    '內地貿易數據遠遜預期 恆指跌幅擴大',
    '首三季度中國與一帶一路國家進出口超4.5萬億人幣',
    '商務部：重視菲總統訪華 冀加強中菲經貿',
    '匯率變化對中國進出口具體影響有限',
    '習近平離京對柬埔寨、孟加拉進行國事訪問並出席金磚國家領導人會晤'
    ]
    numpy.random.seed(1)
    objs=getDB()
    lda_documents=[]
    for obj in objs:

        post_message_seg=obj['message_seg']  # mark use cuted
        lda_documents.append(post_message_seg)
        '''
    segs=[]
    for temp in docs:
        seg=doText(temp.decode('utf-8'))
        segs.append(seg)
    '''
    LDA(lda_documents)
    print 'end'
    
    