# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo
from pymongo import MongoClient
import jieba
import re

# --load dict--#
print'loading dict......'
jieba.load_userdict('../dict/dict.txt.big')
print'loading hkexDict......'
jieba.load_userdict('../dict/hkexDict_update.txt')
print'loading oralDict......'
jieba.load_userdict('../dict/oralDict.txt')
print'loading userDict......'
jieba.load_userdict('../dict/userDict.txt')
# --set stop words--#
stopList = []
with open('../dict/oralDict.txt') as f1, open('../dict/stop_words_ch.txt')as f2, open('../dict/stop_words_custom.txt')as f3, open('../dict/stop_words_eng.txt')as f4:
    for word in f1.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f2.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f3.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f4.readlines():
        stopList.append(word.strip().decode('utf-8'))

# --set synonym dict--#
with open('../dict/hkexSynonym_update.txt') as f:
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
    
def reReplace(sen):
    sen=re.sub(r'\.{2,}','',sen)
    while 1:
        mm = re.search("\d,\d", sen)
        if mm:
            mm = mm.group()
            sen = sen.replace(mm, mm.replace(",", ""))
        else:
            break
    return sen
    
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




def doText(text):
    #text is a string 
    text=strQ2B(text)
    text=reReplace(text)
    words = jieba.cut(text,cut_all=False)  #segmentation method use by jieba
    clean_word=cleanWords(words)
    clean_word=list(clean_word)    
    return clean_word   #clean_word is a cut list segmentation 

def getDB():
    client = MongoClient('localhost', 27017)
    db = client['financial']
    post=db['post']
    start_date = '2016-7-1'
    end_date = '2016-8-1'
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    objs=post.find({'post_create_date':{'$gte':start_date, '$lte':end_date}},{'_id':0}).sort([('post_create_date',1)])
    #objs=post.find({},{'_id':0}).limit(50)
    return objs

def dataPrepare():
    '''
    documents is an 2array  [ [ ],[ ],[ ]....]
    
    '''
    num=1
    documents=[]
    objs=getDB()
    for obj in objs:
        document=[]
        title=obj['title']
        title=doText(title)
        content=''.join(obj['content']['text'])
        content=doText(content)
        document.extend(title)
        document.extend(content)
        comments=obj['comments']
        for comment in comments:
            comment=''.join([text_list.strip() for text_list in comment['content']['text']])
            comment=doText(comment)
            document.extend(comment)
        documents.append(document)
        print num  
        num+=1
    return documents
    


