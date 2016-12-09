# -*- coding: utf-8 -*-
import time
from pymongo import MongoClient
import jieba
import jieba.analyse
import jieba.posseg as pseg
import json
import re
import string
from string import ascii_letters, digits, Formatter

class segmentation(object):

    def __init__(self):

        # --load general dict--#
        print'loading dict......'
        jieba.load_userdict('./dict/dict.txt.big')
        print'loading oralDict......'
        jieba.load_userdict('./dict/oralDict.txt')
        print'loading swear word Dict......'
        jieba.load_userdict('./dict/swear_word.txt')
        print'loading location Dict......'
        jieba.load_userdict('./dict/location.txt')       
        
        #--load special dict--#
        print'loading political Dict......'
        jieba.load_userdict('./dict/political.txt')
        print'loading politician  Dict......'
        jieba.load_userdict('./dict/politician.txt')

        # --set stop words--#
        self.stopList = []
        with open('./dict/stop_words/stop_words_ch.txt')as f2, open('./dict/stop_words/stop_words_eng.txt')as f3, open('./dict/swear_word.txt')as f5:
            for word in f2.readlines():
                self.stopList.append(word.strip().decode('utf-8'))
            for word in f3.readlines():
                self.stopList.append(word.strip().decode('utf-8'))
            for word in f5.readlines():
                self.stopList.append(word.strip().decode('utf-8'))
        self.stopList=list(set(self.stopList))        
    

    def is_punctuation(self, word):
        if word == '...':
            return True
        chinesePunctuation = '《》「」。、.!?:;~。！？～；：【】[]()（）-﹏_——﹃﹄﹁﹂，/／“'.decode('utf8')
        return (word in string.punctuation) or (word in chinesePunctuation)
    

    def is_chinese(self, uchar):
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                return True
        else:
                return False
                
       
    def strQ2B(self, ustring):
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 12288:                             
                inside_code = 32 
            elif (inside_code >= 65281 and inside_code <= 65374): 
                inside_code -= 65248

            rstring += unichr(inside_code)
        return rstring
        

    def isAscii(self, s):
        for c in s:
            if c not in string.ascii_letters:
                return False
        return True

        # --delete stop words and replace synonym--#
    def cleanWords(self, seg_list):
        c_seg = []
        for word in seg_list:
            word = word.strip()
            if len(word)>1:
                if not(self.is_punctuation(word)) and (word not in self.stopList): # check stop words
                    c_seg.append(word)
        return  c_seg
        
    def prepareText(self,text):
        text = self.strQ2B(text)
        text = text.lower()
        #text = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
        text = re.sub(ur'(\.{2,})|(\d+\-\d+\-\d+)|(\d+\:\d+(am|pm)?)|(\$?\d+\.?\d+[\u6708\u5e74\u65e5\u868a])|(\$\d+\.?\d+)|(\$?\d+\.\d+)','',text)
        text = re.sub('\s+', ' ', text.strip())
        text = re.sub('\.{2,}', '', text)
        #text = re.sub('~{2,}', '', text)
        #text = re.sub('\*+', '', text)
        #text = re.sub('\++', '', text)

        
        #text = "".join([ch for ch in text if (ch == ' ' or ch in (ascii_letters + digits) or self.is_chinese(ch) or self.is_punctuation(ch))])
        '''string = ''
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
        '''
        return text

    def segText(self,text):
        #text is a string 
        text = self.prepareText(text)
        
        words = jieba.cut(text,cut_all=False)  #segmentation method use by jieba
        
        #words = pseg.cut(text)  #segmentation method use by jieba
        #words_position=jieba.tokenize(text)  #return words with position ("word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2]))
        #words=[tk[0] for tk in words_position]
        clean_word=self.cleanWords(words)
        clean_word=list(clean_word)    
        return clean_word   #clean_word is a cut list segmentation 





    
if __name__=='__main__':
        #---set db select date---#
    global_start_date='2016-8-1'
    global_end_date='2016-9-1'


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
    

    def getDB(collection):
        post=conDB(collection)

        start_date = datetime_timestamp(global_start_date)
        end_date = datetime_timestamp(global_end_date)
        date_query={'$gte':start_date, '$lt':end_date}
        query={'created_time':date_query}
        
        objs=post.find(query)#.sort([('created_time',1)])
        #find post_create_date and group comments.create_time
        
        #objs=post.find({},{'_id':0}).limit(50)
        return objs
    
    seg=segmentation()
    
    
    #by month
    collection_name='discuss_news3'
    docs=getDB(collection_name)
    with open('seg.txt','w+') as f1:
        for doc in docs:
            content=doc['title']
            seg_text=seg.segText(content)
            obj=content+'\n'+' , '.join(seg_text)+'\n'+'\n'
            f1.write(obj.encode('utf-8'))
    '''
    content='民陣遊行反對人大釋法 由灣仔修頓球場起步'.decode('utf-8')
    result=seg.segText(content)
    print ','.join(result)
    '''
    print 'end'





