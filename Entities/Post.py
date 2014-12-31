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
    elif db_method == 'restore':
        return restore(html_method, request_body)
    elif db_method == 'update':
        return update(html_method, request_body)
    elif db_method == 'vote':
        return vote(html_method, request_body)

    return json.dumps({"code": 3, "response": "Unknown post db method"}, indent=4)


def list_method(qs_dict):
    if not qs_dict.get('forum') and not qs_dict.get('thread'):
        return json.dumps({"code": 2, "response": "No 'forum' or 'thread' key"}, indent=4)

    since = ""
    if qs_dict.get('since'):
        since = qs_dict.get('since')[0]

    limit = -1
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]

    order = ""
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]

    if qs_dict.get('forum'):
        forum = qs_dict.get('forum')[0]
        post_list = get_post_list(forum=forum, since=since, limit=limit, order=order)
    else:
        thread = qs_dict.get('thread')[0]
        post_list = get_post_list(thread=thread, since=since, limit=limit, order=order)

    return json.dumps({"code": 0, "response": post_list}, indent=4)


def create(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'post.create'"}, indent=4)

    request_body = json.loads(request_body.data)

    # Required
    date = request_body.get('date')
    thread = request_body.get('thread')
    message = request_body.get('message')
    message = try_encode(message)
    user = request_body.get('user')
    forum = request_body.get('forum')
    forum = try_encode(forum)

    # Optional
    parent = request_body.get('parent', None)
    is_approved_key = request_body.get('isApproved', False)
    if is_approved_key:
        is_approved = 1
    else:
        is_approved = 0
    is_highlighted_key = request_body.get('isHighlighted', False)
    if is_highlighted_key:
        is_highlighted = 1
    else:
        is_highlighted = 0
    is_edited_key = request_body.get('isEdited', False)
    if is_edited_key:
        is_edited = 1
    else:
        is_edited = 0
    is_spam_key = request_body.get('isSpam', False)
    if is_spam_key:
        is_spam = 1
    else:
        is_spam = 0
    is_deleted_key = request_body.get('isDeleted', False)
    if is_deleted_key:
        is_deleted = 1
    else:
        is_deleted = 0

    sql = """INSERT INTO Post (user, thread, forum, message, parent, date, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved) VALUES \
        (%(user)s, %(thread)s, %(forum)s, %(message)s, %(parent)s, %(date)s, \
        %(isSpam)s, %(isEdited)s, %(isDeleted)s, %(isHighlighted)s, %(isApproved)s);"""
    args = {'user': user, 'thread': thread, 'forum': forum, 'message': message, 'parent': parent, 'date': date,
            'isSpam': is_spam, 'isEdited': is_edited, 'isDeleted': is_deleted, 'isHighlighted': is_highlighted,
            'isApproved': is_approved}

    db = MyDatabase()

    post_list = list()
    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        print message[0]
        post_list = get_post_list(user=user, date=date)
    else:
        post_list = get_post_list(id_value=db.cursor.lastrowid)
        inc_posts_for_thread(thread)
    finally:
        if post_list == list():
            return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
        if not post_list[0]:
            return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

        return json.dumps({"code": 0, "response": post_list[0]}, indent=4)


def details(qs_dict):
    if not qs_dict.get('post'):
        return json.dumps({"code": 2, "response": "No 'post' key"}, indent=4)

    post_id = qs_dict.get('post')[0]
    post_list = get_post_list(id_value=post_id)
    if post_list == list():
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    if not post_list[0]:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    else:
        post = post_list[0]

    thread_related = False
    forum_related = False
    user_related = False
    if qs_dict.get('related'):
        for related_value in qs_dict.get('related'):
            if related_value == 'forum':
                forum_related = True
            elif related_value == 'user':
                user_related = True
            elif related_value == 'thread':
                thread_related = True
            else:
                return json.dumps({"code": 3, "response": "Wrong related value"}, indent=4)

    if thread_related:
        thread_list = get_thread_list(id_value=post['thread'])
        if thread_list == list():
            post['thread'] = dict()
        else:
            post['thread'] = thread_list[0]

    if forum_related:
        post['forum'] = get_forum_dict(short_name=post['forum'])

    if user_related:
        post['user'] = get_user_dict(post['user'])

    return json.dumps({"code": 0, "response": post}, indent=4)


def remove(html_method, request_body, do_remove=True):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'post.remove/restore'"}, indent=4)

    request_body = json.loads(request_body.data)
    post_id = request_body.get('post')
    post = get_post_list(id_value=post_id)[0]
    thread_id = post['thread']

    if do_remove:
        remove_post(post_id)
        dec_posts_for_thread(thread_id)
    else:
        restore_post(post_id)
        inc_posts_for_thread(thread_id)

    return json.dumps({"code": 0, "response": {"post": post_id}}, indent=4)


def restore(html_method, request_body):
    return remove(html_method, request_body, False)


def update(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'post.update'"}, indent=4)

    request_body = json.loads(request_body.data)
    post_id = request_body.get('post')
    message = request_body.get('message')
    message = try_encode(message)

    sql = """UPDATE Post SET message = %(message)s WHERE post = %(post)s;"""

    db = MyDatabase()
    args = {'message': message, 'post': post_id}
    db.execute(sql, args, True)

    post_list = get_post_list(id_value=post_id)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    if not post_list[0]:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    return json.dumps({"code": 0, "response": post_list[0]}, indent=4)


def vote(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3, "response": "Wrong html method for 'post.vote'"}, indent=4)

    request_body = json.loads(request_body.data)
    post_id = request_body.get('post')
    vote_value = request_body.get('vote')
    if vote_value != 1 and vote_value != -1:
        return json.dumps({"code": 3, "response": "Wrong 'vote' value'"}, indent=4)

    if vote_value == 1:
        sql = """UPDATE Post SET likes = likes + 1, points = points + 1 WHERE post = %(post)s;"""
    else:
        sql = """UPDATE Post SET dislikes = dislikes + 1, points = points - 1 WHERE post = %(post)s;"""

    db = MyDatabase()
    db.execute(sql, {'post': post_id}, True)

    post_list = get_post_list(id_value=post_id)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    if not post_list[0]:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    return json.dumps({"code": 0, "response": post_list[0]}, indent=4)