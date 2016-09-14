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
class goldenSpider(Spider):
	name='golden'
	allowed_domains=['hkgolden.com']
	start_urls=['http://forum7.hkgolden.com/topics.aspx?type=FN']
	
	def __init__(self):
		self.i=1
		self.bNext=True
		client=MongoClient('localhost',27017)
		db=client['golden']
		self.post=db['post']
		self.stop=False
	def conDB(self):
		pass
	
	def getDB(self):
		pass
		
	def parse(self,response):
		print '\n'
		print self.i
		tables=Selector(response).css('tr[id*=Thread_No]')		
		print len(tables)

		for table in tables:
			#--- get content---#
			title=table.xpath('./td[2]/a/text()').extract()[0]
			post_href=table.xpath('./td[2]/a/@href').extract()[0]
			post_url=response.urljoin(post_href)
			author=table.xpath('./td[3]/a/text()').extract()[0]
			user_profile_href=table.xpath('./td[3]/a/@href').extract()[0]
			user_profile_url=response.urljoin(user_profile_href)
			last_reply_time=table.xpath('./td[4]//text()').extract()[0]
			last_reply_number=table.xpath('./td[5]//text()').extract()[0]
			score=table.xpath('./td[6]//text()').extract()[0]
			meta={'title':title,'author':author,'last_reply_number':last_reply_number,'last_reply_time':last_reply_time,'post_url':post_url,'comments':comments,'score':score}
			yield Request(post_url, callback=self.detial_parse, meta=meta)

			

		next_href=Selector(response).css('div.ContentPanel').xpath('.//a[contains(.,"ÏÂÒ»í“")]/@href').extract()
		print next_href
		next_url=response.urljoin(next_href[0])
		if next_url:
			if self.i <2:
				self.i+=1
				yield Request(next_url,callback=self.parse)
			

	def detial_parse(self,response):
		tables=Selector(response).css('table.repliers')
		meta=response.meta
		title=meta['title']
		author=meta['author']
		user_profile_href=meta['user_profile_href']
		user_profile_url=meta['user_profile_url']
		last_reply_time=meta['last_reply_time']
		last_reply_number=meta['last_reply_number']
		score=meta['score']
		
		
		for table in tables:
			user=table.css('td.repliers_left').xpath('.//text()').extract()
			content=table.css('div.ContentGrid').xpath('.//text() | .//img/@src').extract()
			create_time=table.css('table.repliers_right').xpath('./tbody/tr[last()]//span//text()').extract()
		#	comment={'user':user,'content':content,'create_time':create_time}
		#	comments.append(comment)
		next_href=Selector(response).xpath('//div[@id="mainTopicTable"]//a/@href').extract()
		if next_href:
			#print 'sub_next_url: %s' %next_href
			next_url=response.urljoin(next_href[0])
			yield Request(next_url,callback=self.detial_parse,meta=meta)
			
		else:
			#--insert into db--#
			postInfo=dict(item)
			self.post.insert(postInfo)
			yield item
			
			
