import MySQLdb

from common import *


def do_method(db_method, html_method, request_body, qs_dict):
    if db_method == 'create':
        return create(html_method, request_body)
    elif db_method == 'details':
        return details(qs_dict)
    elif db_method == 'listPosts':
        return list_posts(qs_dict)
    elif db_method == 'listThreads':
        return list_threads(qs_dict)
    elif db_method == 'listUsers':
        return list_users(qs_dict)

    return json.dumps({"code": 3, "response": "Unknown forum db method"}, indent=4)


def create(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'forum.create'"}, indent=4)

    request_body = json.loads(request_body.data)

    name = request_body.get('name')
    name = try_encode(name)
    short_name = request_body.get('short_name')
    short_name = try_encode(short_name)
    user = request_body.get('user')
    sql = """INSERT INTO Forum (name, short_name, user) VALUES (%s, %s, %s);"""
    args = (name, short_name, user)
    db = MyDatabase()

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        print message[0]
    finally:
        forum_dict = get_forum_dict(short_name=short_name)
        return json.dumps({"code": 0, "response": forum_dict}, indent=4)


def details(qs_dict):
    if not qs_dict.get('forum'):
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    short_name = qs_dict.get('forum')[0]
    forum_dict = get_forum_dict(short_name=short_name)
    if forum_dict == dict():
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    if qs_dict.get('related') and qs_dict.get('related')[0] == 'user':
        user = get_user_dict(forum_dict['user'])
        user['followers'] = get_followers_list(user['email'])
        user['following'] = get_following_list(user['email'])
        user['subscriptions'] = get_subscribed_threads_list(user['email'])

        forum_dict['user'] = user

    return json.dumps({"code": 0, "response": forum_dict}, indent=4)


def list_posts(qs_dict):
    if not qs_dict.get('forum'):
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    forum = qs_dict.get('forum')[0]
    forum = try_encode(forum)

    # Related part
    thread_related = False
    forum_related = False
    user_related = False
    if qs_dict.get('related'):
        for related_value in qs_dict.get('related'):
            if related_value == 'thread':
                thread_related = True
            elif related_value == 'forum':
                forum_related = True
            elif related_value == 'user':
                user_related = True
            else:
                return json.dumps({"code": 3, "response": "Wrong related value"}, indent=4)

    since = ""
    if qs_dict.get('since'):
        since = qs_dict.get('since')[0]

    limit = -1
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]

    sort = "flat"
    if qs_dict.get('sort'):
        sort = qs_dict.get('sort')[0]

    order = "desc"
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]

    post_list = get_post_list(forum=forum, since=since, limit=limit, sort=sort, order=order)

    for post in post_list:
        if user_related:
            post['user'] = get_user_dict(post['user'])

        if thread_related:
            post['thread'] = get_thread_list(id_value=post['thread'])[0]

        if forum_related:
            post['forum'] = get_forum_dict(short_name=post['forum'])

    return json.dumps({"code": 0, "response": post_list}, indent=4)


def list_threads(qs_dict):
    if not qs_dict.get('forum'):
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    forum = qs_dict.get('forum')[0]

    # Since part
    since = ""
    if qs_dict.get('since'):
        since = qs_dict.get('since')[0]

    # Order part
    order = ""
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]

    # Limit part
    limit = -1
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]
    thread_list = get_thread_list(forum=forum, since=since, order=order, limit=limit)

    # Related part
    forum_related = False
    user_related = False
    if qs_dict.get('related'):
        for related_value in qs_dict.get('related'):
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


def list_users(qs_dict):
    if not qs_dict.get('forum'):
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)

    # Since id part
    since_id_sql = ''
    if qs_dict.get('since_id'):
        since_id = qs_dict.get('since_id')[0]
        try:
            since_id = int(since_id)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong since_id value"}, indent=4)
        since_id_sql = """AND User.user >= {}""".format(since_id)

    # Limit part
    limit_sql = ''
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]
        try:
            limit = int(limit)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        if limit < 0:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        limit_sql = """LIMIT {}""".format(limit)

    # Order part
    order = 'desc'
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]
        if order != 'asc' and order != 'desc':
            return json.dumps({"code": 3, "response": "Wrong order value"}, indent=4)
    order_sql = """ORDER BY User.name {}""".format(order)

    sql = """SELECT User.user, User.email, User.name, User.username, User.isAnonymous, User.about FROM User \
        JOIN Post ON Post.user = User.email \
        WHERE Post.forum = %s {snc_sql} GROUP BY User.user {ord_sql} {lim_sql};""".format(
        snc_sql=since_id_sql, lim_sql=limit_sql, ord_sql=order_sql)

    db = MyDatabase()
    user_list_sql = db.execute(sql, qs_dict.get('forum'))

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
