# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo
from pymongo import MongoClient
import re



class dbUnit(object):
	def __init__(self):
		client = MongoClient('localhost', 27017)
		db = client['financial']
		self.post = db['post']
		self.file = open('graph.txt', 'wb')
	
	def conLAS(self,collection):
		client = MongoClient('int-db01.elana.org', 27017)
		db_auth = client['las_dev']
		db_auth.authenticate("las_dev", "DB41as-1")
		db = client['las_dev']
		curs=db[collection]
		return curs
	
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
		end_date = '2016-8-1'
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
			#add comment date
			for comment_list in comment:
				comment_text_list=[comment_text.strip() for comment_text in comment_list['content']['text']]
				comment_content=''.join(comment_text_list)
				if len(comment_text)>=10:
					seg.append(comment_content)
			
			contents.append(''.join(seg))
		return contents

	def select_keywords(self, keywords):
		# keywords must be unicode list
		reList = []
		for w in keywords:
			word = re.compile(w)
			reList.append(word)
		result_list = []
		start_date = '2016-7-1'
		end_date = '2016-8-2'
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
		
		titleReturn = {'post_create_date':1, 'title':1, 'last_status':1, '_id':0}
		commentReturn = {'comments.create_time':1, 'comments.content.text':1, '_id':0}
		postReturn = {'post_create_date':1, 'content.text':1, '_id':0}
		
		sort_title_term=[('post_create_date', pymongo.ASCENDING)]
		sort_comment_term=[('create_time', pymongo.ASCENDING)]
		sort_post_term=[('post_create_date', pymongo.ASCENDING)]
		
		select_date = {'$gte':start_date, '$lte':end_date}
		select_title_term={'post_create_date':select_date, 'title':{'$in':reList}}
		select_comment_term={'comments.create_time':select_date, 'comments.content.text':{'$in':reList}}
		select_post_term={'post_create_date':select_date, 'content.text':{'$in':reList}}

		title=self.post.find(select_title_term,titleReturn).sort(sort_title_term)
		post=self.post.find(select_post_term, postReturn).sort(sort_post_term)
		comment=self.post.find(select_comment_term, commentReturn).sort(sort_comment_term)
		
		result_list=self.post.aggregate([
										{'$project':{'comments.create_time':1, 'comments.content.text':1, '_id':0}},
										{'$unwind':'$comments'},{'$match':{'comments.create_time':select_date,'comments.content.text':{'$in':reList}}},
										{'$group': {'_id': '$comments.create_time', 'content': {'$push': '$comments.content.text'}}},
										{'$sort':{'_id':1}}])
		
		
		return result_list
	


	
	
	
