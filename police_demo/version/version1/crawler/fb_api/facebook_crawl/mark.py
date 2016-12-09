# -*- coding: utf-8 -*-
import requests
from django.conf import settings
settings.configure()
from django_facebook import settings as facebook_settings
from open_facebook import OpenFacebook
from open_facebook.api import FacebookAuthorization
import json

facebook_settings.FACEBOOK_APP_ID ='611406969009887'
facebook_settings.FACEBOOK_APP_SECRET ='6be22272c73f9a90f8ded333fbb0ff4d'
access_token=FacebookAuthorization.get_app_access_token()
graph=OpenFacebook(access_token)

fb_name='HongKongPoliceForce'
target=graph.get(fb_name)
fields='reactions.limit(100){id,name,type},comments.limit(100){id,name}'
id=target['id']

print id
posts=graph.get(id+'/posts',limit=100,fields=fields,version='v2.6')



def getUrl(url):
	if '\\' in url:
		url=eval('u'+"'"+url+"'")
		url=url.replace('\\','')
	return url


def nextData(url,data):

	data_list=data

	response=requests.get(url)
	dict=eval(response.text)
	print dict
	data_list.extend(dict['data'])

	if not dict['data']:
		print 'dict is empty'
		return data_list
	
	elif dict['paging'].has_key('next'):
		url=getUrl(dict['paging']['next'])
		#print len(data_list)
		print 'nextData'
		return nextData(url,data_list)
	else:
		#print data_list
		#print '\n function end and total items: '+str(len(data_list))+'\n'
		return data_list


#------posts------#
#posts=contents['data']
if posts['paging'].has_key('next'):
	url=getUrl(posts['paging']['next'])
	print url
	posts=nextData(url,posts['data'])
	

print len(posts)





print 'start '
for i in range(0,len(posts)):
	#------reactions------#
	reactions=posts[i]['reactions']
	reactions_data=reactions['data']
	if reactions['paging'].has_key('next'):
		url=getUrl(reactions['paging']['next'])
		reactions_data=nextData(url,reactions_data)
	posts[i]['reactions']=reactions_data
	
	#------comments------#
	comments=posts[i]['comments']
	comments_data=comments['data']
	if comments['paging'].has_key('next'):
		url=getUrl(comments['paging']['next'])
		comments_data=nextData(url,comments_data)
	posts[i]['comments']=comments_data
	print 'post=%d: reactions=%d, comments=%d'%(i+1,len(reactions_data),len(comments_data))
	
	 #---for test---#
	if i==2:             
		break
	
print 'end reactions'


doc=json.dumps(posts)
file=open('police.json','wb')
file.write(doc)

'''
#------comments------#
print 'start comments'
for i in range(0,len(posts)):
	
	comments=posts[i]['comments']

	#print type(reactions) 
	comments_data=comments['data']
	if comments['paging'].has_key('next'):
		url=getUrl(comments['paging']['next'])
		comments_data=nextData(url,comments_data)
	posts[i]['comments']=comments_data
	print str(i)+':'+str(len(comments_data))
	
print 'end comments'

'''



# -*- coding: utf-8 -*-
import requests
from django.conf import settings
settings.configure()
from django_facebook import settings as facebook_settings
from open_facebook import OpenFacebook
from open_facebook.api import FacebookAuthorization
import json

facebook_settings.FACEBOOK_APP_ID ='611406969009887'
facebook_settings.FACEBOOK_APP_SECRET ='6be22272c73f9a90f8ded333fbb0ff4d'

access_token=FacebookAuthorization.get_app_access_token()
graph=OpenFacebook(access_token)

fb_name='HongKongPoliceForce'
target=graph.get(fb_name)
id=target['id']

print id
fields='reactions.limit(100),comments.limit(100){id,message_tags,message}'
#fields='reactions.limit(200){id,name,type},comments.limit(100){id,name,comments}'
#fields='comments.limit(100){id,from,created_time,comments.limit(100){from,id,message,message_tags,created_time},message,message_tags},id,reactions.limit(100),updated_time,created_time,message'

#fields='comments.limit(10)'
#fields='id,message,created_time,updated_time,reactions.limit(100){id,name,type},comments.limit(100){id,from,message,message_tags,created_time,likes,comments.limit(100){id,from,message,message_tags,created_time,likes}}'
posts=graph.get(id+'/posts',limit=100,fields=fields,version='v2.6')


def getUrl(url):
	if '\\' in url:
		url=eval('u'+"'"+url+"'")
		url=url.replace('\\','')
	return url


def nextData(url,data):

	data_list=data

	response=requests.get(url)
	dict=eval(response.text)
	if dict['error']:
		print dict['error']
		return data_list

	if not dict['data']:
		print 'dict is empty'
		return data_list
	data_list.extend(dict['data'])
	elif dict['paging'].has_key('next'):
		url=getUrl(dict['paging']['next'])
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
	print url
	posts=nextData(url,posts['data'])
	

print 'get posts total: %d' %len(posts)

doc=json.dumps(posts)
file=open('police.json','wb')
file.write(doc)


'''
print 'start '
for i in range(0,len(posts)):
	#------reactions------#
	print 'round %d' %(i+1)
	print 'start reactions'
	reactions=posts[i]['reactions']
	reactions_data=reactions['data']
	if reactions['paging'].has_key('next'):
		url=getUrl(reactions['paging']['next'])
		reactions_data=nextData(url,reactions_data)
	posts[i]['reactions']=reactions_data
	print 'end reactions'
	#------comments------#
	print 'strat comments '
	comments=posts[i]['comments']
	comments_data=comments['data']
	if comments['paging'].has_key('next'):
		url=getUrl(comments['paging']['next'])
		comments_data=nextData(url,comments_data)
	posts[i]['comments']=comments_data
	print 'post=%d: reactions=%d, comments=%d'%(i+1,len(reactions_data),len(comments_data))
	print 'end comments'
	 #---for test---#
	if i==2:             
		break
	
print 'end reactions'




doc=json.dumps(posts)
file=open('police.json','wb')
file.write(doc)

'''


'''
#------comments------#
print 'start comments'
for i in range(0,len(posts)):
	
	comments=posts[i]['comments']

	#print type(reactions) 
	comments_data=comments['data']
	if comments['paging'].has_key('next'):
		url=getUrl(comments['paging']['next'])
		comments_data=nextData(url,comments_data)
	posts[i]['comments']=comments_data
	print str(i)+':'+str(len(comments_data))
	
print 'end comments'

'''

'''		headers=response.headers
		if 'json' in headers['content-type']:
			print 'json'
			result = response.json()
		elif "access_token" in parse_qs(response.text):
			query_str = parse_qs(response.text)
			if "access_token" in query_str:
				result = {"access_token": query_str["access_token"][0]}
				if "expires" in query_str:
					result["expires"] = query_str["expires"][0]
			else:
				print response.json() #test
				#raise GraphAPIError(response.json())
		else:
			print 'Maintype was not text, image, or querystring' #test
			#raise GraphAPIError('Maintype was not text, image, or querystring') '''