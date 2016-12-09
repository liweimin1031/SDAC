#import settings as facebook_settings
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
print access_token
fb_name='HongKongPoliceForce'
target=graph.get(fb_name)
#fields='id,from,message,created_time,updated_time,reactions.limit(5),comments.limit(5){id,from,message,created_time,comments,likes}'
fields='reactions.limit(100){id,name,type}'
#dict={}
#posts=graph.get(target['id']+'/posts',limit=2, fields=fields,version='v2.6')
#fields=created_time,id,from,comment_count,message,like_count,likes,comments{parent,message,from,id}&limit=100
#fields=comments.limit(20){from,id,created_time,message,likes,comments},id,created_time,from,message,reactions,updated_time&limit=10

id =target['id']
print id
contents=graph.get(id+'/posts',limit=50,fields=fields,version='v2.6')
print contents


def getUrl(url):
	if '\\' in url:
		url=eval('u'+"'"+url+"'")
		url=url.replace('\\','')
	return url


def nextData(url,data):

	data_list=data
	#data.append(data)

	response=requests.get(url)
	dict=eval(response.text)
	data_list.extend(dict['data'])

	if dict['paging'].has_key('next'):
		url=getUrl(dict['paging']['next'])
		#print len(data_list)
		return nextData(url,data_list)
	else:
		#print data_list
		#print '\n function end and total items: '+str(len(data_list))+'\n'
		return data_list

		
print 'function start'

#------posts------#
posts=contents['data']
if posts['paging'].has_key('next'):
	url=getUrl(posts['paging']['next'])
	posts=nextData(url,data)
	
	
	
#------reactions------#
for i in range(0,len(posts)):
	reactions=posts[i]['reactions']
	if reactions['paging'].has_key('next'):
		url=getUrl(reactions['paging']['next'])
		reactions=nextData(url,data)
	posts[i]['reactions']=reactions
	print str(i)+':'+str(len(reactions))