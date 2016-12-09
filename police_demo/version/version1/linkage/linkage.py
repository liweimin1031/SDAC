import networkx as nx
import json
import matplotlib.pyplot as plt
import numpy as np
import math

from pymongo import MongoClient

linkage={}
nodes=[]
links=[]

def conDB(collection):
    client = MongoClient('int-db01.elana.org', 27017)
    db_auth = client['las_dev']
    db_auth.authenticate("las_dev", "DB41as-1")
    db = client['las_dev']
    curs=db[collection]
    return curs

def loadData(filename):
    file=open(filename)
    try:
        object=file.read()
    finally:
        file.close()
    return json.loads(object)
G=nx.DiGraph()
localEdges=[]
'''relationships=loadData('relationships10.json')

for relationship in relationships:
    localEdge=(relationship['src'],relationship['dst'],{'relationship':relationship['relationship']})
    localEdges.append(localEdge)

G.add_edges_from(localEdges)'''

discuss=conDB('discuss_news3')
date_query={'$gte':1475164800,'$lt':1476979200}
query={'created_time':date_query}

relationships=discuss.find(query,{'graphs':1}).limit(5)

for relationship in relationships:
    graphs=relationship['graphs']
    for graph in graphs:
        localEdge=(graph['src'],graph['dst'])
        localEdges.append(localEdge)
        links.append({ 'source':graph['src'] ,'target': graph['dst'] })
G.add_edges_from(localEdges)
layout = nx.spring_layout(G)
degree_node_size=[math.log(float(G.degree(v))) for v in G] 
plt.figure(1)
nx.draw(G,pos=layout, node_size=node_size, node_color='y')
pr=nx.pagerank(G)
for temp in pr:
    name=temp
    v=pr[name]
    value=math.log(v*500+1)*100
    nodes.append({'name':name,'value':value})

print 'node: %d' %len(pr)
with open('linkage_data01.json','w+')as f1:
    linkage['nodes']=nodes
    linkage['links']=links
    json.dump(linkage,f1)
pr_node_size=[math.log(v*500+1)*100 for v in pr.values()] 
plt.figure(2)
nx.draw(G, pos=layout, node_size=pr_node_size,node_color='r',with_labels=False)

plt.show()

'''
node_size=[math.log(float(G.degree(v)))*100 for v in G] 

nx.draw(G,pos=nx.spring_layout(G),node_size=node_size,with_labels=True)

#print G.degree('224419694612538')
plt.savefig("linkage200.png")
'''
