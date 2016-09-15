# -*- coding: utf-8 -*-
import PreProcessUtils
from pyspark import SparkContext

from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.feature import IDF

sc = SparkContext(appName="LatentDirichletAllocationExample")  # SparkContext
#--Load and parse the data--#
#datalist=PreProcessUtils.dataPrepare()
#data = sc.parallelize(datalist)
data=sc.textFile('../../data/lda_data.txt')

#--transform data to tf vectors --#
htf = HashingTF()
tfData=htf.transform(data)
#transform to tf-idf vectors
idf = IDF()
idfData = idf.fit(tfData)
tfidf = idfData.transform(tfData)

#parsedData = data.map(lambda line: Vectors.dense([float(x) for x in line.strip().split(' ')]))

print (tfidf.collect())

# Index documents with unique IDs
corpus = tfidf.zipWithIndex().map(lambda x: [x[1], x[0]]).cache()
print (corpus.collect())
# Cluster the documents into three topics using LDA
ldaModel = LDA.train(corpus, k=3)

# Output topics. Each is a distribution over words (matching word count vectors)
print("Learned topics (as distributions over vocab of " + str(ldaModel.vocabSize()) + " words):")
topics = ldaModel.topicsMatrix()
for topic in range(3):
    print("Topic " + str(topic) + ":")
    for word in range(0, ldaModel.vocabSize()):
        print(" " + str(topics[word][topic]))

'''
# Save and load model
ldaModel.save(sc, "C:/spark/data/mllib/model/lda.obj")
sameModel = LDAModel.load(sc, "C:/spark/data/mllib/model/lda.obj")
'''