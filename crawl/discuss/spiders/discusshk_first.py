# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import discuss.settings as settings
import scrapy
import time
from discuss.items import DiscussItem,UserItem
import urllib2
import json
from pymongo import MongoClient
import logging
class DiscussSpider(Spider):
	name='discuss_first'
	allowed_domains=['discuss.com.hk']
	start_urls=[('news','http://news.discuss.com.hk/forumdisplay.php?fid=54&page=')
					]
	repeat_count=0
	maxCount=10
	Next=True
	
	def __init__(self):
		self.start=1
		
		#con las dev database
		client = MongoClient('int-db01.elana.org', 27017)
		db_auth = client['las_dev']
		db_auth.authenticate("las_dev", "DB41as-1")
		db = client['las_dev']
		self.user=db[settings.USER_COLLECTION]
		self.discuss=db[settings.POST_COLLECTION]
		self.tag_timeFormat='發表於 %Y-%m-%d %I:%M %p'
		self.tag_permisson='閱讀權限'.decode('utf-8')
		
		
	def datetime_timestamp(self,dt):
		#dt is string
		date=time.strptime(dt, self.tag_timeFormat)
		s = time.mktime(date)
		return int(s)
	
	def start_requests(self):
		#@Overridden start_requests
		for temp in self.start_urls:
			category=temp[0]
			url=temp[1]+str(self.start)
			yield scrapy.Request(url=url, callback=self.parse,meta={'category':category})


	def parse(self,response):
		print self.start

		selector=Selector(response)
		tables=selector.css('tbody[id*=normalthread]')
		category=response.meta['category']
		
		#next_href=selector.css('div.pages_btns div.pages a.next::attr(href)').extract()[0]
		#next_url=response.urljoin(next_href)
		
		prase_meta=response.meta
		for table in tables:
			thread_id=table.css('tbody::attr(id)').extract()[0]
			thread_id=thread_id.replace('normalthread',category)
			title=table.css('span.tsubject a::text').extract()[0]
			permisson=table.xpath('./tr/th/text()').extract()
			permisson= ''.join(permisson).strip()
			#--skip the post which need permisson
			if self.tag_permisson in permisson:
				continue
			href=table.css('span.tsubject a::attr(href)').extract()
	#		post_create_date=table.css('td.author em::text').extract()[0]
	#		post_create_date=datetime.strptime(post_create_date,'%Y-%m-%d')
			author=table.css('td.author cite a::text').extract()[0]
			last_status=table.css('td.nums strong::text').extract()[0]
			#lastpost_user=table.css('td.lastpost cite a::text').extract()
			viewed=table.css('td.nums em::text').extract()[0]

			detial_url=response.urljoin(href[0])
			posts=[]
			graphs=[]
			detial_prase_meta={'category':category,'thread_id':thread_id,'title':title,'author':author,'last_status':last_status,'viewed':viewed,'link':detial_url,'posts':posts,'graphs':graphs,'new_post':True}
			
			#check the post already have
			posted=self.discuss.find_one({'thread_id':thread_id},{'last_status':1})
			if posted:
				status=posted['last_status']
				detial_prase_meta['new_post']=False
				if status==last_status:
					self.repeat_count+=1
					print 'same'
					if self.repeat_count>self.maxCount:
						print 'stop'
						self.Next=False
						break
				else:
					
					self.repeat_count=0
					
			else:
				detial_prase_meta['new_post']=True
				self.repeat_count=0
			
			yield Request(detial_url, callback=self.detial_parse, meta=detial_prase_meta)
						
		self.start+=1
		if self.start <=1000 and self.Next:
			
			next_url=self.start_urls[0][1]+str(self.start)
			try:
				yield Request(next_url,callback=self.parse,meta=prase_meta)
			except Exception as e:
				print e
				print 'err url: %s ' %next_url 

	def detial_parse(self,response):
		tables=Selector(response).css('div.mainbox.viewthread')
		posts=response.meta['posts']
		graphs=response.meta['graphs']
		category=response.meta['category']
		thread_id=response.meta['thread_id']
		title=response.meta['title']
		author=response.meta['author']
		last_status=response.meta['last_status']
		viewed=response.meta['viewed']
		link=response.meta['link']
		new_post=response.meta['new_post']
		user_item=UserItem()
		for table in tables:
			user=table.css('td.postauthor cite a::text').extract()[0]
			userid=table.css('td.postauthor cite a::attr(href)').extract()[0]
			userid=userid.replace('space.php?uid=','')
			#--check user in db--#
			#db_user=self.user.find({'userid':userid})
			#db_user=list(db_user)
			#if not db_user:				
			user_img=table.css('td.postauthor div.avatar img::attr(src)').extract()[0]
			user_profile=table.css('td.postauthor dl.profile dd::text').extract()
			user_register_time=user_profile[3].strip()
			user_item['userid']=userid
			user_item['name']=user
			user_item['img']=user_img
			user_item['register_time']=user_register_time
			yield user_item
			
			created_time=table.css('td.postcontent div.postinfo::text').extract()
			created_time= ''.join(created_time).strip().encode('utf-8')
			created_time=self.datetime_timestamp(created_time)
			text=table.css('div.postmessage.defaultpost div.t_msgfont span::text').extract()
			#text=''.join(text)   
			text=''.join([temp.strip() for temp in text])
			#image=table.css('div.postmessage.defaultpost div.t_msgfont span img::attr(src)').extract()
			reply=table.css('div.postmessage.defaultpost div.t_msgfont span div.quote ').xpath('.//text()').extract()
			post={'user':user, 'created_time':created_time, 'text':text}
			userA=user
			if len(reply)>=3:
				post['reply']=reply
				userB=reply[2]
			else:
				userB=author
			if userA!=userB:
				graph={'src':userA,'dst':userB}
				graphs.append(graph)
			posts.append(post)

		meta={'category':category,'thread_id':thread_id,'title':title,'author':author,'last_status':last_status,'viewed':viewed,'link':link,'posts':posts,'graphs':graphs,'new_post':new_post}
		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		if next_href:
			#print 'sub_next_url: %s' %next_href
			next_url=response.urljoin(next_href[0])
			yield Request(next_url,callback=self.detial_parse,meta=meta)
			
		else:
			item=DiscussItem()
			item['category']=response.meta['category']
			item['thread_id']=response.meta['thread_id']
			item['title']=response.meta['title']
			item['author']=response.meta['author']
			item['last_status']=response.meta['last_status']
			item['viewed']=response.meta['viewed']
			item['link']=response.meta['link']
			item['graphs']=response.meta['graphs']
			item['new_post']=response.meta['new_post']
			item['created_time']=posts[0]['created_time']
			item['content']=posts[0]['text']
			#item['comments']=response.meta['posts']
			comments=response.meta['posts']
			del comments[0]
			item['comments']=comments

			yield item
			