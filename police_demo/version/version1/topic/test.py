import lda
from pymongo import MongoClient


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
    
def getTopic():
    collection_name='discuss_news3'
    query={'created_time':{'$gte':1475251200, '$lt':1477929600}}
    objs=getDB(collection_name, query)
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
    result=conDB('discuss_result')
    result.delete_many({})
    id = result.insert({'topic':topic_result})
    print id

if __name__=='__main__':
    getTopic()
    print 'end'