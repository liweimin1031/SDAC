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
global_start_date='2016-7-1'
global_end_date='2016-8-1'

        
#---textrank---#
def textrank(sentence):
    #input sentence is string
    print('-' * 40)
    print(' textrank ')
    print('-' * 40)
    keywords=[]
    for x, w in jieba.analyse.textrank(sentence, topK=5,withWeight=True):
        word_weight=dict()
        print('%s %s' % (x, w))
        word_weight[x]=w
        keywords.append(word_weight)
    #keywords format [{'word1':'weight1'},{'word2':'weight2'}...]
    return keywords

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
    sen=re.sub(r'\.{2,}','',sen)
    while 1:
        mm = re.search(u'([\u4e00-\u9fa5] [\u4e00-\u9fa5])', sen)
        if mm:
            mm = mm.group()
            sen = sen.replace(mm, mm.replace(" ", ""))
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
    query={'post_create_date':date_query,'category':'½ðÈÚØ”½›Í¶ÙY…^'}
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
        
        document=[]
        title=doText(obj['title'])
        content=doText(obj['content'])

        document.extend(title)
        #document.extend(content)
        comments=obj['posts']
        for i,comment in enumerate( comments):
            comment=doText(comment['text'])
            comments[i]['seg']=comment
            # comments add new key seg. seg is a cut list
            
            document.extend(comment)
        #update db, add segmentation result

        post.update({'_id':obj['_id']},{'$set':{'title_seg':title,'content_seg':content,'posts':comments}})
        lda_documents.append(document)
        #textrank_sentences.append(''.join(document))
        print num  
        num+=1
        
    #---lda ---#
    lda_keywords=TopicUnit.LDA(lda_documents)
    '''    
    #---textrank---#
    jieba.analyse.set_stop_words('./dict/oralDict.txt')
    jieba.analyse.set_stop_words('./dict/stop_words_ch.txt')
    jieba.analyse.set_stop_words('./dict/stop_words_custom.txt')
    jieba.analyse.set_stop_words('./dict/stop_words_eng.txt')
    sentence=''.join(textrank_sentences)
    textrank_keywords=textrank(sentence)
    '''
    return lda_keywords
    
def selectDB(keywords):
    # keywords must be unicode list
    post=conDB('discusshk')
    result_list = []

    start_date = global_start_date
    end_date = global_end_date
    
    start_date = datetime_timestamp(start_date)
    end_date = datetime_timestamp(end_date)
    select_date = {'$gte':start_date, '$lt':end_date}
    
    result_list=post.aggregate([
                                    {'$project':{'post_create_date':1,'posts.create_time':1, 'posts.text':1, 'posts.seg':1, '_id':0}},
                                    {'$unwind':'$posts'},
                                    {'$match':{'post_create_date':select_date,'posts.create_time':select_date,'posts.seg':{'$in':keywords}}},
                                    {'$group': {'_id': '$posts.create_time', 'content': {'$push': {'text':'$posts.text','seg':'$posts.seg'}}}},
                                    {'$sort':{'_id':1}}])
    '''                                
    project={'post_create_date':1,'title_seg':1, 'comments.create_time':1,'comments.content.text':1, '_id':0}
    result_list=post.aggregate([
    result_list=post.aggregate([
                                    {'$project':project},
                                    {'$unwind':'$comments'},
                                    {'$match': {'post_create_date':select_date,'title_seg':{'$in':keywords}
                                                    }
                                                    {'comments.create_time':select_date,'comments.content.text':{'$in':keywords}}
                                    },
                                    {'$group': {'_id': '$comments.create_time', 'content': {'$push': '$comments.content.text'}}},
                                    {'$sort':{'_id':1}}])
    '''
    return result_list

#LDA doc topic rate
def docTopicRate(seg,word_weight):
    word_weight
    words=[]
    rate=0
    for word in seg:
        if word_weight.has_key(word):
            weight=float(word_weight[word])
            rate+=weight
            words.append(word)
    return words, rate
    
#set date format as 2016-7-1
def dateFormat(date):
    temp=date.split('-')
    return temp[0] + '-' + str(int(temp[1])) + '-' + str(int(temp[2]));  

def dataFormat(word_weight_list):
    #topic_words=[temp.keys() for temp in word_weight]  
    #input topic_words format:  [ [k11,k12,...] , [k21,k22,...], [k31,k32,...] .....  ]
    #compare data to web json format
    topic_list=[]

    for word_weight in word_weight_list:
        
        keywords=word_weight.keys()
        db_result_list = selectDB(keywords) #get data from db
        
        topic_json={}

        _topic = ','.join([keyword.encode('utf-8') for keyword in keywords])
        #f.write('topic %s \n' % (topic))
        data_list=[]
        temp_data=OrderedDict()
        for result in db_result_list:
            #one date obj
            contents = result['content']
            texts=[]
            for content in contents:  #get one content
                seg=content['seg']
                words,rate=docTopicRate(seg,word_weight)
                text=content['text']
                seg_text='['+' '.join(seg)+']' #add seg list for ref
                tag='('+','.join(words)+':'+str(rate)+')'  #add keywords and weight 
                text=(text+'<br>'+seg_text+'<br>'+'<B>'+tag+'</B>').encode('utf-8')
                texts.append(text)
            post_create_date=time.strftime('%Y-%m-%d', time.localtime(result['_id']))
            post_create_date=dateFormat(post_create_date)
            
            if temp_data.has_key(post_create_date):
                #update temp_data
                temp_data[post_create_date]['content']=temp_data[post_create_date]['content']+texts
            else:
                temp_data[post_create_date]={'content':texts}

        #set temp_data to data_list
        for k,v in temp_data.items():
            _data={}
            _data['date']=k
            _data['content']=v['content']
            #_data['reply']=v['reply']

            data_list.append(_data)
        #set topic data compare with data format
        topic_json['topic'] = _topic
        topic_json['data']=data_list
        #print topic_json
        #save topic_json
        topic_list.append(topic_json)
    return topic_list

    
if __name__=='__main__':
    
    #by month
    lda_keywords=dataPrepare()
    with open('../web/view/lda_financial_july.json', 'w')as f1:
    #with open('../web/view/lda_dbData_month_weight.json', 'w')as f1, open('../web/view/textrank_dbData_month_weight.json', 'w')as f2:
        lda_json=dataFormat(lda_keywords)
        f1.write(json.dumps(lda_json))
        '''
        textrank_json=dataFormat(textrank_keywords)
        f2.write(json.dumps(textrank_json))
        '''
    '''
    # by week
    date_week=[('2016-7-4','2016-7-11'),('2016-7-11','2016-7-18'),('2016-7-18','2016-7-25'),('2016-7-25','2016-8-1')]
    web_path='../web/view/data/'
    for i,week in enumerate(date_week,1):
        global_start_date=week[0]
        global_end_date=week[1]
        lda_file_name='lda_dbData_week_weight'+str(i)+'.json'
        textrank_file_name='textrank_dbData_week_weight'+str(i)+'.json'
        lda_open_file=web_path+lda_file_name
        textrank_open_file=web_path+textrank_file_name
        lda_keywords,textrank_keywords=dataPrepare()
        with open(lda_open_file, 'w')as f1, open(textrank_open_file, 'w')as f2:
            lda_json=dataFormat(lda_keywords)
            f1.write(json.dumps(lda_json))
            textrank_json=dataFormat(textrank_keywords)
            f2.write(json.dumps(textrank_json))
    '''




