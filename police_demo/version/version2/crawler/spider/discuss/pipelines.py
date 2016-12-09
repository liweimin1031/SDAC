# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from pymongo import MongoClient
from discuss.items import DiscussItem,UserItem
import discuss.settings as settings

class MongoPipeline(object):
	
	discuss_collection=settings.POST_COLLECTION
	user_collection=settings.USER_COLLECTION
	
	def open_spider(self, spider):
		self.client = MongoClient('int-db01.elana.org', 27017)
		db_auth = self.client['las_dev']
		db_auth.authenticate("las_dev", "DB41as-1")
		self.db = self.client['las_dev']

	def close_spider(self, spider):
		self.client.close()
		
	def process_item(self, item, spider):
		if isinstance(item, DiscussItem):
			discuss=self.db[self.discuss_collection]
			doc=dict(item)
			if doc['new_post']:
				doc.pop('new_post')
				discuss.insert(doc)
			else:
				doc.pop('new_post')
				discuss.update({'thread_id':doc['thread_id']},{'$set':{'comments':doc['comments'],'last_status':doc['last_status'],'viewed':doc['viewed'],'graphs':doc['graphs']}})
		elif isinstance(item,UserItem):
			user=self.db[self.user_collection]
			doc=dict(item)
			if not user.find_one({'userid':doc['userid']}):
				user.insert(doc)
		
		#return item
