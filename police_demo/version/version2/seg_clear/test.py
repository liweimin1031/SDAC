# -*- coding: utf-8 -*-
from pymongo import MongoClient
from seg import segmentation

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs


seg=segmentation()    

collection_name='discuss_news3'
post=conDB(collection_name)
query={'created_time':{'$gte':1475251200, '$lt':1477929600}}
objs=post.find(query)

for obj in objs:
    content=obj['title']
    seg_text=seg.segText(content)
    post.update({'_id':obj['_id']},{ '$set':{'title_seg':seg_text}})
    
print 'end'