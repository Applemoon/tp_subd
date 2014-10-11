from wsgiref.simple_server import make_server, demo_app
from urlparse import urlparse, parse_qs
import json

from Entities.Database import Database
from Entities.Forum import Forum
from Entities.Post import Post
from Entities.User import User
from Entities.Thread import Thread


def subd_server_app(environ, start_response):
	status = '200 OK'
	headers = [('Content-type', 'application/json')]
	start_response(status, headers)


	try:
		request_body_size = int(environ['CONTENT_LENGTH'])
		request_body = environ['wsgi.input'].read(request_body_size)
	except (TypeError, ValueError):
		request_body = "0"

	path = environ['PATH_INFO']
	path_list = path.split('/')

	# http://{{student_ip}}/db/api/{{entity}}/{{method}}/
	if not path.startswith('/db/api/'):
		return ['error: url should be like "/db/api/{{entity}}/{{method}}/"']

	if len(path_list) < 5:
		return ['too short url']
	if path_list[4] == '':
		return ['too short url']

	qs = environ['QUERY_STRING']
	qs_dict = parse_qs(qs, True);
	db_method = path_list[4]
	html_method  = environ['REQUEST_METHOD']
	if path_list[3].lower() == 'forum':
		forum = Forum()
		return forum.doMethod(db_method, html_method, request_body, qs_dict)
	elif path_list[3].lower() == 'post':
		post = Post()
		return post.doMethod(db_method, html_method, request_body, qs_dict)
	elif path_list[3].lower() == 'user':
		user = User()
		return user.doMethod(db_method, html_method, request_body, qs_dict)
	elif path_list[3].lower() == 'thread':
		thread = Thread()
		return thread.doMethod(db_method, html_method, request_body, qs_dict)
	elif path_list[3].lower() == 's.stupnikov' and path_list[4].lower() == 'clear':
		db = Database()
		return db.clear()
	else:
		return ['unknown entity']

	return ['error: 0']


port = 8000
httpd = make_server('', port, subd_server_app)
# httpd = make_server('', port, demo_app)
print 'Serving on port %s...' % port
httpd.serve_forever()
