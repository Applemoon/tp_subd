import requests
import json
import sys

url_base = "http://localhost:8080"

val = sys.argv[1]
if val == "forumcreate":
    url = url_base + "/db/api/forum/create"
    data = {"name": "Forum With Sufficiently Large Name 3",
            "short_name": "forumwithsufficientlylargename 3",
            "user": "user@mail.ru"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r
elif val == "usercreate":
    url = url_base + "/db/api/user/create"
    data = {'username': None, 
            'about': None, 
            'isAnonymous': False, 
            'name': 'John2', 
            'email': 'example2@mail.ru'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r
elif val == "usercreatewrong":
    url = url_base + "/db/api/user/create"
    data = {'username': None, 
            'about': None, 
            'isAnonymous': False, 
            'name': u'\u0424\u043e\u0440\u0443\u043c \u0422\u0440\u0438', 
            'email': 'example2@mail.ru'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r
elif val == "postcreate":
    url = url_base + "/db/api/post/create"
    data = {"isApproved": True,
            "user": "example@mail.ru",
            "date": "2014-01-01 00:00:01",
            "message": "my message 1",
            "isSpam": False,
            "isHighlighted": True,
            "thread": 4,
            "forum": "forum2",
            "isDeleted": False,
            "isEdited": True}

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r
