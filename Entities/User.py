import MySQLdb
from common import *


class User:
    def __init__(self):
        pass

    def do_method(self, db_method, html_method, request_body, qs_dict):
        if db_method == 'create':
            return self.create(html_method, request_body)
        elif db_method == 'details':
            return self.details(qs_dict)
        elif db_method == 'follow':
            return self.follow(html_method, request_body)
        elif db_method == 'unfollow':
            return self.unfollow(html_method, request_body)
        elif db_method == 'listPosts':
            return self.list_posts(qs_dict)
        elif db_method == 'updateProfile':
            return self.update_profile(html_method, request_body)
        elif db_method == 'listFollowers':
            return self.list_followers(qs_dict)
        elif db_method == 'listFollowing':
            return self.list_following(qs_dict)

        return [json.dumps({"code": 3, "response": "Unknown user db method"}, indent=4)]

    @staticmethod
    def create(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'user.create'"}, indent=4)]

        request_body = json.loads(request_body)

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
        sql = """INSERT INTO User (username, about, name, email, isAnonymous) \
            VALUES (%s, %s, %s, %s, %s);"""
        args = (username, about, name, email, is_anonymous)
        db = MyDatabase()

        try:
            db.execute(sql, args, True)
        except MySQLdb.IntegrityError, message:
            error_code = message[0]
            if error_code == MYSQL_DUPLICATE_ENTITY_ERROR:
                return [json.dumps({"code": 5,
                                    "response": "This user already exists"}, indent=4)]
            else:
                return [json.dumps({"code": 4,
                                    "response": "Oh, we have some really bad error"}, indent=4)]

        user_dict = get_user_dict(email)

        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def details(qs_dict):
        if not qs_dict.get('user'):
            return [json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)]

        email = qs_dict['user'][0]
        user_dict = get_user_dict(email)

        sql = """SELECT follower FROM Follower WHERE following = %s;"""
        db = MyDatabase()
        followers_list = db.execute(sql, email)
        user_dict['followers'] = followers_list

        sql = """SELECT following FROM Follower WHERE follower = %s;"""
        db = MyDatabase()
        following_list = db.execute(sql, email)
        user_dict['following'] = following_list

        sql = """SELECT thread FROM Subscription WHERE subscriber = %s;"""
        db = MyDatabase()
        user_dict['subscriptions'] = db.execute(sql, email)

        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def follow(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'user.follow'"}, indent=4)]

        request_body = json.loads(request_body)

        follower = request_body.get('follower')
        followee = request_body.get('followee')
        sql = """INSERT INTO Follower (follower, following) VALUES (%s, %s);"""
        args = (follower, followee)
        db = MyDatabase()
        db.execute(sql, args, True)
        user_dict = get_user_dict(follower)
        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def unfollow(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'user.unfollow'"}, indent=4)]

        request_body = json.loads(request_body)

        follower = request_body.get('follower')
        followee = request_body.get('followee')
        sql = """DELETE FROM Follower WHERE follower = %s AND following = %s;"""
        args = (follower, followee)
        db = MyDatabase()
        db.execute(sql, args, True)
        user_dict = get_user_dict(follower)
        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def list_posts(qs_dict):
        if not qs_dict.get('user'):
            return [json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)]

        user = qs_dict['user'][0]

        # Since part
        since = ''
        if qs_dict.get('since'):
            since = qs_dict['since'][0]

        # Limit part
        limit = -1
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]

        # Order part
        order = 'desc'
        if qs_dict.get('order'):
            order = qs_dict['order'][0]

        post_list = get_post_list(user=user, since=since, limit=limit, order=order)
        return [json.dumps({"code": 0, "response": post_list}, indent=4)]

    @staticmethod
    def update_profile(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'user.updateProfile'"}, indent=4)]

        request_body = json.loads(request_body)

        about = request_body.get('about')
        about = try_encode(about)
        user = request_body.get('user')
        user = try_encode(user)
        name = request_body.get('name')
        name = try_encode(name)

        sql = """UPDATE User SET about = %s, name = %s WHERE email = %s;"""
        args = (about, name, user)
        db = MyDatabase()
        db.execute(sql, args)
        user_dict = get_user_dict(user)
        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def list_followers(qs_dict):
        if not qs_dict.get('user'):
            return [json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)]

        user = qs_dict['user'][0]

        # Since part
        since_id = -1
        if qs_dict.get('since_id'):
            since_id = qs_dict['since_id'][0]
        since_sql = ""
        if since_id != -1:
            since_sql = """AND User.user > {}""".format(since_id)

        # Order part
        order = 'desc'
        if qs_dict['order']:
            order = qs_dict['order'][0]
        order_sql = """ORDER BY date {}""".format(order)

        # Limit part
        limit = -1
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]
        limit_sql = ""
        if limit != -1:
            try:
                limit = int(limit)
            except ValueError:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            if limit < 0:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            limit_sql = """LIMIT {}""".format(limit)

        sql = """SELECT about, email, user, isAnonymous, name, username FROM User \
            JOIN Follower ON Follower.follower = User.email \
            WHERE Follower.following = %s %s %s %s;"""
        args = (user, since_sql, order_sql, limit_sql)
        db = MyDatabase()
        user_list_sql = db.execute(sql, args, True)
        if not user_list_sql:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        if not user_list_sql[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        user_list = list()
        for user_sql in user_list_sql:
            user = dict()
            user['about'] = str_to_json(user_sql[0])
            user['email'] = str_to_json(user_sql[1])
            user['id'] = str_to_json(user_sql[2])
            user['isAnonymous'] = str_to_json(user_sql[3])
            user['name'] = str_to_json(user_sql[4])
            user['username'] = str_to_json(user_sql[5])

            sql = """SELECT follower FROM Follower WHERE following = %s;"""
            db = MyDatabase()
            user['followers'] = db.execute(sql, user)

            sql = """SELECT following FROM Follower WHERE follower = %s;"""
            user['following'] = db.execute(sql, user)

            sql = """SELECT thread FROM Subscription WHERE subscriber = %s;"""
            db = MyDatabase()
            user['subscriptions'] = db.execute(sql, user)

            user_list.append(user)

        return [json.dumps({"code": 0, "response": user_list}, indent=4)]

    @staticmethod
    def list_following(qs_dict):
        if not qs_dict.get('user'):
            return [json.dumps({"code": 2, "response": "No 'user' key"}, indent=4)]

        user = qs_dict['user'][0]

        # Since part
        since_id = ""
        if qs_dict.get('since_id'):
            since_id = qs_dict['since_id'][0]
        since_sql = ""
        if since_id != "":
            since_sql = """AND User.user > {}""".format(since_id)

        # Order part
        order = "desc"
        if qs_dict.get('order'):
            order = qs_dict['order'][0]
        order_sql = """ORDER BY date {}""".format(order)

        # Limit part
        limit = -1
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]
        limit_sql = ""
        if limit != -1:
            try:
                limit = int(limit)
            except ValueError:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            if limit < 0:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            limit_sql = """LIMIT {}""".format(limit)

        sql = """SELECT about, email, user, isAnonymous, name, username FROM User \
            JOIN Follower ON Follower.following = User.email \
            WHERE Follower.follower = %s %s %s %s;"""
        args = (user, since_sql, order_sql, limit_sql)
        db = MyDatabase()
        user_list_sql = db.execute(sql, args, True)
        if not user_list_sql:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        if not user_list_sql[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        user_list = list()
        for user_sql in user_list_sql:
            user = dict()
            user['about'] = str_to_json(user_sql[0])
            user['email'] = str_to_json(user_sql[1])
            user['id'] = str_to_json(user_sql[2])
            user['isAnonymous'] = str_to_json(user_sql[3])
            user['name'] = str_to_json(user_sql[4])
            user['username'] = str_to_json(user_sql[5])

            sql = """SELECT follower FROM Follower WHERE following = %s;"""
            db = MyDatabase()
            user['followers'] = db.execute(sql, user)

            sql = """SELECT following FROM Follower WHERE follower = %s;"""
            user['following'] = db.execute(sql, user)

            sql = """SELECT thread FROM Subscription WHERE subscriber = %s;"""
            db = MyDatabase()
            user['subscriptions'] = db.execute(sql, user)

            user_list.append(user)

        return [json.dumps({"code": 0, "response": user_list}, indent=4)]
