import json
import urlparse

from Entities.MyDatabase import db


MYSQL_DUPLICATE_ENTITY_ERROR = 1062


def str_to_json(value, is_bool=False):
    if is_bool:
        return value != 0

    if value == "NULL":
        return None

    return value


def try_encode(value):
    if value is not None:
        return value.encode('utf-8')

    return value


def get_forum_dict(short_name):
    sql = """SELECT forum, name, short_name, user FROM Forum WHERE short_name = %(short_name)s LIMIT 1;"""
    forum_sql = db.execute(sql, {'short_name': short_name})
    if not forum_sql:
        return dict()

    forum_sql = forum_sql[0]
    return {'id': str_to_json(forum_sql[0]),
            'name': str_to_json(forum_sql[1]),
            'short_name': str_to_json(forum_sql[2]),
            'user': str_to_json(forum_sql[3])}


def get_post_list(user="", forum="", thread="", since="", limit=-1, sort='flat', order='desc'):
    # WHERE part
    if forum != "":
        where_sql = "forum = '{}'".format(forum)
    elif thread != "":
        where_sql = "thread = {}".format(thread)
    elif user != "":
        where_sql = "user = '{}'".format(user)
    else:
        print "Can't find search field in getPostList"
        return list()

    # since part
    since_sql = ""
    if since != "":
        since_sql = """AND date >= '{}'""".format(since)

    # sort part TODO
    if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
        print "Wrong sort value"
        return list()
    # sort_sql = """ORDER BY Post.date {}""".format(sort)
    sort_sql = """"""

    # limit part
    limit_sql = ""
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            print "Wrong limit value"
            return list()
        if limit < 0:
            print "Wrong limit value"
            return list()
        limit_sql = """LIMIT {}""".format(limit)

    # order part
    if order != 'asc' and order != 'desc':
        return json.dumps({"code": 3, "response": "Wrong order value"}, indent=4)
    order_sql = """ORDER BY date {}""".format(order)

    sql = """SELECT post, user, thread, forum, message, parent, date, likes, dislikes, points, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
        WHERE {where_value} {since_value} {order_value} {sort_value} {limit_value};""".format(
        where_value=where_sql,
        since_value=since_sql,
        limit_value=limit_sql,
        order_value=order_sql,
        sort_value=sort_sql)

    post_list_sql = db.execute(sql)
    if not post_list_sql:
        return list()

    post_list = list()
    for post_sql in post_list_sql:
        post_list.append({'id': str_to_json(post_sql[0]),
                          'user': str_to_json(post_sql[1]),
                          'thread': str_to_json(post_sql[2]),
                          'forum': str_to_json(post_sql[3]),
                          'message': str_to_json(post_sql[4]),
                          'parent': str_to_json(post_sql[5]),
                          'date': post_sql[6].strftime('%Y-%m-%d %H:%M:%S'),
                          'likes': str_to_json(post_sql[7]),
                          'dislikes': str_to_json(post_sql[8]),
                          'points': str_to_json(post_sql[9]),
                          'isSpam': str_to_json(post_sql[10], True),
                          'isEdited': str_to_json(post_sql[11], True),
                          'isDeleted': str_to_json(post_sql[12], True),
                          'isHighlighted': str_to_json(post_sql[13], True),
                          'isApproved': str_to_json(post_sql[14], True)})

    return post_list


def get_post_by_id(id_value):
    where_sql = "post = {}".format(id_value)

    sql = """SELECT post, user, thread, forum, message, parent, date, likes, dislikes, points, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
        WHERE post = %(id)s LIMIT 1;""".format(where_value=where_sql)

    post_list_sql = db.execute(sql, {'id': id_value})
    if not post_list_sql:
        return list()

    post_sql = post_list_sql[0]
    return {'id': str_to_json(post_sql[0]),
            'user': str_to_json(post_sql[1]),
            'thread': str_to_json(post_sql[2]),
            'forum': str_to_json(post_sql[3]),
            'message': str_to_json(post_sql[4]),
            'parent': str_to_json(post_sql[5]),
            'date': post_sql[6].strftime('%Y-%m-%d %H:%M:%S'),
            'likes': str_to_json(post_sql[7]),
            'dislikes': str_to_json(post_sql[8]),
            'points': str_to_json(post_sql[9]),
            'isSpam': str_to_json(post_sql[10], True),
            'isEdited': str_to_json(post_sql[11], True),
            'isDeleted': str_to_json(post_sql[12], True),
            'isHighlighted': str_to_json(post_sql[13], True),
            'isApproved': str_to_json(post_sql[14], True)}


