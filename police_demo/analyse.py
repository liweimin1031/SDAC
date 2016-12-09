import time
from pymongo import MongoClient
import sys
sys.path.append('./topic')
sys.path.append('./linkage')
import linkage
import topic
from compiler.ast import flatten


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
    objs=post.find(query,{'title_seg':1,'graphs':1})
    return objs
    
def datetime_timestamp(dt):
    #dt is string
    date=time.strptime(dt, '%Y-%m-%d')
    s = time.mktime(date)
    return int(s)

def getFullCorpus(domain_collection):
    #domain_db=conDB(domain_collection)
    #domain_corpus=domain_db.find({},{'title_seg':1})
    full_corpus=[]
    #domain_corpus=list(domain_corpus)

    #full_corpus=[doc['title_seg'] for doc in domain_corpus]
    
    corpus_db=conDB('corpus')
    normal_corpus=corpus_db.find({},{'seg_text':1})
    normal_corpus=list(normal_corpus)
    full_corpus=[doc['seg_text'] for doc in normal_corpus]
    return full_corpus       
 
def getResult(start, end, collection):

    start_date=datetime_timestamp(start)
    end_date=datetime_timestamp(end)+24*60*60
    
    query={'created_time':{'$gte':start_date, '$lt':end_date}}
    objs=getDB(collection, query)

    lda_documents=[]
    lda_ids=[]
    original_doc=[]
    
    localEdges=[]
    links=[]

    objs=list(objs)

    lda_documents=[obj['title_seg'] for obj in objs]
    lda_ids=[obj['_id'] for obj in objs]
    dict_corpus=getFullCorpus(collection)
    dict_corpus+=lda_documents
    #original_doc.append(obj['title'])

    graphs=flatten([obj['graphs'] for obj in objs])  

    localEdges=[(graph['src'],graph['dst']) for graph in graphs ]

    '''
    for obj in objs:
        lda_documents.append(obj['title_seg'])
        lda_ids.append(obj['_id'])
        original_doc.append(obj['title'])
        graphs=obj['graphs']

        for graph in graphs:
            localEdge=(graph['src'],graph['dst'])
            localEdges.append(localEdge)
            links.append({ 'source':graph['src'] ,'target': graph['dst'] })
        
        '''
    topic_data={'docs':lda_documents , 'ids':lda_ids,'dict_corpus':dict_corpus}
    linkage_data={'localEdges':localEdges}

    topic_result=topic.getTopic(topic_data)
    linkage_result=linkage.getLinkage(linkage_data)
    
    result=conDB(result_db)
    id = result.insert({'topic':topic_result,'linkage':linkage_result})
    print id

if __name__=='__main__':
    from sys import argv
    script, start, end, collection=argv
    #collection='discuss_news3'
    #start='2016-9-1'
    #end='2016-9-30'
    getResult( start, end, collection)
