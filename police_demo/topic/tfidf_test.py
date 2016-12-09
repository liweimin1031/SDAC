from gensim import corpora, models
import time
from pymongo import MongoClient

def saveTFIDF(filename,data,word_dict,doc_text):
    tfidf_result= list(data)
    with open(filename,'w+')as f1:
        for i, tfidf_result_temp in enumerate(tfidf_result):
            word_tfidf=''
            for word_list in tfidf_result_temp:
                word=word_dict[word_list[0]]
                value=word_list[1]
                word_tfidf+=(word+':'+str(value)+' ')
            line=doc_text[i]+'\n'+word_tfidf+'\n'*2
            f1.write(line.encode('utf-8')+'\n')

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs
    
def getDB(collection,query):
    post=conDB(collection)
    objs=post.find(query,{'title':1,'title_seg':1})
    return objs
    
def datetime_timestamp(dt):
    #dt is string
    date=time.strptime(dt, '%Y-%m-%d')
    s = time.mktime(date)
    return int(s)
    
def getTopic(collection):
    start='2016-10-1'
    end='2016-10-31'
    start_date=datetime_timestamp(start)
    end_date=datetime_timestamp(end)+24*60*60   
    query={'created_time':{'$gte':start_date, '$lt':end_date}}
    
    #get total seg for base dict
    total_docs=getDB(collection,{})
    base=[]
    j=0
    for docs in total_docs:
        base.append(docs['title_seg'])
        j+=1
    #get target seg 
    objs=getDB(collection, query)
    words_list=[]
    doc_text=[]
    i=0
    for obj in objs:
        i+=1
        words_list.append(obj['title_seg'])
        doc_text.append(obj['title'])
    print 'total doc: %d, select doc: %d' %(j,i)

    word_dict = corpora.Dictionary(base)
    #filter low fq words
    #word_dict.filter_extremes(no_below=10,keep_n=1000) 
    #word_dict.compactify() 
    
    #base_corpus_list = [word_dict.doc2bow(texts) for texts in base]
    target_corpus_list = [word_dict.doc2bow(texts) for texts in words_list]
    
    base_tfidf = models.TfidfModel(dictionary=word_dict)
    target_tfidf = models.TfidfModel(corpus=target_corpus_list)
    #tfidf = models.TfidfModel(corpus=corpus_list,dictionary=word_dict)
    target_corpus_tfidf = base_tfidf[target_corpus_list]
    
    
    only_corpus_tfidf=target_tfidf[target_corpus_list]
    #corpus_tfidf = tfidf[corpus_list]
    
    #---save word tfidf --#
    saveTFIDF('total_tfidf.txt',target_corpus_tfidf,word_dict,doc_text)
    saveTFIDF('only_tfidf.txt',only_corpus_tfidf,word_dict,doc_text)
    
    

            
            
if __name__=='__main__':
    collection='discuss_news3'
    getTopic(collection)
    
    
    



    
