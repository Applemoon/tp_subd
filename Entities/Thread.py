import MySQLdb
from common import *


def do_method(db_method, html_method, request_body, qs_dict):
    if db_method == 'list':
        return list_method(qs_dict)
    elif db_method == 'create':
        return create(html_method, request_body)
    elif db_method == 'details':
        return details(qs_dict)
    elif db_method == 'remove':
        return remove(html_method, request_body)
    elif db_method == 'open':
        return open_method(html_method, request_body)
    elif db_method == 'close':
        return close(html_method, request_body)
    elif db_method == 'restore':
        return restore(html_method, request_body)
    elif db_method == 'listPosts':
        return list_posts(qs_dict)
    elif db_method == 'update':
        return update(html_method, request_body)
    elif db_method == 'subscribe':
        return subscribe(html_method, request_body)
    elif db_method == 'unsubscribe':
        return unsubscribe(html_method, request_body)
    elif db_method == 'vote':
        return vote(html_method, request_body)

    return json.dumps({"code": 3, "response": "Unknown thread db method"}, indent=4)


def list_method(qs_dict):
    if qs_dict.get('forum'):
        key = "forum"
    elif qs_dict.get('user'):
        key = "user"
    else:
        return json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)
    key_value = qs_dict.get(key)[0]

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
    if key == "forum":
        thread_list = get_thread_list(forum=key_value, since=since, order=order, limit=limit)
    else:
        thread_list = get_thread_list(user=key_value, since=since, order=order, limit=limit)

    return json.dumps({"code": 0, "response": thread_list}, indent=4)


