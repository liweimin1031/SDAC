# -*- coding: utf-8 -*-
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from datetime import datetime
import urllib2
import json

class FinTechSpider(BaseSpider):
	name='debug'
	allowed_domains=['discuss.com.hk']
	start_urls=['http://finance.discuss.com.hk/viewthread.php?tid=25961010&extra=page%3D1']
	
	def parse(self,response):
		tables=Selector(response).css('div.mainbox.viewthread')
		for table in tables:
			user=table.css('td.postauthor cite a::text').extract()[0]
			print 'user:%s'%user
			comment_datetime=table.css('td.postcontent div.postinfo::text').extract()
			
			
			print 'comment time:%s'%comment_datetime
	#		comment_datetime=comment_datetime.encode('utf-8')
	#		comment_datetime=datetime.strptime(comment_datetime,timeFormat)
	#		comment_intTime=int(comment_datetime.strftime('%H%M'))

		next_href=Selector(response).css('div.pages_btns div.pages a.next::attr(href)').extract()
		if next_href:
			next_url=response.urljoin(next_href[0])
			yield Request(next_url,callback=self.detial_parse)

		
		

