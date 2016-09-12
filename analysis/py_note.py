

    
'''
#--Text Rank--#
print('-'*40)
print(' TextRank ')
print('-'*40)
term=jieba.analyse.textrank(text_analyse, topK=20, withWeight=True)
for x, w  in term:
    print('%s %s' % (x, w))

'''

'''
#-- jieba cut with word flag--#
words = pseg.cut(cText)
nword = []
i=0
for w in words: 
    if((w.flag == 'n'or w.flag == 'v' or w.flag == 'a') and len(w.word)>1): 
        nword.append(w.word)
        #i+=1
        #print i
'''
'''
print('-'*40)
n_key_words=[]
v_key_words=[]

print('-'*40)
print(' TF-IDF')
print('-'*40)
for x, w in jieba.analyse.extract_tags(cText, topK=15,withWeight=True,allowPOS= ('n' )):
    print('%s %s' % (x, w))
    n_key_words.append(x)

print('-'*40)
for x, w in jieba.analyse.extract_tags(cText, topK=15,withWeight=True,allowPOS= ('v','vn','a','ad')):
    print('%s %s' % (x, w))
    v_key_words.append(x)
'''
'''
print('-'*40)
print(' TextRank with freq')
print('-'*40)
#c = Counter(seg_list)

term=jieba.analyse.textrank(text, topK=10, withWeight=True,allowPOS= ('n'))
for x, w  in term:
    print('%s %s' % (x, w))
    
print('-'*40)

a_term=jieba.analyse.textrank(text, topK=10, withWeight=True,allowPOS= ('a','d','v'))
for x, w  in a_term:
    print('%s %s' % (x, w))
'''
'''
topic_list=[]
for x,w in term:
    for i,y in a_term:
        topic=    w+y
        scort=abs(int(str(x))-int(str(i)))
        topic_tuple=(topic,scort)
        topic_list.append(topic_tuple)
print('-'*40)
print topic_list
freq=OrderedDict(sorted(topic_list,key=lambda t: t[1],reverse=True))
print('-'*40)
print freq
for x, w in freq.items():
    print('%s %s' % (x.encode('gb18030'), w))
'''
'''
print('-'*40)
print(' topic span')
print('-'*40)
span=2
for title in text:
    title_cut = jieba.cut(title, cut_all=False)
    title_cut = list(title_cut)
    for key_word in n_key_words:        
        key_index=[i for i, x in enumerate(title_cut) if x == key_word]
        for i in key_index:
            if i<=span :
                _topic=title_cut[0:(i+span+1)]
            if i>span :
                _topic=title_cut[(i-span):(i+span+1)]
            print ''.join(_topic)

print('-'*40)
'''
'''
A=n_key_words
B=v_key_words
title_list=text
print len(title_list)
def PA(n,m):
    topics=[]
    for x in n:
        for y in m:
            _a=0
            _ab=0
            P=0
            #print 'x:%s, y:%s' %(x,y)
            for title in title_list:
                #print title_list.index(title)
                if x in title:
                    _a=_a+1.0
                if (x in title) and (y in title):
                    _ab=_ab+1.0
            if _a!=0 and _ab!=0:
                #print _a
                #print _ab
                P=_ab/_a
                topic=(P,x+y)
                print 'topic:%s P:%f'%(x+y,P)
                #topics.append(topic)
                #print topics
PA(A, B)

'''

'''
print('-'*40)
print(' word freq')
print('-'*40)
c = Counter(seg_list)
    
freq=OrderedDict(sorted(c.items(),key=lambda t: t[1],reverse=True))
for x, w in freq.items():
    print('%s %s' % (x.encode('gb18030'), w))
'''