def get_thread_list(title="", forum="", user="", since="", limit=-1, order="desc"):
    if title != "":
        where_sql = "title = '{}'".format(title)
    elif forum != "":
        where_sql = "forum = '{}'".format(forum)
    elif user != "":
        where_sql = "user = '{}'".format(user)
    else:
        print "Can't find search field in getThreadList"
        return list()

    # Since part
    since_sql = ""
    if since != "":
        since_sql = """ AND date >= '{}'""".format(since)

    # Order part
    if order != 'asc' and order != 'desc':
        print "Wrong order value"
        return list()
    order_sql = """ ORDER BY date {}""".format(order)

    # Limit part
    limit_sql = ""
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            print "Wrong limit value"
            return list()
        if limit < 0:
            print "Wrong limit value"
            return list()
        limit_sql = """ LIMIT {}""".format(limit)

    sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, date, slug, likes, dislikes, \
        points, posts FROM Thread WHERE {where_value} {since_value} {order_value} {limit_value};""".format(
        where_value=where_sql, since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

    thread_list_sql = db.execute(sql)
    if not thread_list_sql:
        return list()

    thread_list = list()
    for thread_sql in thread_list_sql:
        thread_list.append({'id': str_to_json(thread_sql[0]),
                            'title': str_to_json(thread_sql[1]),
                            'user': str_to_json(thread_sql[2]),
                            'message': str_to_json(thread_sql[3]),
                            'forum': str_to_json(thread_sql[4]),
                            'isDeleted': str_to_json(thread_sql[5], True),
                            'isClosed': str_to_json(thread_sql[6], True),
                            'date': thread_sql[7].strftime('%Y-%m-%d %H:%M:%S'),
                            'slug': str_to_json(thread_sql[8]),
                            'likes': str_to_json(thread_sql[9]),
                            'dislikes': str_to_json(thread_sql[10]),
                            'points': str_to_json(thread_sql[11]),
                            'posts': str_to_json(thread_sql[12])})

    return thread_list


def get_thread_by_id(id_value):
    sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, date, slug, likes, dislikes, \
        points, posts FROM Thread WHERE thread = %(thread)s LIMIT 1;"""

    thread_list_sql = db.execute(sql, {'thread': id_value})
    if not thread_list_sql:
        return list()

    thread_sql = thread_list_sql[0]
    return {'id': str_to_json(thread_sql[0]),
            'title': str_to_json(thread_sql[1]),
            'user': str_to_json(thread_sql[2]),
            'message': str_to_json(thread_sql[3]),
            'forum': str_to_json(thread_sql[4]),
            'isDeleted': str_to_json(thread_sql[5], True),
            'isClosed': str_to_json(thread_sql[6], True),
            'date': thread_sql[7].strftime('%Y-%m-%d %H:%M:%S'),
            'slug': str_to_json(thread_sql[8]),
            'likes': str_to_json(thread_sql[9]),
            'dislikes': str_to_json(thread_sql[10]),
            'points': str_to_json(thread_sql[11]),
            'posts': str_to_json(thread_sql[12])}


def get_user_dict(email):
    user_list_sql = db.execute("""SELECT user, email, name, username, isAnonymous, about FROM User \
        WHERE email = %(email)s;""", {'email': email})
    if not user_list_sql:
        return dict()

    user_sql = user_list_sql[0]

    return {'id': str_to_json(user_sql[0]),
            'email': str_to_json(user_sql[1]),
            'name': str_to_json(user_sql[2]),
            'username': str_to_json(user_sql[3]),
            'isAnonymous': str_to_json(user_sql[4], True),
            'about': str_to_json(user_sql[5])}


def inc_posts_for_thread(thread_id):
    db.execute("""UPDATE Thread SET posts = posts + 1 WHERE thread = %(thread)s;""", {'thread': thread_id}, post=True)


def dec_posts_for_thread(thread_id):
    db.execute("""UPDATE Thread SET posts = posts - 1 WHERE thread = %(thread)s;""", {'thread': thread_id}, post=True)


def remove_post(post_id):
    db.execute("""UPDATE Post SET isDeleted = 1 WHERE post = %(post)s;""", {'post': post_id}, True)


def restore_post(post_id):
    db.execute("""UPDATE Post SET isDeleted = 0 WHERE post = %(post)s;""", {'post': post_id}, True)


def get_followers_list(email):
    followers_list_sql = db.execute("""SELECT follower FROM Follower WHERE following = %(following)s;""",
                                    {'following': email})
    if not followers_list_sql:
        return list()

    return followers_list_sql[0]


def get_following_list(email):
    following_list = db.execute("""SELECT following FROM Follower WHERE follower = %(follower)s;""",
                                {'follower': email})
    if not following_list:
        return list()

    return following_list[0]


def get_subscribed_threads_list(email):
    subscriptions_list = db.execute("""SELECT thread FROM Subscription WHERE subscriber = %(subscriber)s;""",
                                    {'subscriber': email})
    result = list()
    for thread in subscriptions_list:
        result.append(thread[0])

    return result


def get_json(request):
    if request.method == 'GET':
        return dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

    return request.json