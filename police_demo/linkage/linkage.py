import networkx as nx
import time
def getLinkage(data):
    start_time=time.time()
    G=nx.DiGraph()
    localEdges=data['localEdges']
    links=[{ 'source':localEdge[0] ,'target': localEdge[1] } for localEdge in localEdges ]
    linkage={}
    nodes=[]

    G.add_edges_from(localEdges)

    pr=nx.pagerank(G)
    sum_node=len(pr)

    for temp in pr:
        name=temp
        v=pr[name]
        #value=math.log(v*500+1)*100
        nodes.append({'name':name,'value':v})
    nodes.sort(key=lambda x:x['value'], reverse=True)
    top_nodes=nodes[:100]

    name=[ node['name'] for node in top_nodes ]

    sum_links=len(links)
    new_links=[ link  for link in links if((link['source'] in name) and (link['target'] in name))]


    linkage['nodes']=top_nodes
    linkage['links']=new_links
    linkage['info']={'nodes':sum_node,'links':sum_links}
    end_time=time.time()
    cost_time=end_time-start_time
    print 'linkage cost: %d'%cost_time
    return linkage