# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import time
from fintech.items import FintechItem
import urllib2
import json
from pymongo import MongoClient
class FinTechSpider(Spider):
	name='discuss'
	allowed_domains=['discuss.com.hk']
	start_urls=['http://finance.discuss.com.hk/forumdisplay.php?fid=54']
		
	def __init__(self):
		self.i=1
		self.bNext=True
		
		#con las dev database
		client = MongoClient('int-db01.elana.org', 27017)
		db_auth = client['las_dev']
		db_auth.authenticate("las_dev", "DB41as-1")
		db = client['las_dev']
		self.post=db['discuss']
		
		self.stop=False
		self.tag_timeFormat='發表於 %Y-%m-%d %I:%M %p'
		self.tag_permisson='閱讀權限'.decode('utf-8')
		
	def datetime_timestamp(self,dt):
		#dt is string
		date=time.strptime(dt, self.tag_timeFormat)
		s = time.mktime(date)
		return int(s)
		
	def parse(self,response):
		print 'start'
		tables=Selector(response).css('tbody[id*=normalthread]')

		for table in tables:
			thread_id=table.css('tbody::attr(id)').extract()[0]
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
			comments=[]
			graphs=[]
			meta={'thread_id':thread_id,'title':title,'author':author,'last_status':last_status,'viewed':viewed,'link':detial_url,'comments':comments,'graphs':graphs,'new_post':True}
			
			status=self.post.find_one({'thread_id':thread_id},{'last_status':1})
			if status:
				if status['last_status']==last_status:
					#--post didn't update--#
					self.stop=True
					return
				else:
					#--post had update--#
					meta['new_post']=False
					yield Request(detial_url, callback=self.detial_parse, meta=meta)
			else:
				meta['new_post']=True
				yield Request(detial_url, callback=self.detial_parse, meta=meta)
			
		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		next_url=response.urljoin(next_href[0])

		if not self.stop:
			if self.i <15:
				print self.i
				self.i+=1
				yield Request(next_url,callback=self.parse)
			

	def detial_parse(self,response):
		tables=Selector(response).css('div.mainbox.viewthread')
		comments=response.meta['comments']
		graphs=response.meta['graphs']
		thread_id=response.meta['thread_id']
		title=response.meta['title']
		author=response.meta['author']
		last_status=response.meta['last_status']
		viewed=response.meta['viewed']
		link=response.meta['link']
		new_post=response.meta['new_post']
		for table in tables:
			user=table.css('td.postauthor cite a::text').extract()[0]
			create_time=table.css('td.postcontent div.postinfo::text').extract()
			create_time= ''.join(create_time).strip().encode('utf-8')
			create_time=self.datetime_timestamp(create_time)
			text=table.css('div.postmessage.defaultpost div.t_msgfont span::text').extract()
			#image=table.css('div.postmessage.defaultpost div.t_msgfont span img::attr(src)').extract()
			reply=table.css('div.postmessage.defaultpost div.t_msgfont span div.quote ').xpath('.//text()').extract()
			comment={'user':user, 'create_time':create_time, 'text':text}
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

		meta={'thread_id':thread_id,'title':title,'author':author,'last_status':last_status,'viewed':viewed,'link':link,'comments':comments,'new_post':new_post,'graphs':graphs}
		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		if next_href:
			#print 'sub_next_url: %s' %next_href
			next_url=response.urljoin(next_href[0])
			yield Request(next_url,callback=self.detial_parse,meta=meta)
			
		else:
			item=FintechItem()
			item['thread_id']=response.meta['thread_id']
			item['title']=response.meta['title']
			item['author']=response.meta['author']
			item['last_status']=response.meta['last_status']
			item['viewed']=response.meta['viewed']
			item['link']=response.meta['link']
			item['graphs']=response.meta['graphs']
			item['post_create_date']=comments[0]['create_time']
			item['content']=comments[0]['text']
			del comments[0]
			item['comments']=comments
			
			#--insert into db--#
			if new_post:
				postInfo=dict(item)
				self.post.insert(postInfo)
			else:
				self.post.update({'thread_id':thread_id}, {'$set':{'comments':comments,'last_status':last_status,'viewed':viewed,'graphs':graphs}})
			yield item
			