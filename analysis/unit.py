# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo
from pymongo import MongoClient
from __builtin__ import list
import re
from scrapy.http.request.form import _select_value

class dbUnit(object):
	def __init__(self):
		client = MongoClient('localhost', 27017)
		db = client['financial']
		self.post = db['post']
		self.file = open('graph.txt', 'wb')
	
	def conDB(self):
		client = MongoClient('localhost', 27017)
		db = client['financial']
		post = db['post']
		return post
	
	def getGraph(self):

		relationships = self.post.find({'post_create_date':{'$gte':datetime(2016, 7, 1), '$lte':datetime(2016, 8, 2)}}, {'graphs':1, '_id':0})
		graph = []
		for  relationship in relationships:
			graph.extend(relationship['graphs'])
	
		print len(graph)
		for url in graph:
			if url['src'].strip() and url['dst'].strip():
				line = url['src'].encode('gb18030') + ' ' + url['dst'].encode('gb18030') + '\n'
				self.file.write(line)
			else:
				print 'err'

	def getTitle(self):
		title = self.post.find({'post_create_date':{'$gte':datetime(2016, 7, 1), '$lte':datetime(2016, 8, 2)}}, {'title':1, '_id':0})
		contents = []
		for  text in title:
			contents.append(text['title'])
		return contents

	def getContent(self):
		# title=self.post.find({'post_create_date':{'$gte':datetime(2016,7,1),'$lte':datetime(2016,8,2)}},{'title':1,'_id':0})
		start_date = '2016-7-1'
		end_date = '2016-8-2'
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
		db_contents = self.post.find({'post_create_date':{'$gte':start_date, '$lte':end_date}}, {'title':1, 'content.text':1, 'comments.content.text':1, '_id':0})
		contents = []
		for  db_content in db_contents:
			seg = []
			comment = db_content['comments']
			title = db_content['title']
			post_content = db_content['content']['text']
			post = [post.strip() for post in post_content]
			seg.append(title.strip())
			seg.append(''.join(post))
			'''
			for comment_list in comment:
				comment_text_list=[comment_text.strip() for comment_text in comment_list['content']['text']]
				comment_content=''.join(comment_text_list)
				if len(comment_text)>=10:
					seg.append(comment_content)
			'''
			contents.append(''.join(seg))
		return contents

	def select_keywords(self, keywords):
		# keywords must be unicode list
		reList = []
		start_date = '2016-7-1'
		end_date = '2016-8-2'
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
		dbReturn = {'post_create_date':1, 'title':1, 'content.text':1, 'link':1, 'last_status':1, '_id':0}
		select_date = {'$gte':start_date, '$lte':end_date}
		for w in keywords:
			word = re.compile(w)
			reList.append(word)
		result_list = self.post.find({'post_create_date':select_date, '$or':[{'title':{'$in':reList}}, {'content.text':{'$in':reList}}]}, dbReturn).sort([('post_create_date', pymongo.ASCENDING), ('last_status', pymongo.DESCENDING)])
		return result_list
	


	
	
	
