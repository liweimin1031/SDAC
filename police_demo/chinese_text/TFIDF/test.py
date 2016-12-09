# -*- coding: utf-8 -*-
from pymongo import MongoClient
from seg import segmentation
import os

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs

corpus=[]
def find_file(arg,dirname,files):
    for file in files:
        file_path=os.path.join(dirname,file)
        if os.path.isfile(file_path):
            with open(file_path)as f:

                corpus.append(f.read().decode('utf-8'))

os.path.walk('..\data',find_file,())     
print len(corpus)
    
seg=segmentation()    

collection_name='corpus'
cur=conDB(collection_name)


for doc in corpus:
    seg_text=seg.segText(doc)
    cur.insert({'text':doc,'seg_text':seg_text})

# seg=segmentation()    
# with open('../data/hkej/instantnews_announcement_article_1028464.txt')as f1:
    # text=f1.read()
    # seg_text=seg.segText(text.decode('utf-8'))
    # print seg_text
    
print 'end'