import time
start_time=time.time()
from gensim import corpora, models
from pymongo import MongoClient

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs

def getFullCorpus():
    domain_db=conDB(collection)
    domain_corpus=domain_db.find({},{'title_seg':1})
    base=[]
    domain_corpus=list(domain_corpus)

    base=[doc['title_seg'] for doc in domain_corpus]
    
    corpus_db=conDB('corpus')
    normal_corpus=corpus_db.find({},{'seg_text':1})
    normal_corpus=list(normal_corpus)
    base=base+[doc['seg_text'] for doc in normal_corpus]
    return base

# --LDA model--#
def getTopic(data):
    print 'topic'
    docs_id=data['ids']
    words_list=data['docs']
    #input words_list is documents [ [ ] ,[ ], [ ]..... ]

    start_time=time.time()
    lda_data={}
    word_dict = corpora.Dictionary(words_list)
    #filter low fq words
    word_dict.filter_extremes(no_below=10) 
    word_dict.compactify() 
    
    corpus_list = [word_dict.doc2bow(texts) for texts in words_list]  
    tfidf = models.TfidfModel(corpus=corpus_list)
    
    corpus_tfidf = tfidf[corpus_list]
    

    lda = models.ldamodel.LdaModel(corpus=corpus_list, id2word=word_dict, num_topics=5, alpha='auto',iterations=500)  
    patterns = lda.show_topics(num_topics=-1, num_words=10,formatted=False)

    '''
    [
    ( 0 , [("category", -0.340), ("$M$", 0.298), ("algebra", 0.183), ("functor", -0.174), ("operator", -0.168)],..)
    (1, [ ] )
    ...
    ]
    '''
    docs_rate= list(lda[corpus_tfidf]) #[ [topic1_rate,topic2_rate,..... ], [ ],.....   ] 
    #[[(0, 0.87957941149628527), (1, 0.012899218298363135), (2, 0.013875322327932914),...],[(0,0.22474428),...], [ ],....]
    

    #--get keywords list all words--#
    keywords = []
    topic_result=[]
    for pattern in patterns:
        topic_word=[]
        #doc_ids=[]
        for word_value in pattern[1]:
            word = word_value[0]
            value=word_value[1]
            topic_word.append({'word':word,'value':value})
        
        topic_result.append({'topic_words':topic_word, 'doc_ids': [ ] })
        
    for i,rates in enumerate(docs_rate):
        rates.sort(key=lambda x:x[1],reverse=True)
        topic_index=int(rates[0][0])
        topic_value=float(rates[0][1])
        str_id=str(docs_id[i])
        topic_result[topic_index]['doc_ids'].append({'id':str_id,'value':topic_value})
        
    for term in topic_result:
        term['doc_ids'].sort(key=lambda x:x['value'], reverse=True)
    
    end_time=time.time()
    cost_time=end_time-start_time
    print 'LDA cost %d s'%cost_time
    return topic_result
    #topic_result format: [ topic1 , topic2, ...]
    '''
    ex:
    'topic1':{'topic_word':[{'word':string, 'value':int},  {'word':string, 'value':int},....   ],
                 'doc_ids':[{'id': string, 'value' :float }, {'id': string, 'value' :float },... ]}
    '''
    