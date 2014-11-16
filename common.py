import json

from Entities.MyDatabase import MyDatabase


MYSQL_DUPLICATE_ENTITY_ERROR = 1062


def str_to_json(value, is_bool=False):
    if is_bool:
        return value != 0

    if value == "None":
        return None

    return value


def try_encode(value):
    if value is not None:
        return value.encode('utf-8')

    return value


def get_forum_dict(short_name="", id_value=""):
    if id_value != "":
        sql_where = "forum = '{}'".format(id_value)
    elif short_name != "":
        sql_where = "short_name = '{}'".format(short_name)
    else:
        print "Wrong value for id_value or short_name in getForumDict"
        return dict()

    sql = """SELECT forum, name, short_name, user FROM Forum WHERE {};""".format(sql_where)
    db = MyDatabase()
    forum_list_sql = db.execute(sql)
    if not forum_list_sql:
        return dict()
    if not forum_list_sql[0]:
        return dict()

    forum_sql = forum_list_sql[0]
    forum = dict()
    forum['id'] = str_to_json(forum_sql[0])
    forum['name'] = str_to_json(forum_sql[1])
    forum['short_name'] = str_to_json(forum_sql[2])
    forum['user'] = str_to_json(forum_sql[3])
    return forum


def get_post_list(user="", forum="", thread="", id_value="", since="", limit=-1, sort='flat',
                  order='desc', date=""):
    # WHERE part
    if id_value != "":
        where_sql = "post = {}".format(id_value)
    elif forum != "":
        where_sql = "forum = '{}'".format(forum)
    elif thread != "":
        where_sql = "thread = {}".format(thread)
    elif user != "":
        if date != "":
            where_sql = "user = '{user_value}' AND date = '{date_value}'".format(user_value=user,
                                                                                 date_value=date)
        else:
            where_sql = "user = '{user_value}'".format(user_value=user)
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
        return [json.dumps({"code": 3, "response": "Wrong order value"}, indent=4)]
    order_sql = """ORDER BY date {}""".format(order)

    sql = """SELECT post, user, thread, forum, message, parent, date, likes, dislikes, points, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
        WHERE {where_value} {since_value} {order_value} {sort_value} {limit_value};""".format(
        where_value=where_sql,
        since_value=since_sql,
        limit_value=limit_sql,
        order_value=order_sql,
        sort_value=sort_sql)

    db = MyDatabase()
    post_list_sql = db.execute(sql)
    if not post_list_sql:
        return list()
    if not post_list_sql[0]:
        return list()

    post_list = list()
    for post_sql in post_list_sql:
        post = dict()
        post['id'] = str_to_json(post_sql[0])
        post['user'] = str_to_json(post_sql[1])
        post['thread'] = str_to_json(post_sql[2])
        post['forum'] = str_to_json(post_sql[3])
        post['message'] = str_to_json(post_sql[4])
        post['parent'] = str_to_json(post_sql[5])
        post['date'] = post_sql[6].strftime('%Y-%m-%d %H:%M:%S')
        post['likes'] = str_to_json(post_sql[7])
        post['dislikes'] = str_to_json(post_sql[8])
        post['points'] = str_to_json(post_sql[9])
        post['isSpam'] = str_to_json(post_sql[10], True)
        post['isEdited'] = str_to_json(post_sql[11], True)
        post['isDeleted'] = str_to_json(post_sql[12], True)
        post['isHighlighted'] = str_to_json(post_sql[13], True)
        post['isApproved'] = str_to_json(post_sql[14], True)

        post_list.append(post)

    return post_list


def get_thread_list(id_value="", title="", forum="", user="", since="", limit=-1, order="desc"):
    if id_value != "":
        where_sql = "thread = {}".format(id_value)
    elif title != "":
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

    db = MyDatabase()
    thread_list_sql = db.execute(sql)
    if not thread_list_sql:
        return list()

    thread_list = list()
    for thread_sql in thread_list_sql:
        thread = dict()
        thread['id'] = str_to_json(thread_sql[0])
        thread['title'] = str_to_json(thread_sql[1])
        thread['user'] = str_to_json(thread_sql[2])
        thread['message'] = str_to_json(thread_sql[3])
        thread['forum'] = str_to_json(thread_sql[4])
        thread['isDeleted'] = str_to_json(thread_sql[5], True)
        thread['isClosed'] = str_to_json(thread_sql[6], True)
        date = thread_sql[7].strftime('%Y-%m-%d %H:%M:%S')
        thread['date'] = str_to_json(date)
        thread['slug'] = str_to_json(thread_sql[8])
        thread['likes'] = str_to_json(thread_sql[9])
        thread['dislikes'] = str_to_json(thread_sql[10])
        thread['points'] = str_to_json(thread_sql[11])
        thread['posts'] = str_to_json(thread_sql[12])

        thread_list.append(thread)

    return thread_list


def get_user_dict(email):
    sql = """SELECT user, email, name, username, isAnonymous, about FROM User WHERE email = %s;"""
    args = email
    db = MyDatabase()
    user_list_sql = db.execute(sql, args)
    if not user_list_sql:
        return dict()
    if not user_list_sql[0]:
        return dict()

    user_sql = user_list_sql[0]

    user = dict()
    user["id"] = str_to_json(user_sql[0])
    user["email"] = str_to_json(user_sql[1])
    user["name"] = str_to_json(user_sql[2])
    user["username"] = str_to_json(user_sql[3])
    user["isAnonymous"] = str_to_json(user_sql[4], True)
    user["about"] = str_to_json(user_sql[5])

    return user


def inc_posts_for_thread(thread_id):
    sql = """UPDATE Thread SET posts = posts + 1 WHERE thread = {};""".format(thread_id)
    db = MyDatabase()
    db.execute(sql, post=True)


def dec_posts_for_thread(thread_id):
    sql = """UPDATE Thread SET posts = posts - 1 WHERE thread = {};""".format(thread_id)
    db = MyDatabase()
    db.execute(sql, post=True)


def remove_post(post_id, thread_id):
    sql = """UPDATE Post SET isDeleted = 1 WHERE post = %s;"""
    db = MyDatabase()
    db.execute(sql, post_id, True)
    dec_posts_for_thread(thread_id)