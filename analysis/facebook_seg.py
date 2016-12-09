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
# --load dict--#
print'loading dict......'
jieba.load_userdict('./dict/dict.txt.big')
print'loading oralDict......'
jieba.load_userdict('./dict/oralDict.txt')
print'loading swear word Dict......'
jieba.load_userdict('./dict/swear_word.txt')
print'loading political Dict......'
jieba.load_userdict('./dict/political.txt')
print'loading political name Dict......'
jieba.load_userdict('./dict/political_name.txt')

print'loading location Dict......'
locations = [line.rstrip('\n\r') for line in codecs.open('./dict/location.txt', encoding='utf-8')]
for item in locations:
    jieba.add_word(item, 40, tag='ns')
# --set topic number--#
num_topics=150
# --set stop words--#
stopList = []
#-- set removed number dict--#
removed_num={}
with open('./dict/oralDict.txt') as f1, open('./dict/stop_words_ch.txt')as f2, open('./dict/stop_words_eng.txt')as f3,\
    open('./dict/punctuation.txt') as f4, open('./dict/swear_word.txt')as f5:
    for word in f1.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f2.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f3.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f4.readlines():
        stopList.append(word.strip().decode('utf-8'))
    for word in f5.readlines():
        stopList.append(word.strip().decode('utf-8'))
stopList=list(set(stopList))        



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

# --delete stop words and replace synonym--#
def cleanWords(seg_list):
    c_seg = []
    
    remain_flags = ['n', 'v', 'ns']

    for word, flag in seg_list:
        word = word.strip()
        if len(word)>1:
            if not(is_punctuation(word)) and (flag.startswith('n') or flag.startswith('v')) and (word not in stopList): # check stop words
                c_seg.append(word)
    return  c_seg

def is_punctuation(word):
    if word == '...':
        return True
    chinesePunctuation = '《》「」。、.!?:;~。！？～；：【】[]()（）-﹏_——﹃﹄﹁﹂，/／“'.decode('utf8')
    return (word in string.punctuation) or (word in chinesePunctuation)

def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            return True
    else:
            return False
        
def strQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:                             
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): 
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring

def isAscii(s):
    for c in s:
        if c not in string.ascii_letters:
            return False
    return True

def clean_text(text):
    
    text = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
    text = re.sub('\s+', ' ', text.strip())
    text = re.sub('\.{2,}', '...', text)
    #text = re.sub('~{2,}', '', text)
    text = re.sub('\*+', '', text)
    text = re.sub('\++', '', text)
    text = strQ2B(text)
    
    text = "".join([ch for ch in text if (ch == ' ' or ch in (ascii_letters + digits) or is_chinese(ch) or is_punctuation(ch))])
    string = ''
    length = len(text)
    i = 0
    while i < length:
        if text[i] != ' ':
            string = string + text[i]
            i = i + 1
        else:
            if i == 0:
                i = i + 1
            elif text[i - 1] in ascii_letters and (i + 1) < length and  text[i + 1] in ascii_letters:
                string = string + text[i]
                i = i + 1
            else:
                i = i + 1
    # string = Segmentation.strQ2B(string)
    return string

def doText(text):
    #text is a string 
    text = clean_text(text)
    
    #words = jieba.cut(text,cut_all=False)  #segmentation method use by jieba
    
    words = pseg.cut(text)  #segmentation method use by jieba
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
    query={'post_create_date':date_query,'category':'金融財經投資區'}
    
    objs=post.find({}).sort([('created_time',1)])
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
    for obj in objs:
        
        post=conDB('youngspiration')
        
        document=[] #doc_seg
        comments=obj['comments']  #comments
        #post_message_seg=doText(obj['message'])  #mark new cut
        post_message_seg=obj['message_seg']  # mark use cuted
        if post_message_seg:
            lda_documents.append(post_message_seg)
        
            lda_id.append(obj['_id'])
        '''
        for comment in comments:
            comment_seg=doText(comment['message'])
            comment['seg']=comment_seg
            # comments add new key seg. seg is a cut list
            #document.extend(comment_seg)  #mark add comment
            
            if comment.has_key('comments'):
                re_comments=comment['comments']
                for re_comment in re_comments:
                    re_comment_seg=doText(re_comment['message'])
                    re_comment['seg']=re_comment_seg
                    #document.extend(re_comment_seg)  #mark add re_comment
        #update db, add segmentation result

        post.update({'_id':obj['_id']},{'$set':{'doc_seg':document,'message_seg':post_message_seg,'comments':comments}})
        '''
        #print document

        '''
        #--textrank data--#
        #textrank_sentences += ' '.join(document)
        if obj['created_time']<end_date:
            textrank_sentences += ' '.join(document)
        else:
            textrank_sentences_week.append(textrank_sentences)
            date_array.append({'start_date':end_date,'end_date':end_date+one_week})
            end_date+=one_week
            textrank_sentences=''
         ''' 
 
        #print num  
        #num+=1
    '''    
    #--textrank--#
    print 'textrank'
    result_con=conDB('youngspiration_result')
    print len(textrank_sentences_week)
    week_data=[]
    for i,textrank_sentences in enumerate(textrank_sentences_week):
        #print 'textrank'
        result= jieba.analyse.textrank(textrank_sentences,withWeight=True)
        textrank=[]
        for word, weight in result: 
            #print '%s:%s'%(word,weight)
            textrank.append({'word':word,'weight':weight})
            
        #print 'extract tags'
        result = jieba.analyse.extract_tags(textrank_sentences,withWeight=True)
        extract_tags=[]
        for word, weight in result: 
            #print '%s:%s'%(word,weight)
            extract_tags.append({'word':word,'weight':weight})

        week_data.append({'textrank':textrank,'extract_tags':extract_tags,'start_date':date_array[i]['start_date'],'end_date':date_array[i]['end_date']})
    '''        


    print 'lda'
    #---lda ---#
    lda_data=TopicUnit.LDA(lda_documents,num_topics)
    
    docs_rate=lda_data['docs_rate']
    keywords=lda_data['keywords']
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
    result_con.remove({})
    result_con.insert({
            #'week':week_data, 
            'lda':lda_topic
    })

def topicNum(keywords_list):
    # keywords_list: [ [ w11,w12,...], [w21,w22,.... ], .... ]
    
    for i , keywords in enumerate(keywords_list):
        for j in range(i,num_topics):
            temp=keywords +keywords_list[j]
            union_len=len(set(temp))
            if union_len<8:
                #these two topics are too similar
                break
    
    
if __name__=='__main__':
    
    #by month
    dataPrepare()
    print 'end'





