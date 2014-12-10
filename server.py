from urlparse import parse_qs
import json
from flask import Flask, request

from Entities.MyDatabase import MyDatabase
from Entities.Forum import do_method as do_forum_method
from Entities.Post import do_method as do_post_method
from Entities.User import do_method as do_user_method
from Entities.Thread import do_method as do_thread_method


def subd_server_app(path, request_body):
    path_list = path.split('/')

    if not path.startswith('/db/api/'):
        return json.dumps({"code": 3,
                           "response": "Url should be like \'/db/api/{{entity}}/{{method}}/\'"}, indent=4)

    if path_list[3].lower() == 'clear':
        db = MyDatabase()
        return db.clear()

    if len(path_list) < 5 or path_list[4] == '':
        return json.dumps({"code": 3, "response": "Too short url"}, indent=4)
    html_method = request_body.method
    db_method = path_list[4]

    qs = request_body.environ['QUERY_STRING']
    qs_dict = parse_qs(qs, True)

    if path_list[3].lower() == 'forum':
        return do_forum_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'post':
        return do_post_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'user':
        return do_user_method(db_method, html_method, request_body, qs_dict)
    elif path_list[3].lower() == 'thread':
        return do_thread_method(db_method, html_method, request_body, qs_dict)

    return json.dumps({"code": 3, "response": "Unknown entity"}, indent=4)


app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def do_dome_server(path):
    return subd_server_app(request.path, request)


if __name__ == "__main__":
    app.run(port=5000)
