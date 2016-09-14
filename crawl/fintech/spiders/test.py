# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from datetime import datetime
from fintech.items import FintechItem
import time
import urllib2
import json
from pymongo import MongoClient
class FinTechSpider(Spider):
	name='test'
	allowed_domains=['discuss.com.hk']
	start_urls=['http://www.discuss.com.hk/forumdisplay.php?fid=475']
	
	#post={author,create_time,location,content,comments,last_status}
	#item=[{title, location, author, data:[{user,create_time,content,}]}]
	
	def __init__(self):
		self.i=1
		self.bNext=True
		client=MongoClient('localhost',27017)
		db=client['discusshk']
		self.post=db['post']
		self.stop=False
	def conDB(self):
		pass
	
	def getDB(self):
		pass
		
	def parse(self,response):
		print '\n'
		print self.i
		tables=Selector(response).css('tbody[id*=normalthread]')		
		print len(tables)

		for table in tables:
			#--- get content---#
			tag= '餐前餐後口水區'.decode('utf-8')
			title=table.css('span.tsubject a::text').extract()[0]
			if tag in title:
				continue
			href=table.css('span.tsubject a::attr(href)').extract()
			create_time=table.css('td.author em::text').extract()[0]
			author=table.css('td.author cite a::text').extract()[0]
			location=table.css('th em a::text').extract()
			if location:
				location=location[0]
			last_status=table.css('td.nums strong::text').extract()[0]
			#lastpost_user=table.css('td.lastpost cite a::text').extract()
			#commented=table.css('td.nums strong::text').extract()
			#viewed=table.css('td.nums em::text').extract()
			
			#print 'sub_link: %s' %href
			detial_url=response.urljoin(href[0])
			comments=[]
			graphs=[]
			meta={'location':location,'title':title,'author':author,'create_time':create_time,'last_status':last_status,'link':detial_url,'comments':comments,'graphs':graphs,'new_post':True}
			
			status=self.post.find_one({'title':title,'author':author,'create_time':create_time},{'last_status':1})
			if status:
				if status['last_status']==last_status:
					#--post didn't update--#
					self.stop=True
					return
				else:
					#--post had update--#
					meta['new_post']=False
					meta['_id']=status['_id']
					yield Request(detial_url, callback=self.detial_parse, meta=meta)
			else:
				meta['new_post']=True
				yield Request(detial_url, callback=self.detial_parse, meta=meta)
			
		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		next_url=response.urljoin(next_href[0])

		if not self.stop:
			if self.i <15:
				self.i+=1
				yield Request(next_url,callback=self.parse)
			

	def detial_parse(self,response):
		tables=Selector(response).css('div.mainbox.viewthread')
		comments=response.meta['comments']
		graphs=response.meta['graphs']
		title=response.meta['title']
		location=response.meta['location']
		author=response.meta['author']
		create_time=response.meta['create_time']
		last_status=response.meta['last_status']
		link=response.meta['link']
		new_post=response.meta['new_post']
		for table in tables:
			user=table.css('td.postauthor cite a::text').extract()[0]
			create_time=table.css('td.postcontent div.postinfo::text').extract()[4].strip()
			content=table.css('div.postmessage.defaultpost div.t_msgfont span::text,div.postmessage.defaultpost div.t_msgfont span img::attr(src)').extract()
			reply=table.css('div.postmessage.defaultpost div.t_msgfont span div.quote ').xpath('.//text()').extract()
			comment={'user':user, 'create_time':create_time, 'content':content}
			userA=user
			if reply:
				comment['reply']=reply
				userB=reply[2]
			else:
				userB=author
			if userA!=userB:
				graph={'src':userA,'dst':userB}
				graphs.append(graph)
			comments.append(comment)

		meta={'location':location,'title':title,'author':author,'create_time':create_time,'last_status':last_status,'link':link,'comments':comments,'new_post':new_post,'graphs':graphs}
		if response.meta.has_key('_id'):
			_id=response.meta['_id']
			meta['_id']=_id
		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		if next_href:
			#print 'sub_next_url: %s' %next_href
			next_url=response.urljoin(next_href[0])
			yield Request(next_url,callback=self.detial_parse,meta=meta)
			
		else:
			item=FintechItem()
			item['title']=response.meta['title']
			item['location']=response.meta['location']
			item['author']=response.meta['author']
			item['create_time']=response.meta['create_time']
			item['last_status']=response.meta['last_status']
			item['link']=response.meta['link']
			item['graphs']=response.meta['graphs']
			item['content']=comments[0]['content']
			del comments[0]
			item['comments']=comments
			
			#--insert into db--#
			if new_post:
				postInfo=dict(item)
				self.post.insert(postInfo)
			else:
				self.post.update({'_id':_id}, {'$set':{'comments':comments,'graphs':graphs}})
			yield item
			
			
