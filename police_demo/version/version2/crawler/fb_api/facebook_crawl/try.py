import requests
import facebook
import json
import time
import httplib2


FACEBOOK_APP_ID ='611406969009887'
FACEBOOK_APP_SECRET ='6be22272c73f9a90f8ded333fbb0ff4d'
fb_name='HongKongPoliceForce'

post_data={}
comments_data={}
reactions_data={}

access_token= facebook.GraphAPI().get_app_access_token(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)
print access_token

graph = facebook.GraphAPI(access_token, timeout=30,version='2.6')

profile=graph.get_object(fb_name)


#postids=['960526577368640_1079296418824988','960526577368640_1078642538890376','960526577368640_1078023762285587','960526577368640_1077918332296130','960526577368640_1077302345691062','960526577368640_1076696552418308','960526577368640_1076243532463610','960526577368640_1076075595813737','960526577368640_1075508755870421','960526577368640_1074834519271178','960526577368640_1074814532606510']


posts_fields='posts.limit(100){id,message,created_time}'

comments_fields='comments.limit(100){id,from,created_time,message_tags,message,likes.limit(100),comments.limit(100){id,from,created_time,message_tags,message,likes.limit(50)}}'

reactions_fields='reactions.limit(1000)'

posts=graph.get_object(profile['id'],fields=posts_fields)

h = httplib2.Http()

def getUrl(url):
	if '\\' in url:
		url=eval('u'+"'"+url+"'")
		url=url.replace('\\','')
	return url

def nextData(url,data):
	data_list=data
	resp, response=h.request(url)
	dict=eval(response)
	
	#response=requests.get(url)
	#dict=eval(response.text)
	#print url
	#print '\n'
	if dict.has_key('error'):
		print dict
		#return dict
		return data_list
	if not dict['data']:
		return data_list
	data_list.extend(dict['data'])
	#print 'data_list:%d'%len(data_list)
	if dict['paging'].has_key('next'):
		print 'next'
		url=getUrl(dict['paging']['next'])
		#print url
		#print len(data_list)
		return nextData(url,data_list)
	else:
		#print data_list
		#print '\n function end and total items: '+str(len(data_list))+'\n'
		return data_list



#------posts------#
posts=posts['posts']
if posts['paging'].has_key('next'):
	url=getUrl(posts['paging']['next'])
	#print url
	posts=nextData(url,posts['data'])	
print 'get posts total: %d' %len(posts)


#------get posts ids-------#
count_next_comment=0
start=time.time()
for i in range(len(posts)):
	print  'round %d'%(i+1)
	
	#if (i+1)%50==0:
		#time.sleep(10)
	
	
	reactions=graph.get_object(posts[i]['id'],fields=reactions_fields)
	reactions=reactions['reactions']
	if reactions['paging'].has_key('next'):
		print 'next reactions'
		url=getUrl(reactions['paging']['next'])
		reactions=nextData(url,reactions['data'])
	comments=graph.get_object(posts[i]['id'],fields=comments_fields)
	if comments.has_key('comments'):
		comments=comments['comments']
		if comments['paging'].has_key('next'):
			print 'next comments'
			url=getUrl(comments['paging']['next'])
			comments=nextData(url,comments['data'])
			count_next_comment=count_next_comment+1
			print 'next comments'
	else:
		comments['comments']=''
	posts[i]['reactions']=reactions
	posts[i]['comments']=comments
	#print 'post=%d: reactions=%d, comments=%d'%(i+1,len(reactions),len(comments))
	
end=time.time()
print 'totally cost time: %d' %(end-start)



doc=json.dumps(posts)
file=open('try.json','wb')
file.write(doc)


