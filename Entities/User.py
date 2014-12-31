import MySQLdb
from common import *


def do_method(db_method, html_method, request_body, qs_dict):
    if db_method == 'create':
        return create(html_method, request_body)
    elif db_method == 'details':
        return details(qs_dict)
    elif db_method == 'follow':
        return follow(html_method, request_body)
    elif db_method == 'unfollow':
        return unfollow(html_method, request_body)
    elif db_method == 'listPosts':
        return list_posts(qs_dict)
    elif db_method == 'updateProfile':
        return update_profile(html_method, request_body)
    elif db_method == 'listFollowers':
        return list_followers(qs_dict)
    elif db_method == 'listFollowing':
        return list_following(qs_dict)

    return json.dumps({"code": 3, "response": "Unknown user db method"}, indent=4)


def create(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'user.create'"}, indent=4)

    request_body = json.loads(request_body.data)

    username = request_body.get('username')
    username = try_encode(username)
    about = request_body.get('about')
    name = request_body.get('name')
    name = try_encode(name)
    email = request_body.get('email')
    is_anonymous_key = request_body.get('isAnonymous', False)
    if is_anonymous_key:
        is_anonymous = 1
    else:
        is_anonymous = 0

    sql = """INSERT INTO User (username, about, name, email, isAnonymous) VALUES \
        (%(username)s, %(about)s, %(name)s, %(email)s, %(isAnonymous)s);"""
    args = {'username': username, 'about': about, 'name': name, 'email': email, 'isAnonymous': is_anonymous}
    db = MyDatabase()

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        error_code = message[0]
        if error_code == MYSQL_DUPLICATE_ENTITY_ERROR:
            return json.dumps({"code": 5,
                               "response": "This user already exists"}, indent=4)
        return json.dumps({"code": 4,
                           "response": "Oh, we have some really bad error"}, indent=4)

    user_dict = get_user_dict(email)

    return json.dumps({"code": 0, "response": user_dict}, indent=4)


def details(qs_dict):
    if not qs_dict.get('user'):
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    email = qs_dict.get('user')[0]
    user = get_user_dict(email)

    user['followers'] = get_followers_list(email)
    user['following'] = get_following_list(email)
    user['subscriptions'] = get_subscribed_threads_list(email)

    return json.dumps({"code": 0, "response": user}, indent=4)


def follow(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'user.follow'"}, indent=4)

    request_body = json.loads(request_body.data)

    follower = request_body.get('follower')
    followee = request_body.get('followee')

    sql = """INSERT INTO Follower (follower, following) VALUES (%(follower)s, %(following)s);"""
    args = {'follower': follower, 'following': followee}
    db = MyDatabase()
    db.execute(sql, args, True)
    user_dict = get_user_dict(follower)
    return json.dumps({"code": 0, "response": user_dict}, indent=4)


def unfollow(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'user.unfollow'"}, indent=4)

    request_body = json.loads(request_body.data)

    follower = request_body.get('follower')
    followee = request_body.get('followee')

    sql = """DELETE FROM Follower WHERE follower = %(follower)s AND following = %(following)s;"""
    args = {'follower': follower, 'following': followee}
    db = MyDatabase()
    db.execute(sql, args, True)
    user = get_user_dict(follower)
    return json.dumps({"code": 0, "response": user}, indent=4)


def list_posts(qs_dict):
    if not qs_dict.get('user'):
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    user = qs_dict.get('user')[0]

    # Since part
    since = ''
    if qs_dict.get('since'):
        since = qs_dict.get('since')[0]

    # Limit part
    limit = -1
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]

    # Order part
    order = 'desc'
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]

    post_list = get_post_list(user=user, since=since, limit=limit, order=order)
    return json.dumps({"code": 0, "response": post_list}, indent=4)


def update_profile(html_method, request_body):
    if html_method != 'POST':
        return json.dumps({"code": 3,
                           "response": "Wrong html method for 'user.updateProfile'"}, indent=4)

    request_body = json.loads(request_body.data)

    about = request_body.get('about')
    about = try_encode(about)
    user = request_body.get('user')
    user = try_encode(user)
    name = request_body.get('name')
    name = try_encode(name)

    sql = """UPDATE User SET about = %(about)s, name = %(name)s WHERE email = %(email)s;"""
    args = {'about': about, 'name': name, 'email': user}
    db = MyDatabase()
    db.execute(sql, args, True)
    user = get_user_dict(user)
    return json.dumps({"code": 0, "response": user}, indent=4)


def list_followers(qs_dict, following=False):
    if not qs_dict.get('user'):
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    user_email = qs_dict.get('user')[0]

    # Since part
    since_id = -1
    if qs_dict.get('since_id'):
        since_id = qs_dict.get('since_id')[0]
    since_sql = ""
    if since_id != -1:
        since_sql = """AND User.user >= {}""".format(since_id)

    # Order part
    order = 'desc'
    if qs_dict.get('order'):
        order = qs_dict.get('order')[0]
    order_sql = """ORDER BY User.name {}""".format(order)

    # Limit part
    limit = -1
    if qs_dict.get('limit'):
        limit = qs_dict.get('limit')[0]
    limit_sql = ""
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        if limit < 0:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        limit_sql = """LIMIT {}""".format(limit)

    sql = """SELECT about, email, user, isAnonymous, name, username FROM User JOIN Follower ON """
    if not following:
        sql += """Follower.follower = User.email WHERE Follower.following"""
    else:
        sql += """Follower.following = User.email WHERE Follower.follower"""

    sql += """ = %(email)s {since_value} {order_value} {limit_value};""".format(
        since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

    db = MyDatabase()
    user_list_sql = db.execute(sql, {'email': user_email})
    if not user_list_sql:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)
    if not user_list_sql[0]:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    user_list = list()
    for user_sql in user_list_sql:
        user = dict()
        user['about'] = str_to_json(user_sql[0])
        user['email'] = str_to_json(user_sql[1])
        user['id'] = str_to_json(user_sql[2])
        user['isAnonymous'] = str_to_json(user_sql[3])
        user['name'] = str_to_json(user_sql[4])
        user['username'] = str_to_json(user_sql[5])
        user['followers'] = get_followers_list(user['email'])
        user['following'] = get_following_list(user['email'])
        user['subscriptions'] = get_subscribed_threads_list(user['email'])

        user_list.append(user)

    return json.dumps({"code": 0, "response": user_list}, indent=4)


def list_following(qs_dict):
    return list_followers(qs_dict, following=True)
