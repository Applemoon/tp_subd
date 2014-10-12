import requests
import json

url = "http://localhost:8000/db/api/forum/create"
data = {"name": "Forum With Sufficiently Large Name 0", \
	"short_name": "forumwithsufficientlylargename 0", \
	"user": "user@mail.ru"}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)
print r