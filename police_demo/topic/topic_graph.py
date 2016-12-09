# -*- coding: utf-8 -*-
from pymongo import MongoClient
import time



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


def getDB(collection,start,end):
    post=conDB(collection)

    date_query={'$gte':start, '$lt':end}
    query={'created_time':date_query}
    
    count=post.find(query).count()#.sort([('created_time',1)])
    #find post_create_date and group comments.create_time
    
    #objs=post.find({},{'_id':0}).limit(50)
    return count

global_start_date=1451577600#'2016-1-1'
global_end_date='2016-12-31'
gap_time=60*60*24
date=[31,29,31,30,31,30,31,31,30,31,30,31]
topic_num=[]
month=[]
for i in range(0,12):
    if i==0:
        start=1451577600
    else:
        start=end
    
    end=start+date[i]*gap_time
    sum=getDB('discuss_news3',start,end)
    topic_num.append(sum)
    print sum
    month.append(i+1)
import numpy as np
from matplotlib import pyplot as plt
plt.figure(figsize=(9,6))
n = 12
X = np.arange(n)+1
Y1=topic_num
plt.bar(X,Y1,width = 0.5,facecolor = 'lightskyblue',edgecolor = 'white')
#width:柱的宽度

#给图加text
for x,y in zip(X,Y1):
    plt.text(x+0.3, y+0.05, y, ha='center', va= 'bottom')

plt.show()