# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FintechItem(scrapy.Item):
	# define the fields for your item here like:
	title=scrapy.Field()
	comments=scrapy.Field()
	author=scrapy.Field()
	post_create_date=scrapy.Field()
	last_status=scrapy.Field()
	viewed=scrapy.Field()
	link=scrapy.Field()
	content=scrapy.Field()
	comments=scrapy.Field()
	graphs=scrapy.Field()
	thread_id=scrapy.Field()
	
	#pass
