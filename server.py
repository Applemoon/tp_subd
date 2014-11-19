from wsgiref.simple_server import make_server, demo_app
from urlparse import parse_qs
import json

from Entities.MyDatabase import MyDatabase
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

    if not path.startswith('/db/api/'):
        return [json.dumps({"code": 3,
                            "response": "Url should be like \'/db/api/{{entity}}/{{method}}/\'"}, indent=4)]

    if path_list[3].lower() == 'clear':
        db = MyDatabase()
        return db.clear()

    if len(path_list) < 5 or path_list[4] == '':
        return [json.dumps({"code": 3, "response": "Too short url"}, indent=4)]

    qs = environ['QUERY_STRING']
    qs_dict = parse_qs(qs, True)
    db_method = path_list[4]
    html_method = environ['REQUEST_METHOD']
    if path_list[3].lower() == 'forum':
        forum = Forum()
        return forum.do_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'post':
        post = Post()
        return post.do_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'user':
        user = User()
        return user.do_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'thread':
        thread = Thread()
        return thread.do_method(db_method, html_method, request_body, qs_dict)

    return [json.dumps({"code": 3, "response": "Unknown entity"}, indent=4)]


port = 8000
httpd = make_server('', port, subd_server_app)
# httpd = make_server('', port, demo_app)
print 'Serving on port %s...' % port
httpd.serve_forever()
