from gensim import corpora, models
import time
from pymongo import MongoClient
from collections import Counter
import matplotlib.pyplot as plt  
def saveTFIDF(filename,data,base_dict,doc_text):
    tfidf_result= list(data)
    with open(filename,'w+')as f1:
        for i, tfidf_result_temp in enumerate(tfidf_result):
            word_tfidf=''
            for word_list in tfidf_result_temp:
                word=base_dict[word_list[0]]
                value=word_list[1]
                word_tfidf+=(word+':'+str(value)+' ')
            line=doc_text[i]+'\n'+word_tfidf+'\n'*2
            f1.write(line.encode('utf-8')+'\n')

def drawDFS(dfs,title):
    term_doc_fre=dfs.values()
    fre_count=dict(Counter(term_doc_fre))
    fre_count=sorted(fre_count.iteritems(), key=lambda d:d[0], reverse = False)
    #print fre_count
    x=[temp[0] for temp in fre_count]
    y=[temp[1] for temp in fre_count]
    plt.xlabel("word frequency")
    plt.ylabel("frequency of word frequency")
    plt.title(title)
    plt.plot(x,y,color="red",linewidth=2)
    plt.xlim((0,100))
    plt.ylim((0,100))
    plt.show()
    return 
            
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
    # total_docs=getDB(collection,{})
    base=[]
    # for docs in total_docs:
        # base.append(docs['title_seg'])
    
    corpus_db=conDB('corpus')
    normal_corpus=corpus_db.find({},{'seg_text':1})
    for doc in normal_corpus:
        base.append(doc['seg_text'])
    
    
    #get target seg 
    objs=getDB(collection, query)
    words_list=[]
    doc_text=[]
    for obj in objs:
        words_list.append(obj['title_seg'])
        doc_text.append(obj['title'])

    print len(base)

    base_dict = corpora.Dictionary(base)
    #drawDFS(base_dict.dfs,'base')
    domain_dict=corpora.Dictionary(words_list)
    
    print 'base_dict term count: %d' %len(base_dict)
    print 'domain_dict term count: %d' %len(domain_dict)
    #filter low fq words
    #domain_dict.filter_extremes(no_below=20,no_above=1.0) 
    #domain_dict.compactify() 
    #print 'after filter, domain_dict term count: %d' %len(domain_dict)
    base_dict.merge_with(domain_dict)
    print 'total dict term count: %d' %len(base_dict)
    base_dict.filter_extremes(no_below=20,no_above=1.0) 
    base_dict.compactify() 
    print 'filter base_dict term count: %d' %len(base_dict)
    #base_corpus_list = [base_dict.doc2bow(texts) for texts in base]
    target_corpus_list = [base_dict.doc2bow(texts) for texts in words_list]
    
    base_tfidf = models.TfidfModel(dictionary=base_dict)
    target_tfidf = models.TfidfModel(corpus=target_corpus_list)
    #drawDFS(target_tfidf.dfs,'select')
    #tfidf = models.TfidfModel(corpus=corpus_list,dictionary=base_dict)
    target_corpus_tfidf = base_tfidf[target_corpus_list]
    
    
    only_corpus_tfidf=target_tfidf[target_corpus_list]
    #corpus_tfidf = tfidf[corpus_list]
    
    #---save word tfidf --#
    saveTFIDF('total_tfidf08.txt',target_corpus_tfidf,base_dict,doc_text)
    #saveTFIDF('only_tfidf.txt',only_corpus_tfidf,base_dict,doc_text)
    
    

            
            
if __name__=='__main__':
    collection='discuss_news3'
    getTopic(collection)
    
    
    



    
