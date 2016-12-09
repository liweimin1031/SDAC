# -*- coding: gb18030 -*-
import json

file_object=open('police_content_cn_140.json')

try:
	text=file_object.read()
finally:
	file_object.close()
	
#object_list = text
object_list = json.loads(text)
print len(object_list)

An error occurred while installing the items
session context was:(profile=epp.package.java, phase=org.eclipse.equinox.internal.p2.engine.phases.Install, operand=null --> [R]org.eclipse.rcp.configuration_root.win32.win32.x86_64 1.0.3.v20150204-1745, action=org.eclipse.equinox.internal.p2.touchpoint.natives.actions.ChmodAction).
The action chmod failed - file C:\Eclipse-IDE\eclipse\eclipse.exe does not exist

'''

for i in range(len(object_list)):
	print i
	comments=object_list[i]['comments']
	for j in range(len(comments)):
		if comments[j].has_key('likes'):
			comments[j]['likes']=comments[j]['likes']['data']
		if comments[j].has_key('comments'):
			reply_comments=comments[j]['comments']['data']
			comments[j]['comments']=reply_comments
			for k in range(len(reply_comments)):
				if reply_comments[k].has_key('likes'):
					comments[j]['comments'][k]['likes']=reply_comments[k]['likes']['data']
	object_list[i]['comments']=comments
'''

def save_file(file_name,file_data):
	doc=json.dumps(file_data)
	file=open(file_name,'wb')
	file.write(doc)
