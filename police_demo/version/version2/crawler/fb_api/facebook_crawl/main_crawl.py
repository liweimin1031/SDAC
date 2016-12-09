# -*- coding: utf-8 -*-
import myMethod
import json
import time
from pymongo import MongoClient

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs

def datetime_timestamp(dt):
    #dt is string
    #2016-10-12T16:18:32+0000
    date=time.strptime(dt, '%Y-%m-%dT%X+0000')   
    s = time.mktime(date)
    return int(s)

#--get Last Date--#
def getPostsFields(fb_name):
    fb_cur=conDB(fb_name)
    obj=fb_cur.find({},{'created_time':1}).sort([('created_time',-1)]).limit(1)
    obj=list(obj)
    if obj:
        lastDate=obj[0]['created_time']
        selectTime=lastDate-7*24*60*60
        posts_fields='posts.since(%s).limit(100){id,message,created_time}'%str(selectTime)
    else:    
        posts_fields='posts.limit(100){id,message,created_time}'
    return posts_fields

#hkindigenous   youngspiration  100most
fb_name='hkindigenous'    
access_token='611406969009887|2BaFB_nqrIrunDAn6h8PzYZbovw'

graph=myMethod.fbAPI(access_token,'2.8')
profile=graph.getFBRequest(fb_name)

post_data={}
comments_data={}
reactions_data={}

#posts_fields='posts.limit(100){id,message,created_time}'
posts_fields=getPostsFields(fb_name)

#comments_fields='comments.limit(100){id,from,created_time,message_tags,message,likes.limit(100),comments.limit(100){id,from,created_time,message_tags,message,likes.limit(50)}}'
comments_fields='comments.limit(100){id,from,created_time,message,comments.limit(100){id,from,created_time,message}}'

#reactions_fields='reactions.limit(1000)'

posts=graph.getFBRequest(profile['id'],fields=posts_fields)


#------posts------#
posts=posts['posts']
if posts['paging'].has_key('next'):
    url=myMethod.getUrl(posts['paging']['next'])
    print url
    posts=myMethod.nextData(url,posts['data'])    
print 'get posts total: %d' %len(posts)

#------get posts ids-------#
start=time.time()
postDB=conDB(fb_name)
for i in range(len(posts)):
    print  'round %d'%(i+1)
    if i%500==0:
        time.sleep(120)
    comments=graph.getFBRequest(posts[i]['id'],fields=comments_fields)
    if comments.has_key('comments'):
        comments=comments['comments']
        if comments['paging'].has_key('next'):
            print 'next comments'
            url=myMethod.getUrl(comments['paging']['next'])
            comments=myMethod.nextData(url,comments['data'])
            
            print 'next comments'
        else:
            comments=comments['data']
    else:
        comments=[]
    posts[i]['comments']=comments
    for temp in comments:
        temp['created_time']=datetime_timestamp(temp['created_time'])
        if temp.has_key('comments'):
            re_comments=temp['comments']['data']
            for re_comment in re_comments:
                re_comment['created_time']=datetime_timestamp(re_comment['created_time'])
            temp['comments']=re_comments
                
    if posts[i].has_key('message'):
        message=posts[i]['message']
    else:
        message=''
    #print message
    if postDB.find_one({'post_id':posts[i]['id']}):
        postDB.update({'post_id':posts[i]['id']},{'$set':{ 'message':message,'comments':comments}})
        print 'update'
    else:
        postDB.insert({ 
                'created_time':datetime_timestamp(posts[i]['created_time']),
                'post_id': posts[i]['id'],
                'message':message,
                'comments':comments
        })
        print 'insert'
    #print 'post=%d: reactions=%d, comments=%d'%(i+1,len(reactions),len(comments))

'''
start=time.time()
for i in range(len(posts)):
    print  'round %d'%(i+1)
    reactions=graph.getRequest(posts[i]['id'],fields=reactions_fields)
    reactions=reactions['reactions']
    if reactions['paging'].has_key('next'):
        print 'next reactions'
        url=myMethod.getUrl(reactions['paging']['next'])
        reactions=myMethod.nextData(url,reactions['data'])
    else:
        reactions=reactions['data']
    comments=graph.getRequest(posts[i]['id'],fields=comments_fields)
    if comments.has_key('comments'):
        comments=comments['comments']
        if comments['paging'].has_key('next'):
            print 'next comments'
            url=myMethod.getUrl(comments['paging']['next'])
            comments=myMethod.nextData(url,comments['data'])
            print 'next comments'
        else:
            comments=comments['data']
    else:
        comments=[]
    posts[i]['reactions']=reactions
    posts[i]['comments']=comments
    #print 'post=%d: reactions=%d, comments=%d'%(i+1,len(reactions),len(comments))
'''
    
end=time.time()
print 'totally cost time: %d' %(end-start)




