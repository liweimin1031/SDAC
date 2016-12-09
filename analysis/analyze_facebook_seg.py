# -*- coding: utf-8 -*-
import time
import pymongo
from pymongo import MongoClient
import jieba
import jieba.analyse
import jieba.posseg as pseg
import json
import re
from collections import OrderedDict
import TopicUnit
import copy
import codecs
import string
from string import ascii_letters, digits, Formatter

num_topics=10



#---set db select date---#
global_start_date='2016-9-1'
global_end_date='2016-10-1'
# 金融財經投資區
# 香港及世界新聞討論
# 飲飲食食

def datetime_timestamp(dt):
    #dt is string
    date=time.strptime(dt, '%Y-%m-%d')
    s = time.mktime(date)
    return int(s)


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
    
    objs=post.find(query).sort([('created_time',1)])
    #find post_create_date and group comments.create_time
    
    #objs=post.find({},{'_id':0}).limit(50)
    return objs

def dataPrepare():
    '''
    documents is an 2array  [ [ ],[ ],[ ]....]
    '''
    num=1
    lda_id=[]
    lda_documents=[]
    textrank_sentences_week=[]   
    textrank_sentences= ''
    objs=getDB()
    
    start_date=1472659200 #2016-9-1
    one_week=7*24*60*60
    end_date=start_date+one_week
    date_array=[{'start_date':start_date,'end_date':end_date}]
    n=0
    for obj in objs:
        post_message_seg=obj['message_seg']  # mark use cuted
        if post_message_seg:
            n+=1
            lda_documents.append(post_message_seg)        
            lda_id.append(obj['_id'])

    print n
    print 'lda'
    #---lda ---#
    lda_data=TopicUnit.LDA(lda_documents,num_topics)
    
    docs_rate=lda_data['docs_rate']
    keywords=lda_data['keywords']
    
    overlapRatio(keywords)
    #create lda topic result db
    result_con=conDB('youngspiration_result')
    
    lda_topic=[]
    for keyword in keywords:
        topic_words=[]
        for word in keyword:
            topic_words.append({'word':word,'weight':keyword[word]})
        lda_topic.append({ 'topic_words':topic_words,'doc_ids':[] })
    _lda_topic=[]
    for x in range(num_topics):
        _lda_topic.append([])
    for i,rates in enumerate(docs_rate):
        rates.sort(key=lambda x:x[1],reverse=True)
        topic_index=int(rates[0][0])
        topic_value=float(rates[0][1])
        str_lda_id=str(lda_id[i])
        _lda_topic[topic_index].append((str_lda_id,topic_value))
    for j,temp in enumerate(_lda_topic):
        temp.sort(key=lambda x:x[1],reverse=True)
        for id_value in temp:
            lda_topic[j]['doc_ids'].append(id_value[0])
    
    #result_con.update({},{'$set':{'lda':lda_topic} } )
    #result_con.remove({})
    result_con.insert({
            #'week':week_data,
            'period': 'oct',
            'lda':lda_topic
    })

def overlapRatio(keywords_list):
    # keywords_list: [ [ w11,w12,...], [w21,w22,.... ], .... ]
    word=[]
    for i , keywords_tuple in enumerate(keywords_list):
        for word_weight in keywords_tuple:
            word.append(word_weight[0])
    union_len=len(set(word))
    ratio=1-union_len/(num_topics*5.000)
    print ratio

    
    
if __name__=='__main__':
    
    #by month
    dataPrepare()
    print 'end'





