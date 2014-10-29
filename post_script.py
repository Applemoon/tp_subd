import requests
import json
import sys

val = sys.argv[1]
if val == "forumcreate":
	url = "http://localhost:8000/db/api/forum/create"
	data = {"name": "Forum With Sufficiently Large Name 3", \
			"short_name": "forumwithsufficientlylargename 3", \
			"user": "user@mail.ru"}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	print r
elif val == "usercreate":
	url = "http://localhost:8000/db/api/user/create"
	data = {'username': None, 
			'about': None, 
			'isAnonymous': False, 
			'name': 'John2', 
			'email': 'example2@mail.ru'}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	print r
elif val == "usercreatewrong":
	url = "http://localhost:8000/db/api/user/create"
	data = {'username': None, 
			'about': None, 
			'isAnonymous': False, 
			'name': u'\u0424\u043e\u0440\u0443\u043c \u0422\u0440\u0438', 
			'email': 'example2@mail.ru'}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	print r
