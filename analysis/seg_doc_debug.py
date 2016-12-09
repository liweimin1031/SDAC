# -*- coding: utf-8 -*-
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

#---set db select date---#
global_start_date='2016-8-1'
global_end_date='2016-9-1'
# 金融財經投資區
# 香港及世界新聞討論
# 飲飲食食

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
    post=conDB('discuss')

    start_date = datetime_timestamp(global_start_date)
    end_date = datetime_timestamp(global_end_date)
    date_query={'$gte':start_date, '$lt':end_date}
    query={'post_create_date':date_query,'category':'金融財經投資區'}
    objs=post.find(query).sort([('post_create_date',1)])
    #find post_create_date and group comments.create_time
    
    #objs=post.find({},{'_id':0}).limit(50)
    return objs

def dataPrepare():
    '''
    documents is an 2array  [ [ ],[ ],[ ]....]
    '''
    num=1
    lda_documents=[]
    textrank_sentences=[]
    objs=getDB()
    for obj in objs:
        post=conDB('discuss')
        
        document=[] #doc_seg
        doc=obj['title']  #doc
        title=doText(obj['title'])
        content=doText(obj['content'])

        document.extend(title)
        #document.extend(content)
        comments=obj['posts']
        for i,comment in enumerate( comments):
            doc=doc+'<br>'+comment['text']
            comment=doText(comment['text'])
            comments[i]['seg']=comment
            # comments add new key seg. seg is a cut list
            
            document.extend(comment)
        #update db, add segmentation result

        post.update({'_id':obj['_id']},{'$set':{'doc':doc,'doc_seg':document,'title_seg':title,'content_seg':content,'posts':comments}})
        lda_documents.append(document)
        #textrank_sentences.append(''.join(document))
        print num  
        num+=1
        
    #---lda ---#
    lda_keywords=TopicUnit.LDA(lda_documents)

    return lda_keywords
    

#get doc from db
def selectDoc():
    post=conDB('discuss')
    result_list = []
    start_date = global_start_date
    end_date = global_end_date

    start_date = datetime_timestamp(start_date)
    end_date = datetime_timestamp(end_date)
    date_query = {'$gte':start_date, '$lt':end_date}
    query={'post_create_date':date_query,'category':'金融財經投資區'}
    result_list=post.find(query,{'doc':1,'doc_seg':1,'post_create_date':1,'posts.text':1,'posts.seg':1,'title':1,'title_seg':1}).sort([('post_create_date',1)]) # get doc
    #result_list=post.find(query,{'post_create_date':1,'content':1,'content_seg':1,'title':1,'title_seg':1}).sort([('post_create_date',1)]) # get doc
    return result_list
    
#LDA doc topic rate
    
#set date format as 2016-7-1
def dateFormat(date):
    temp=date.split('-')
    return temp[0] + '-' + str(int(temp[1])) + '-' + str(int(temp[2]));  

def getDocTopic(word_weight_list):
    documents =selectDoc()
    web_obj={}   #{'topic':[],'data':[doc1,doc2,....]}
    
    json_list=[]#[{'topic':{ },data:data_json },.....]
    web_obj['topic']=[]
    web_obj['data']=[]
    #format word_weight_list to topic_rate_list
    topic_rate_list=[]
    for word_weight in word_weight_list:  #loop topic and get doc's topic rate in this topic
        topic_rate=word_weight
        #topic_rate={'word1':{'count':int,'weight':int},......}
        for temp in word_weight:
            topic_rate[temp]={'count':0,'weight':float(word_weight[temp])}
        topic_rate_list.append(topic_rate)
        web_obj['topic'].append(', '.join(word_weight.keys()))

    data_json=OrderedDict()  #{'2016-7-1':{'doc':'xxxxx','topic':'xxxxx'},....}

    for document in documents:
        
        doc={}  #{post_create_date:xxx,content:'' ,topic_rate}
        content=[]
        post_create_date=document['post_create_date']
        post_create_date=time.strftime('%Y-%m-%d', time.localtime(post_create_date))
        post_create_date=dateFormat(post_create_date)
        doc['post_create_date']=post_create_date
        
        _topic_rate=[]
        c_topic_rate_list=copy.deepcopy(topic_rate_list)
        for temp in c_topic_rate_list:  #loop topic and get doc's topic rate in this topic
            doc_seg=document['doc_seg']
            topic_weight=temp

            for seg in doc_seg:
                if topic_weight.has_key(seg):
                    topic_weight[seg]['count']+=1

            _rate=0.0
            for word in topic_weight:
                _rate+=topic_weight[word]['count']*topic_weight[word]['weight']
            _topic_rate.append({'topic':topic_weight,'rate':_rate})

        doc['topic_rate']=_topic_rate
        
        title=document['title']+'\n'+'['+' '.join(document['title_seg'])+']'
        content.append(title)
        posts=document['posts']
        for post in posts:
            content.append(post['text']+'\n'+'['+' '.join(post['seg'])+']')
        doc['content']=content
        web_obj['data'].append(doc)
        #format document for web json

    return web_obj
    
if __name__=='__main__':
    
    #by month
    lda_keywords=dataPrepare()
    with open('../web/view/data/test.json', 'w')as f1, open('../web/view/data/removed_num.json','w')as f2:
        lda_json=getDocTopic(lda_keywords)
        f1.write(json.dumps(lda_json))
        removed_num_sorted=sorted(removed_num.iteritems(),key=lambda t:t[1],reverse=True)
        for temp in removed_num_sorted:
            k=temp[0]
            v=str(temp[1])
            line=k+':'+v+'\n'
            f2.write(line.encode('utf-8'))




