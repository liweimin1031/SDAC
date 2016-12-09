import requests

url = 'http://www.facebook.com/login.php'
#url='https://www.facebook.com/dialog/oauth?'
app_id='611406969009887'
redirect_uri='https://www.facebook.com/connect/login_success.html'
email='liweimin1031@gmail.com'
pw='Other1031'
data={'email':email,'pass':pw}
'''url='https://graph.facebook.com/v2.3/oauth/access_token?'
app_id='611406969009887'
redirect_uri='https://www.facebook.com/connect/login_success.html'
app_secret='6be22272c73f9a90f8ded333fbb0ff4d'
code_parameter=''
data={'client_id':app_id,'redirect_uri':redirect_uri,'client_secret':app_secret,'code':code_parameter}
'''
r=requests.get(url,data=data)
print r.headers