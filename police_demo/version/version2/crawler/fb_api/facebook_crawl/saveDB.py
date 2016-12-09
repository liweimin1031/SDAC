import json
posts_file=open('police.json')
try:
	posts_data=posts_file.read()
finally:
	posts_file.close()
dict = json.loads(posts_data)
print type(dict)	
print len(dict)	
sample=[]
sample.append(dict[0])
sample.append(dict[1])

doc=json.dumps(sample)
file_object=open('sample.json','wb')
file_object.write(doc)
file_object.close()