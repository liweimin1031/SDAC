# -*- coding: utf-8 -*-
import facebook
import json
import time
app_id = '611406969009887' 
app_secret = "6be22272c73f9a90f8ded333fbb0ff4d" 
access_token=facebook.GraphAPI().get_app_access_token(app_id, app_secret)
print access_token +' \n'
#access_token='EAACEdEose0cBAMQdAdwE51ZBgNwMGEiLe8WJPkeo6rG2jpSQRQP2AUnkpmnbTEgAz4VKgiZBW9fhLDGVNhZBukvU22hdx6scVikjVZAPe4fRYCZAg9MfMYzVZCdPbOkqWo3qsuZCMMyFOhImJaRFxtx5sNiv2v95ZCtBHJZAeotxTSAZDZD'
#graph=facebook.GraphAPI()
graph=facebook.GraphAPI(access_token)
#fb_name='1546925482228025'
fb_name = 'HongKongPoliceForce'
#user='100002713419731'

user=graph.get_object('me')
#name=post['name']
id=user['id']
#print post
#print name.encode('GB18030')
posts=graph.get_connections(id,'posts')
#print datas['data']
#line=json.dumps(datas['data'],ensure_ascii=False)+'\n'
#print line
items=[]
i=0
for post in posts['data']:
	i=i+1
	comments=graph.get_connections(post['id'],'comments')
	
	item={'number':i,'post':post,'comments':comments['data']}
	items.append(item)
print items
doc=json.dumps(items)+'\n'
file=open('police.json','wb')
file.write(doc)
	#print jComments

#line=json.dumps(datas['data'],ensure_ascii=True)+'\n'
#1546925482228025_1711231592464079/comments?fields=created_time,id,from,comment_count,message,like_count,likes,comments{parent,message,from,id}&limit=100
'''while True:
	getPostComments()
	time.sleep(3600)'''
#def saveData(data):
	# ######