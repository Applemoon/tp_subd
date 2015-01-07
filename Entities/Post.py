import MySQLdb
from flask import Blueprint, request

from common import *

module = Blueprint('post', __name__, url_prefix='/db/api/post')


@module.route("/list/", methods=["GET"])
def list_method():
    qs = get_json(request)

    forum = qs.get('forum')
    thread = qs.get('thread')
    if not forum and not thread:
        return json.dumps({"code": 2, "response": "No 'forum' or 'thread' key"}, indent=4)

    since = qs.get('since', '')
    limit = qs.get('limit', -1)
    order = qs.get('order', '')

    if forum:
        post_list = get_post_list(forum=forum, since=since, limit=limit, order=order)
    else:
        post_list = get_post_list(thread=thread, since=since, limit=limit, order=order)

    return json.dumps({"code": 0, "response": post_list}, indent=4)


@module.route("/create/", methods=["POST"])
def create():
    request_body = request.json

    # Required
    date = request_body.get('date')
    thread = request_body.get('thread')
    message = try_encode(request_body.get('message'))
    user = request_body.get('user')
    forum = try_encode(request_body.get('forum'))

    # Optional
    parent = request_body.get('parent', None)
    if request_body.get('isApproved', False):
        is_approved = 1
    else:
        is_approved = 0

    if request_body.get('isHighlighted', False):
        is_highlighted = 1
    else:
        is_highlighted = 0

    if request_body.get('isEdited', False):
        is_edited = 1
    else:
        is_edited = 0

    if request_body.get('isSpam', False):
        is_spam = 1
    else:
        is_spam = 0

    if request_body.get('isDeleted', False):
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

    # post_list = list()
    # try:
    #     post_id = db.execute(sql, args, True)
    # except MySQLdb.IntegrityError, message:
    #     print message[0]
    #     post_list = get_post_list(user=user, date=date)
    # else:
    #     post_list = get_post_list(id_value=post_id)
    #     inc_posts_for_thread(thread)
    # finally:
    #     if not post_list:
    #         return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    #
    #     return json.dumps({"code": 0, "response": post_list[0]}, indent=4)

    post_id = db.execute(sql, args, True)
    post_list = get_post_list(id_value=post_id)
    inc_posts_for_thread(thread)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    return json.dumps({"code": 0, "response": post_list[0]}, indent=4)


@module.route("/details/", methods=["GET"])
def details():
    print "post/details"
    qs = get_json(request)

    post_id = qs.get('post')
    if not post_id:
        return json.dumps({"code": 2, "response": "No 'post' key"}, indent=4)

    post_list = get_post_list(id_value=post_id)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    else:
        post = post_list[0]

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


@module.route("/remove/", methods=["POST"])
def remove():
    return remove_method(True)


@module.route("/restore/", methods=["POST"])
def restore():
    return remove_method(False)


def remove_method(do_remove):
    request_body = request.json

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


@module.route("/update/", methods=["POST"])
def update():
    request_body = request.json
    post_id = request_body.get('post')
    message = try_encode(request_body.get('message'))

    sql = """UPDATE Post SET message = %(message)s WHERE post = %(post)s;"""

    args = {'message': message, 'post': post_id}
    db.execute(sql, args, True)

    post_list = get_post_list(id_value=post_id)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    return json.dumps({"code": 0, "response": post_list[0]}, indent=4)


@module.route("/vote/", methods=["POST"])
def vote():
    request_body = request.json

    post_id = request_body.get('post')
    vote_value = request_body.get('vote')

    if vote_value == 1:
        sql = """UPDATE Post SET likes = likes + 1, points = points + 1 WHERE post = %(post)s;"""
    elif vote_value == -1:
        sql = """UPDATE Post SET dislikes = dislikes + 1, points = points - 1 WHERE post = %(post)s;"""
    else:
        return json.dumps({"code": 3, "response": "Wrong 'vote' value'"}, indent=4)

    db.execute(sql, {'post': post_id}, True)

    post_list = get_post_list(id_value=post_id)
    if not post_list:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    return json.dumps({"code": 0, "response": post_list[0]}, indent=4)