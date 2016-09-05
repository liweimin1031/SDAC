# -*- coding: utf-8 -*-
from pymongo import MongoClient


class basicData(object):
	def __init__(self):
		client = MongoClient('localhost', 27017)
		db = client['discusshk']
		
