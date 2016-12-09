# -*- coding: utf-8 -*-
import sys
import json
import re
reload(sys)
sys.setdefaultencoding( 'utf-8' )

posts_file=open('police_content.json')
try:
	posts_data=posts_file.read()
finally:
	posts_file.close()

object_list = json.loads(posts_data)


'''
for i in range(len(object_list)):
	if not(object_list[i].has_key('comments')):
		print 'comments:%d'%i
	if not object_list[i].has_key('reactions'):
		print 'reactions:%d'%i
'''
'''
doc=json.dumps(object_list[2])
file=open('2.json','wb')
file.write(doc)
'''
'''
#Get data array Drop paging#
for i in range(len(object_list)):
	print i
	reactions=[]
	if type(object_list[i]['reactions'])=='dict':
	#if object_list[i]['reactions'].has_key('data'):
		reactions=object_list[i]['reactions']['data']
		object_list[i]['reactions']=reactions
	
	comments=[]
	if type(object_list[i]['comments'])=='dict':
	#if object_list[i]['comments'].has_key('data'):
		comments=object_list[i]['comments']['data']
	else:
		comments=object_list[i]['comments']
	for j in range(len(comments)):
		if comments[j].has_key('likes'):
			comments[j]['likes']=comments[j]['likes']['data']
			
		if comments[j].has_key('comments'):
			reply_comments=comments[j]['comments']['data']
			comments[j]['comments']=reply_comments
			
			for k in range(len(reply_comments)):
				if reply_comments[k].has_key('likes'):
					comments[j]['comments'][k]['likes']=reply_comments[k]['likes']['data']
	object_list[i]['comments']=comments

'''	
'''
# only need message
for i in range(len(object_list)):
	print i
	object_list[i].pop('id')
	object_list[i].pop('reactions')
	object_list[i].pop('created_time')
	for j in range(len(object_list[i]['comments'])):
		object_list[i]['comments'][j].pop('id')
		object_list[i]['comments'][j].pop('created_time')
		object_list[i]['comments'][j].pop('from')
		if object_list[i]['comments'][j].has_key('likes'):
			object_list[i]['comments'][j].pop('likes')
		if object_list[i]['comments'][j].has_key('message_tags'):
			object_list[i]['comments'][j].pop('message_tags')
		if object_list[i]['comments'][j].has_key('comments'):
			for k in range(len(object_list[i]['comments'][j]['comments'])):
				object_list[i]['comments'][j]['comments'][k].pop('id')
				object_list[i]['comments'][j]['comments'][k].pop('created_time')
				object_list[i]['comments'][j]['comments'][k].pop('from')
				if object_list[i]['comments'][j]['comments'][k].has_key('message_tags'):
					object_list[i]['comments'][j]['comments'][k].pop('message_tags')
				if object_list[i]['comments'][j]['comments'][k].has_key('likes'):
					object_list[i]['comments'][j]['comments'][k].pop('likes')
'''


posts=[]

# only need message
for i in range(len(object_list)):
	print i
	post={'message':'','comments':[]}
	if object_list[i].has_key('message'):

		post['message']=object_list[i]['message'].replace('\\','\\').encode('gb18030').replace('\n','')
	if object_list[i].has_key('comments'):
		comments=[]
		for j in range(len(object_list[i]['comments'])):
			comment={}
			comments_message=object_list[i]['comments'][j]['message'].replace('\\','\\').encode('gb18030').replace('\n','')
			
			if object_list[i]['comments'][j].has_key('comments'):
				reply_comments=[]
				for k in range(len(object_list[i]['comments'][j]['comments'])):
					reply_comments.append(object_list[i]['comments'][j]['comments'][k]['message'].replace('\\','\\').encode('gb18030').replace('\n','')  )
				comment['reply_comments']=reply_comments
		
			comment['message']=comments_message
			comments.append(comment)
		post['comments']=comments
	posts.append(post)

print type(posts)

def save_file(file_name,file_data):
	doc=json.dumps(file_data,ensure_ascii=False)
	file=open(file_name,'wb')
	file.write(doc)

for i in range(0,len(posts),20):
		data=posts[i:i+20]
		name='police_content_cn_%d.json'%i
		save_file(name,data)
		
		
		
def save_file(file_name,file_data):
	doc=json.dumps(file_data,ensure_ascii=False)
	file=open(file_name,'wb')
	file.write(doc)
'''
doc=json.dumps(posts,ensure_ascii=False)
file=open('police_content_cn.json','wb')
file.write(doc)
'''
'''
post={
			'id':''
			'created_time':''
			'message':''
			'reactions':[{'type':'','id':'','name':''}]
			'comments':[{
								'id':''
								'created_time':''
								'message_tags':''
								'message':''
								'from':{'id':'','name':''}
								'likes':[{'id':'','name':''}]
								'comments':[{
													'id':''
													'created_time':''
													'message_tags':''
													'message':''
													'from':{'id':'','name':''}
													'likes':[{'id':'','name':''}]
													}]
								}]
		}
		'''