import MySQLdb
from flask import Blueprint, request

from common import *

module = Blueprint('forum', __name__, url_prefix='/db/api/forum')


@module.route("/create/", methods=["POST"])
def create():
    request_body = request.json

    name = request_body.get('name')
    short_name = try_encode(request_body.get('short_name'))
    user = request_body.get('user')
    sql = """INSERT INTO Forum (name, short_name, user) VALUES (%(name)s, %(short_name)s, %(user)s);"""
    args = {'name': name, 'short_name': short_name, 'user': user}

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        print message[0]
    finally:
        forum_dict = get_forum_dict(short_name=short_name)
        return json.dumps({"code": 0, "response": forum_dict}, indent=4)


@module.route("/details/", methods=["GET"])
def details():
    qs = get_json(request)
    short_name = qs.get('forum')

    if not short_name:
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    forum_dict = get_forum_dict(short_name=short_name)
    if not forum_dict:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    if qs.get('related', '') == 'user':
        user = get_user_dict(forum_dict['user'])
        user['followers'] = get_followers_list(user['email'])
        user['following'] = get_following_list(user['email'])
        user['subscriptions'] = get_subscribed_threads_list(user['email'])

        forum_dict['user'] = user

    return json.dumps({"code": 0, "response": forum_dict}, indent=4)


@module.route("/listPosts/", methods=["GET"])
def list_posts():
    qs = get_json(request)

    forum = qs.get('forum')

    if not forum:
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    forum = try_encode(forum)

    # Related part
    related_values = list()
    qs_related = qs.get('related')
    if type(qs_related) is list:
        related_values.extend(qs_related)
    elif type(qs_related) is str:
        related_values.append(qs_related)

    thread_related = False
    forum_related = False
    user_related = False
    for related_value in related_values:
        if related_value == 'thread':
            thread_related = True
        elif related_value == 'forum':
            forum_related = True
        elif related_value == 'user':
            user_related = True
        else:
            return json.dumps({"code": 3, "response": "Wrong related value"}, indent=4)

    since = qs.get('since', '')
    limit = qs.get('limit', -1)
    sort = qs.get('sort', 'flat')
    order = qs.get('order', 'desc')

    post_list = get_post_list(forum=forum, since=since, limit=limit, sort=sort, order=order)

    for post in post_list:
        if user_related:
            post['user'] = get_user_dict(post['user'])

        if thread_related:
            post['thread'] = get_thread_list(id_value=post['thread'])[0]

        if forum_related:
            post['forum'] = get_forum_dict(short_name=post['forum'])

    return json.dumps({"code": 0, "response": post_list}, indent=4)


@module.route("/listThreads/", methods=["GET"])
def list_threads():
    qs = get_json(request)

    forum = qs.get('forum')

    if not forum:
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    since = qs.get('since', '')
    order = qs.get('order', '')
    limit = qs.get('limit', -1)
    thread_list = get_thread_list(forum=forum, since=since, order=order, limit=limit)

    # Related part
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

    for thread in thread_list:
        if user_related:
            thread['user'] = get_user_dict(thread['user'])
            thread['user']['followers'] = get_followers_list(thread['user']['email'])
            thread['user']['following'] = get_following_list(thread['user']['email'])
            thread['user']['subscriptions'] = get_subscribed_threads_list(thread['user']['email'])

        if forum_related:
            thread['forum'] = get_forum_dict(short_name=thread['forum'])

    return json.dumps({"code": 0, "response": thread_list}, indent=4)


@module.route("/listUsers/", methods=["GET"])
def list_users():
    qs = get_json(request)

    if not qs.get('forum'):
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    # Since id part
    since_id = qs.get('since_id')
    if since_id:
        try:
            since_id = int(since_id)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong since_id value"}, indent=4)
        since_id_sql = """AND User.user >= {}""".format(since_id)
    else:
        since_id_sql = ''

    # Limit part
    if qs.get('limit'):
        limit = qs.get('limit')[0]
        try:
            limit = int(limit)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        if limit < 0:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        limit_sql = """LIMIT {}""".format(limit)
    else:
        limit_sql = ''

    # Order part
    order = qs.get('order', 'desc')
    order_sql = """ORDER BY User.name {}""".format(order)

    sql = """SELECT User.user, User.email, User.name, User.username, User.isAnonymous, User.about FROM User \
        JOIN Post ON Post.user = User.email \
        WHERE Post.forum = %(forum)s {snc_sql} GROUP BY User.user {ord_sql} {lim_sql};""".format(
        snc_sql=since_id_sql, lim_sql=limit_sql, ord_sql=order_sql)

    user_list_sql = db.execute(sql, {'forum': qs.get('forum')})

    user_list = list()
    for user_sql in user_list_sql:
        user = dict()
        user['id'] = str_to_json(user_sql[0])
        user['email'] = str_to_json(user_sql[1])
        user['name'] = str_to_json(user_sql[2])
        user['username'] = str_to_json(user_sql[3])
        user['isAnonymous'] = str_to_json(user_sql[4])
        user['about'] = str_to_json(user_sql[5])
        user['followers'] = get_followers_list(user['email'])
        user['following'] = get_following_list(user['email'])
        user['subscriptions'] = get_subscribed_threads_list(user['email'])

        user_list.append(user)

    return json.dumps({"code": 0, "response": user_list}, indent=4)
