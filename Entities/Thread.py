import json
import MySQLdb
from flask import Blueprint, request

from Entities.MyDatabase import db
from common import get_json, get_thread_list, try_encode, get_forum_dict, get_user_dict, get_post_list, remove_post, \
    restore_post, str_to_json, get_thread_by_id, MYSQL_DUPLICATE_ENTITY_ERROR

module = Blueprint('thread', __name__, url_prefix='/db/api/thread')


@module.route("/list/", methods=["GET"])
def list_method():
    qs = get_json(request)
    if qs.get('forum'):
        key = "forum"
    elif qs.get('user'):
        key = "user"
    else:
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)
    key_value = qs.get(key)

    since = qs.get('since', '')
    order = qs.get('order', '')
    limit = qs.get('limit', -1)

    if key == "forum":
        thread_list = get_thread_list(forum=key_value, since=since, order=order, limit=limit)
    else:
        thread_list = get_thread_list(user=key_value, since=since, order=order, limit=limit)

    return json.dumps({"code": 0, "response": thread_list}, indent=4)


@module.route("/create/", methods=["POST"])
def create():
    request_body = request.json

    # Required
    forum = request_body.get('forum')
    title = try_encode(request_body.get('title'))
    if request_body.get('isClosed'):
        is_closed = 1
    else:
        is_closed = 0
    user = request_body.get('user')
    date = request_body.get('date')
    message = request_body.get('message')
    slug = request_body.get('slug')

    # Optional
    if request_body.get('isDeleted', False):
        is_deleted = 1
    else:
        is_deleted = 0

    sql = """INSERT INTO Thread (forum, title, isClosed, user, date, message, slug, isDeleted) \
        VALUES (%(forum)s, %(title)s, %(isClosed)s, %(user)s, %(date)s, %(message)s, %(slug)s, %(isDeleted)s);"""
    args = {'forum': forum, 'title': title, 'isClosed': is_closed, 'user': user, 'date': date, 'message': message,
            'slug': slug, 'isDeleted': is_deleted}

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        print message[0]
    finally:
        thread_list = get_thread_list(title=title)
        if thread_list == list():
            return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

        return json.dumps({"code": 0, "response": thread_list[0]}, indent=4)


@module.route("/details/", methods=["GET"])
def details():
    qs = get_json(request)

    thread_id = qs.get('thread')
    if not thread_id:
        return json.dumps({"code": 2, "response": "No 'thread' key"}, indent=4)

    thread = get_thread_by_id(thread_id)
    if thread == list():
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    related_values = list()
    qs_related = qs.get('related')
    if type(qs_related) is list:
        related_values.extend(qs_related)
    elif type(qs_related) is str:
        related_values.append(qs_related)

    forum_related = False
    user_related = False
    for related_value in related_values:
        if related_value == 'forum':
            forum_related = True
        elif related_value == 'user':
            user_related = True
        else:
            return json.dumps({"code": 3, "response": "Wrong related value"}, indent=4)

    if forum_related:
        thread['forum'] = get_forum_dict(short_name=thread['forum'])

    if user_related:
        thread['user'] = get_user_dict(thread['user'])

    return json.dumps({"code": 0, "response": thread}, indent=4)


@module.route("/remove/", methods=["POST"])
def remove():
    request_body = request.json

    thread = request_body.get('thread')
    post_list = get_post_list(thread=thread)
    for post in post_list:
        remove_post(post['id'])

    db.execute("""UPDATE Thread SET isDeleted = 1, posts = 0 WHERE thread = %(thread)s;""", {'thread': thread}, True)

    return json.dumps({"code": 0, "response": thread}, indent=4)


@module.route("/open/", methods=["POST"])
def open_route():
    thread = request.json.get('thread')
    db.execute("""UPDATE Thread SET isClosed = 0 WHERE thread = %(thread)s;""", {'thread': thread}, True)
    return json.dumps({"code": 0, "response": thread}, indent=4)


@module.route("/close/", methods=["POST"])
def close_route():
    thread = request.json.get('thread')
    db.execute("""UPDATE Thread SET isClosed = 1 WHERE thread = %(thread)s;""", {'thread': thread}, True)
    return json.dumps({"code": 0, "response": thread}, indent=4)


@module.route("/restore/", methods=["POST"])
def restore():
    thread = request.json.get('thread')

    post_list = get_post_list(thread=thread)
    for post in post_list:
        restore_post(post['id'])

    db.execute("""UPDATE Thread SET isDeleted = 0, posts = %(posts)s WHERE thread = %(thread)s;""",
               {'posts': len(post_list), 'thread': thread}, True)

    return json.dumps({"code": 0, "response": thread}, indent=4)


@module.route("/listPosts/", methods=["GET"])
def list_posts():
    qs = get_json(request)

    thread = qs.get('thread')
    since = qs.get('since', '')
    limit = qs.get('limit', -1)
    order = qs.get('order', 'desc')
    sort = qs.get('sort', 'flat')

    post_list = get_post_list(thread=thread, since=since, limit=limit, sort=sort, order=order)

    return json.dumps({"code": 0, "response": post_list}, indent=4)


@module.route("/update/", methods=["POST"])
def update():
    request_body = request.json

    message = request_body.get('message')
    slug = request_body.get('slug')
    thread_id = request_body.get('thread')

    db.execute("""UPDATE Thread SET message = %(message)s, slug = %(slug)s WHERE thread = %(thread)s;""",
               {'message': message, 'slug': slug, 'thread': thread_id}, True)
    return json.dumps({"code": 0, "response": get_thread_by_id(thread_id)}, indent=4)


@module.route("/subscribe/", methods=["POST"])
def subscribe():
    return subscribe_method(False)


@module.route("/unsubscribe/", methods=["POST"])
def unsubscribe():
    return subscribe_method(True)


def subscribe_method(unsubscribe_value=False):
    request_body = request.json

    user = request_body.get('user')
    thread = request_body.get('thread')
    if not unsubscribe_value:
        try:
            db.execute("""INSERT INTO Subscription (subscriber, thread) VALUES (%(subscriber)s, %(thread)s);""",
                       {'subscriber': user, 'thread': thread}, True)
        except MySQLdb.IntegrityError, message:
            if message[0] == MYSQL_DUPLICATE_ENTITY_ERROR:
                print "Already subscribed"
    else:
        db.execute("""DELETE FROM Subscription WHERE subscriber = %(subscriber)s AND thread = %(thread)s;""",
                   {'subscriber': user, 'thread': thread}, True)

    result_dict = {'thread': thread, 'user': str_to_json(user)}
    return json.dumps({"code": 0, "response": result_dict}, indent=4)


@module.route("/vote/", methods=["POST"])
def vote():
    request_body = request.json

    vote_value = request_body.get('vote')
    thread_id = request_body.get('thread')

    if vote_value == 1:
        db.execute("""UPDATE Thread SET likes = likes + 1, points = points + 1 WHERE thread = %(thread)s;""",
                   {'thread': thread_id}, True)
    else:
        db.execute("""UPDATE Thread SET dislikes = dislikes + 1, points = points - 1 WHERE thread = %(thread)s;""",
                   {'thread': thread_id}, True)
    return json.dumps({"code": 0, "response": get_thread_by_id(thread_id)}, indent=4)