def create(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.create'"}, indent=4)

    request_body = json.loads(request_body.data)

    # Required
    forum = request_body.get('forum')
    forum = try_encode(forum)
    title = request_body.get('title')
    title = try_encode(title)
    is_closed_key = request_body.get('isClosed')
    is_closed = 0
    if is_closed_key:
        is_closed = 1
    user = request_body.get('user')
    date = request_body.get('date')
    message = request_body.get('message')
    message = try_encode(message)
    slug = request_body.get('slug')
    slug = try_encode(slug)

    # Optional
    is_deleted_key = request_body.get('isDeleted', False)
    is_deleted = 0
    if is_deleted_key:
        is_deleted = 1

    sql = """INSERT INTO Thread (forum, title, isClosed, user, date, message, slug, isDeleted) \
        VALUES (%(forum)s, %(title)s, %(isClosed)s, %(user)s, %(date)s, %(message)s, %(slug)s, %(isDeleted)s);"""
    args = {'forum': forum, 'title': title, 'isClosed': is_closed, 'user': user, 'date': date, 'message': message,
            'slug': slug, 'isDeleted': is_deleted}
    db = MyDatabase()

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        print message[0]
    finally:
        thread_list = get_thread_list(title=title)
        if thread_list == list():
            return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

        return json.dumps({"code": 0, "response": thread_list[0]}, indent=4)


def details(qs_dict):
    if not qs_dict.get('thread'):
        return json.dumps({"code": 2, "response": "No 'thread' key"}, indent=4)

    thread_id = qs_dict.get('thread')[0]
    thread_list = get_thread_list(id_value=thread_id)
    if thread_list == list():
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    thread = thread_list[0]

    forum_related = False
    user_related = False
    if qs_dict.get('related'):
        for related_value in qs_dict.get('related'):
            if related_value == 'forum':
                forum_related = True
            elif related_value == 'user':
                user_related = True
            else:
                return json.dumps({"code": 3, "response": "Wrong related value"},
                                  indent=4)

    if forum_related:
        thread['forum'] = get_forum_dict(short_name=thread['forum'])

    if user_related:
        thread['user'] = get_user_dict(thread['user'])

    return json.dumps({"code": 0, "response": thread}, indent=4)


def remove(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'thread.remove'"}, indent=4)

    request_body = json.loads(request_body.data)

    thread = request_body.get('thread')
    sql = """UPDATE Thread SET isDeleted = 1, posts = 0 WHERE thread = %(thread)s;"""
    post_list = get_post_list(thread=thread)
    for post in post_list:
        remove_post(post['id'])
    db = MyDatabase()
    db.execute(sql, {'thread': thread}, True)

    return json.dumps({"code": 0, "response": thread}, indent=4)


def open_method(html_method, request_body, close_value=False):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.open'"}, indent=4)

    request_body = json.loads(request_body.data)

    thread = request_body.get('thread')
    if not close_value:
        sql = """UPDATE Thread SET isClosed = 0 WHERE thread = %(thread)s;"""
    else:
        sql = """UPDATE Thread SET isClosed = 1 WHERE thread = %(thread)s;"""

    db = MyDatabase()
    db.execute(sql, {'thread': thread}, True)

    return json.dumps({"code": 0, "response": thread}, indent=4)


def close(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.close'"}, indent=4)

    return open_method(html_method, request_body, True)


def restore(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.restore'"}, indent=4)

    request_body = json.loads(request_body.data)

    thread = request_body.get('thread')

    post_list = get_post_list(thread=thread)
    for post in post_list:
        restore_post(post['id'])

    sql = """UPDATE Thread SET isDeleted = 0, posts = %(posts)s WHERE thread = %(thread)s;"""
    args = {'posts': len(post_list), 'thread': thread}
    db = MyDatabase()
    db.execute(sql, args, True)

    return json.dumps({"code": 0, "response": thread}, indent=4)


def list_posts(qs_dict):
    thread = qs_dict.get('thread')[0]

    since = ""
    if qs_dict.get('since', ''):
        since = qs_dict.get('since')[0]

    limit = -1
    if qs_dict.get('limit', ''):
        limit = qs_dict.get('limit')[0]

    order = 'desc'
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]

    sort = 'flat'
    if qs_dict.get('sort'):
        sort = qs_dict.get('sort')[0]

    post_list = get_post_list(thread=thread, since=since, limit=limit, sort=sort, order=order)

    return json.dumps({"code": 0, "response": post_list}, indent=4)


def update(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.update'"}, indent=4)

    request_body = json.loads(request_body.data)

    message = request_body.get('message')
    message = try_encode(message)
    slug = request_body.get('slug')
    thread = request_body.get('thread')

    sql = """UPDATE Thread SET message = %(message)s, slug = %(slug)s WHERE thread = %(thread)s;"""
    args = {'message': message, 'slug': slug, 'thread': thread}
    db = MyDatabase()
    db.execute(sql, args, True)
    thread_list = get_thread_list(id_value=thread)
    if thread_list != list():
        thread_dict = thread_list[0]
    else:
        thread_dict = dict()

    return json.dumps({"code": 0, "response": thread_dict}, indent=4)


def subscribe(html_method, request_body, unsubscribe_value=False):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'thread.subscribe/unsubscribe'"}, indent=4)

    request_body = json.loads(request_body.data)

    user = request_body.get('user')
    thread = request_body.get('thread')
    if not unsubscribe_value:
        sql = """INSERT INTO Subscription (subscriber, thread) VALUES (%(subscriber)s, %(thread)s);"""
    else:
        sql = """DELETE FROM Subscription WHERE subscriber = %(subscriber)s AND thread = %(thread)s;"""

    args = {'subscriber': user, 'thread': thread}
    db = MyDatabase()
    db.execute(sql, args, True)
    result_dict = dict()
    result_dict['thread'] = thread
    result_dict['user'] = str_to_json(user)

    return json.dumps({"code": 0, "response": result_dict}, indent=4)


def unsubscribe(html_method, request_body):
    return subscribe(html_method, request_body, True)


def vote(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'thread.vote'"}, indent=4)

    request_body = json.loads(request_body.data)

    vote_value = request_body.get('vote')
    thread = request_body.get('thread')

    if vote_value == 1:
        sql = """UPDATE Thread SET likes = likes + 1, points = points + 1 WHERE thread = %(thread)s;"""
    else:
        sql = """UPDATE Thread SET dislikes = dislikes + 1, points = points - 1 WHERE thread = %(thread)s;"""

    db = MyDatabase()
    db.execute(sql, {'thread': thread}, True)

    thread_dict = dict()
    thread_list = get_thread_list(id_value=thread)
    if thread_list != list():
        thread_dict = thread_list[0]

    return json.dumps({"code": 0, "response": thread_dict}, indent=4)
