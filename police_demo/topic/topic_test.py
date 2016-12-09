import lda
import time
from pymongo import MongoClient

result_db='discuss_result'

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs
    
def getDB(collection,query):
    post=conDB(collection)
    objs=post.find(query)
    return objs
    
def datetime_timestamp(dt):
    #dt is string
    date=time.strptime(dt, '%Y-%m-%d')
    s = time.mktime(date)
    return int(s)
    
def getTopic(start, end, collection):

    start_date=datetime_timestamp(start)
    end_date=datetime_timestamp(end)+24*60*60
    
    query={'created_time':{'$gte':start_date, '$lt':end_date}}
    objs=getDB(collection, query)
    lda_documents=[]
    lda_ids=[]
    tfidf_obj=[]
    original_doc=[]
    for obj in objs:
        lda_documents.append(obj['title_seg'])
        lda_ids.append(obj['_id'])
        original_doc.append(obj['title'])
    lda_data={'docs':lda_documents , 'ids':lda_ids,'original_doc':original_doc}
    topic_result=lda.LDA(lda_data,num_topics=5)

    '''
    with open('tfidf.txt','w+')as f1:
        for i, tfidf_obj_temp in enumerate(tfidf_obj):
            tfidf_doc=tfidf_result[i]
            word_tfidf=''
            len_seg=len(tfidf_obj_temp['title_seg'])
            len_tfidf=len(tfidf_doc)

            if len_seg!=len_tfidf:
                print i
                print tfidf_obj_temp['title_seg']
                print tfidf_doc
            for j, temp in enumerate(tfidf_obj_temp['title_seg']):
                word_tfidf+=(temp+':'+str(tfidf_doc[j][1])+'\t')
            line=tfidf_obj_temp['title']+'\n'+word_tfidf+'\n'+'\n'
            f1.write(line.encode('utf-8'))
        
    '''
    result=conDB(result_db)
    #result.delete_many({})
    id = result.insert({'topic':topic_result})
    print id

if __name__=='__main__':
    from sys import argv
    script, start, end, collection=argv
    #collection='discuss_news3'
    #start='2016-9-1'
    #end='2016-9-30'
    getTopic( start, end, collection)
