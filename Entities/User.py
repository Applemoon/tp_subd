import json
import MySQLdb
from flask import Blueprint, request

from Entities.MyDatabase import db
from common import try_encode, MYSQL_DUPLICATE_ENTITY_ERROR, get_user_dict, get_json, get_followers_list, \
    get_following_list, get_subscribed_threads_list, get_post_list, str_to_json

module = Blueprint('user', __name__, url_prefix='/db/api/user')


@module.route("/create/", methods=["POST"])
def create():
    request_body = request.json

    username = try_encode(request_body.get('username'))
    about = request_body.get('about')
    name = try_encode(request_body.get('name'))
    email = request_body.get('email')
    is_anonymous_key = request_body.get('isAnonymous', False)
    if is_anonymous_key:
        is_anonymous = 1
    else:
        is_anonymous = 0

    sql = """INSERT INTO User (username, about, name, email, isAnonymous) VALUES \
        (%(username)s, %(about)s, %(name)s, %(email)s, %(isAnonymous)s);"""
    args = {'username': username, 'about': about, 'name': name, 'email': email, 'isAnonymous': is_anonymous}

    try:
        db.execute(sql, args, True)
    except MySQLdb.IntegrityError, message:
        if message[0] == MYSQL_DUPLICATE_ENTITY_ERROR:
            return json.dumps({"code": 5,
                               "response": "This user already exists"}, indent=4)
        return json.dumps({"code": 4,
                           "response": "Oh, we have some really bad error"}, indent=4)

    user_dict = get_user_dict(email)

    return json.dumps({"code": 0, "response": user_dict}, indent=4)


@module.route("/details/", methods=["GET"])
def details():
    qs = get_json(request)
    email = qs.get('user')
    if not email:
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    user = get_user_dict(email)

    user['followers'] = get_followers_list(email)
    user['following'] = get_following_list(email)
    user['subscriptions'] = get_subscribed_threads_list(email)

    return json.dumps({"code": 0, "response": user}, indent=4)


@module.route("/follow/", methods=["POST"])
def follow():
    return follow_method(False)


@module.route("/unfollow/", methods=["POST"])
def unfollow():
    return follow_method(True)


def follow_method(do_unfollow):
    request_body = request.json

    follower = request_body.get('follower')
    followee = request_body.get('followee')

    args = {'follower': follower, 'following': followee}
    if not do_unfollow:
        db.execute("""INSERT INTO Follower (follower, following) VALUES (%(follower)s, %(following)s);""", args, True)
    else:
        db.execute("""DELETE FROM Follower WHERE follower = %(follower)s AND following = %(following)s;""", args, True)

    return json.dumps({"code": 0, "response": get_user_dict(follower)}, indent=4)


@module.route("/listPosts/", methods=["GET"])
def list_posts():
    qs = get_json(request)

    email = qs.get('user')
    if not email:
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    since = qs.get('since', '')
    limit = qs.get('limit', -1)
    order = qs.get('order', 'desc')

    post_list = get_post_list(user=email, since=since, limit=limit, order=order)
    return json.dumps({"code": 0, "response": post_list}, indent=4)


@module.route("/updateProfile/", methods=["POST"])
def update_profile():
    request_body = request.json

    about = try_encode(request_body.get('about'))
    email = try_encode(request_body.get('user'))
    name = try_encode(request_body.get('name'))

    args = {'about': about, 'name': name, 'email': email}
    db.execute("""UPDATE User SET about = %(about)s, name = %(name)s WHERE email = %(email)s;""", args, True)
    return json.dumps({"code": 0, "response": get_user_dict(email)}, indent=4)


@module.route("/listFollowers/", methods=["GET"])
def list_followers():
    return list_followers_method(False)


@module.route("/listFollowing/", methods=["GET"])
def list_following():
    return list_followers_method(True)


def list_followers_method(is_following):
    qs = get_json(request)

    email = qs.get('user')
    if not email:
        return json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)

    # Since part
    since_id = qs.get('since_id', -1)
    if since_id != -1:
        since_sql = """AND User.user >= {}""".format(since_id)
    else:
        since_sql = ""

    # Order part
    order_sql = """ORDER BY User.name {}""".format(qs.get('order', 'desc'))

    # Limit part
    limit = qs.get('limit', -1)
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        if limit < 0:
            return json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)
        limit_sql = """LIMIT {}""".format(limit)
    else:
        limit_sql = ""

    sql = """SELECT about, email, user, isAnonymous, name, username FROM User JOIN Follower ON """
    if not is_following:
        sql += """Follower.follower = User.email WHERE Follower.following"""
    else:
        sql += """Follower.following = User.email WHERE Follower.follower"""

    sql += """ = %(email)s {since_value} {order_value} {limit_value};""".format(
        since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

    user_list_sql = db.execute(sql, {'email': email})
    if not user_list_sql:
        return json.dumps({"code": 1, "response": "Empty set"}, indent=4)

    user_list = list()
    for user_sql in user_list_sql:
        follower_email = str_to_json(user_sql[1])
        user_list.append({'about': str_to_json(user_sql[0]),
                          'email': follower_email,
                          'id': str_to_json(user_sql[2]),
                          'isAnonymous': str_to_json(user_sql[3]),
                          'name': str_to_json(user_sql[4]),
                          'username': str_to_json(user_sql[5]),
                          'followers': get_followers_list(follower_email),
                          'following': get_following_list(follower_email),
                          'subscriptions': get_subscribed_threads_list(follower_email)})

    return json.dumps({"code": 0, "response": user_list}, indent=4)
