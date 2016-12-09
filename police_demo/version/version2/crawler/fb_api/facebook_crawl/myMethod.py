
import json
import requests
import re
import httplib2
FACEBOOK_GRAPH_URL = 'https://graph.facebook.com/'
VALID_API_VERSIONS = ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6","2.7","2.8"]

requests.adapters.DEFAULT_RETRIES = 15

def getRequest(path,params):
    try:
        if params.has_key("access_token"):
            response = requests.request("GET", path,params=params)
        else:
            response = requests.request("GET", path)
    except requests.HTTPError as e:
        print  response
        print 'url:%s'%path
        #raise GraphAPIError(response)
    headers=response.headers
    if 'json' in headers['content-type']:
        result = response.json()
    elif "access_token" in parse_qs(response.text):
        query_str = parse_qs(response.text)
        if "access_token" in query_str:
            result = {"access_token": query_str["access_token"][0]}
            if "expires" in query_str:
                result["expires"] = query_str["expires"][0]
        else:
            print response.json() #test
            #raise GraphAPIError(response.json())
    else:
        print 'Maintype was not text, image, or querystring' #test
        #raise GraphAPIError('Maintype was not text, image, or querystring')

    if result and isinstance(result, dict) and result.get("error"):
        print result #test
        #raise GraphAPIError(result)
    return result
        
def getUrl(url):
    if '\\' in url:
        url=eval('u'+"'"+url+"'")
        url=url.replace('\\','')
    #url=url.lstrip('https://')
    return url

class fbAPI(object):
    def __init__(self,access_token=None,version=None):
        default_version = "2.8"
        self.access_token=access_token
        if version:
            version_regex = re.compile("^\d\.\d$")
            match = version_regex.search(str(version))
            if match is not None:
                if str(version) not in VALID_API_VERSIONS:
                    print "Valid API versions are " + str(VALID_API_VERSIONS).strip('[]')
                else:
                    self.version = "v" + str(version)
            else:
                print ("Version number should be in the"" following format: #.# (e.g. 2.0).")
        else:
            self.version = "v" + default_version
    

        
    def getFBRequest(self,id, **args ):
        path=FACEBOOK_GRAPH_URL+self.version+'/'+id
        args = args or {}
        #-----access_token-----#
        args["access_token"] = self.access_token
            #-----requests-----#
        result=getRequest(path,params=args)
        return result
        '''
        try:
            response = requests.request("GET", path,params=args)
        except requests.HTTPError as e:
            print  response
            #raise GraphAPIError(response)
        headers=response.headers
        if 'json' in headers['content-type']:
            result = response.json()
        elif "access_token" in parse_qs(response.text):
            query_str = parse_qs(response.text)
            if "access_token" in query_str:
                result = {"access_token": query_str["access_token"][0]}
                if "expires" in query_str:
                    result["expires"] = query_str["expires"][0]
            else:
                print response.json() #test
                #raise GraphAPIError(response.json())
        else:
            print 'Maintype was not text, image, or querystring' #test
            #raise GraphAPIError('Maintype was not text, image, or querystring')

        if result and isinstance(result, dict) and result.get("error"):
            print result #test
            #raise GraphAPIError(result)
        print 'result'
        print result
        return result
        '''


def nextData(url,data):
    data_list=data

    #h = httplib2.Http()
    #resp,content = h.request(url)
    params={}
    content=getRequest(path=url,params=params)
    #dict=eval(content)

    if content.has_key('error'):
        print content
        return data_list
    if not content['data']:
        print 'data is empty'
        return data_list
    data_list.extend(content['data'])
    if content['paging'].has_key('next'):
        print 'next'
        url=getUrl(content['paging']['next'])

        return nextData(url,data_list)
    else:

        return data_list
        
'''
    def getUrl(url):
        if '\\' in url:
            url=eval('u'+"'"+url+"'")
            url=url.replace('\\','')
        return url

    def nextData(url,data):
        data_list=data
        conn=httplib.HTTPSConnection(url)
        conn.request("GET", "/")
        response = conn.getresponse()
        data = response.read()
        dict=eval(response.read())
        
        #response=requests.get(url)
        #dict=eval(response.text)
        
        if dict['error']:
            print dict['error']
            return data_list
        if not dict['data']:
            print 'dict is empty'
            return data_list
        data_list.extend(dict['data'])
        if dict['paging'].has_key('next'):
            print 'next'
            url=getUrl(dict['paging']['next'])
            #print url
            #print len(data_list)
            return nextData(url,data_list)
        else:
            #print data_list
            #print '\n function end and total items: '+str(len(data_list))+'\n'
            return data_list
'''