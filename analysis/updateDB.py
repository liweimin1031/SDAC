# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo
from pymongo import MongoClient
import jieba
import jieba.posseg as pseg
import re

# --load dict--#
print'loading dict......'
jieba.load_userdict('./dict/dict.txt.big')

print'loading hkexDict......'
jieba.load_userdict('./dict/hkexDict_update.txt')
print'loading oralDict......'
jieba.load_userdict('./dict/oralDict.txt')
print'loading userDict......'
jieba.load_userdict('./dict/userDict.txt')
# --set stop words--#
stopList = []
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
    for word in seg_list:
        if word.strip():
            seg = word.strip()
        # print seg
            if seg not in stopList:  # check stop words
                if synonymDict.has_key(seg):  # check synonym
                    seg = synonymDict[seg]       
                c_seg.append(seg)
    return  c_seg
def conDB(collection):
    client = MongoClient('localhost', 27017)
    db = client['financial']
    curs=db[collection]
    return curs

start_date = '2016-7-1'
end_date = '2016-8-2'
start_date = datetime.strptime(start_date, '%Y-%m-%d')
end_date = datetime.strptime(end_date, '%Y-%m-%d')
post=conDB('post')
#objs=post.find({'post_create_date':{'$gte':start_date, '$lte':end_date}},{'_id':0}).sort([('post_create_date',1)])
objs=post.find({},{'_id':0})

def conLAS(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs
num=1
discuss=conLAS('discusshk')
for obj in objs:
    comments=obj['comments']
    for i,comment in enumerate(comments):
        text=''.join([text_list.strip() for text_list in comment['content']['text']])
        text=strQ2B(text)
        obj['comments'][i]['text']=text
        pseg_list = pseg.cut(text)
        word_flag=[]
        words=[]
        for word, flag in pseg_list:
            words.append(word)
            word=word+'/'+flag
            word_flag.append(word)
        word_flag=' '.join(word_flag)
        obj['comments'][i]['word_flag']=word_flag
        clean_word=cleanWords(words)
        clean_word=' '.join([w for w in clean_word])
        obj['comments'][i]['analyse_word']=clean_word
        del obj['comments'][i]['content']
    discuss.insert(obj)
    print num  
    num+=1
     
