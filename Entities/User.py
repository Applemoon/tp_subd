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
            errorcode = message[0]
            if errorcode == MYSQL_DUPLICATE_ENTITY_ERROR:
                return [json.dumps({"code": 5,
                                    "response": "This user already exists"}, indent=4)]
            else:
                return [json.dumps({"code": 4,
                                    "response": "Oh, we have some realy bad error"}, indent=4)]

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
        subscriptions_list = db.execute(sql, email)
        user_dict['subscriptions'] = subscriptions_list

        return [json.dumps({"code": 0, "response": user_dict}, indent=4)]

    @staticmethod
    def follow(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def unfollow(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def list_posts(qs_dict):
        # TODO
        return True

    @staticmethod
    def update_profile(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def list_followers(qs_dict):
        # TODO
        return True

    @staticmethod
    def list_following(qs_dict):
        # TODO
        return True
