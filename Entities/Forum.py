import MySQLdb
import json

from MyDatabase import MyDatabase
from common import *


class Forum:
    def doMethod(self, db_method, html_method, request_body, qs_dict):
        if db_method == 'create':
            return self.create(html_method, request_body)
        elif db_method == 'details':
            return self.details(qs_dict)
        elif db_method == 'listPosts':
            return self.list_posts(qs_dict)
        elif db_method == 'listThreads':
            return self.list_threads(qs_dict)
        elif db_method == 'listUsers':
            return self.list_users(qs_dict)

        return [json.dumps({"code": 3, "response": "Unknown forum db method"}, indent=4)]

    @staticmethod
    def create(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3, "response": "Wrong html method \
                for 'forum.create'"}, indent=4)]

        request_body = json.loads(request_body)
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
            forum_dict = get_forum_dict(id_value=db.get_last_row_id())

            return [json.dumps({"code": 0, "response": forum_dict}, indent=4)]

    @staticmethod
    def details(qs_dict):
        if not qs_dict.get('forum'):
            return [json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)]

        short_name = qs_dict['forum'][0]
        forum_dict = get_forum_dict(short_name=short_name)
        if forum_dict == dict():
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        if qs_dict.get('related') and qs_dict.get('related')[0] == 'user':
            user = get_user_dict(forum_dict['user'])
            if user == dict():
                return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

            sql = """SELECT follower FROM Follower WHERE following = %s"""
            args = (user['email'])
            db = MyDatabase()
            data = db.execute(sql, args)

            followers_list = list()
            for line in data:
                followers_list.append(line[0])
            user['followers'] = followers_list

            sql = """SELECT following FROM Follower WHERE follower = %s"""
            args = (user['email'])
            data = db.execute(sql, args)
            following_list = list()
            for line in data:
                following_list.append(line[0])
            user['following'] = str_to_json(following_list)

            sql = """SELECT thread FROM Subscription WHERE subscriber = %s"""
            args = (user['email'])
            data = db.execute(sql, args)
            data_list = list()
            for line in data:
                data_list.append(line[0])
            user['subscriptions'] = data_list

            forum_dict['user'] = user

        return [json.dumps({"code": 0, "response": forum_dict}, indent=4)]

    @staticmethod
    def list_posts(qs_dict):
        if not qs_dict.get('forum'):
            return [json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)]

        # Related part
        thread_related = False
        forum_related = False
        user_related = False
        if qs_dict.get('related'):
            for related_value in qs_dict['related']:
                if related_value == 'thread':
                    thread_related = True
                elif related_value == 'forum':
                    forum_related = True
                elif related_value == 'user':
                    user_related = True
                else:
                    return [json.dumps({"code": 3, "response": "Wrong related value"},
                                       indent=4)]

        if qs_dict.get('since'):
            since = qs_dict['since'][0]

        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]

        if qs_dict.get('sort'):
            sort = qs_dict['sort'][0]

        if qs_dict.get('order'):
            order = qs_dict['order'][0]

        post_list = get_post_list(forum=qs_dict['forum'][0], since=since, limit=limit,
                                  sort=sort, order=order)

        if not post_list:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        if not post_list[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        post_list = list()
        for post in post_list:
            if user_related:
                post['user'] = get_user_dict(post[1])

            if thread_related:
                post['thread'] = get_thread_list(id_value=post[2])

            if forum_related:
                post['forum'] = get_forum_dict(short_name=post[3])

            post_list.append(post)

        return [json.dumps({"code": 0, "response": post_list}, indent=4)]

    @staticmethod
    def list_threads(qs_dict):
        if not qs_dict.get('forum'):
            return [json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)]

        # Since part
        since_sql = ''
        if qs_dict.get('since'):
            since_sql = """AND date >= '{}'""".format(qs_dict['since'][0])

        # Limit part
        limit_sql = ''
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]
            try:
                limit = int(limit)
            except ValueError:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            if limit < 0:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            limit_sql = """LIMIT {}""".format(limit)

        # Order part
        order = 'desc'
        if qs_dict.get('order'):
            order = qs_dict['order'][0]
            if order != 'asc' and order != 'desc':
                return [json.dumps({"code": 3, "response": "Wrong order value"}, indent=4)]
        order_sql = """ORDER BY date {}""".format(order)

        # Related part
        forum_related = False
        user_related = False
        if qs_dict.get('related'):
            for related_value in qs_dict['related']:
                if related_value == 'forum':
                    forum_related = True
                elif related_value == 'user':
                    user_related = True
                else:
                    return [json.dumps({"code": 3, "response": "Wrong related value"},
                                       indent=4)]

        sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
            date, slug FROM Thread \
            WHERE forum = %s {snc_sql} {ord_sql} {lim_sql};""".format(snc_sql=since_sql,
                                                                      ord_sql=order_sql, lim_sql=limit_sql)

        db = MyDatabase()
        data = db.execute(sql, (qs_dict['forum'][0]))
        if not data:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        thread_list = list()
        for thread in data:
            thread_dict = dict()
            thread_dict['id'] = str_to_json(thread[0])
            thread_dict['title'] = str_to_json(thread[1])
            thread_dict['user'] = str_to_json(thread[2])
            thread_dict['message'] = str_to_json(thread[3])
            thread_dict['forum'] = str_to_json(thread[4])
            thread_dict['isDeleted'] = str_to_json(thread[5], True)
            thread_dict['isClosed'] = str_to_json(thread[6], True)
            date = thread[7].strftime('%Y-%m-%d %H:%M:%S')
            thread_dict['date'] = str_to_json(date)
            thread_dict['slug'] = str_to_json(thread[8])

            if user_related:
                thread_dict['user'] = get_user_dict(thread_dict['user'])

            if forum_related:
                thread_dict['forum'] = get_forum_dict(short_name=thread_dict['forum'])

            thread_list.append(thread_dict)

        return [json.dumps({"code": 0, "response": thread_list}, indent=4)]

    @staticmethod
    def list_users(qs_dict):
        if not qs_dict.get('forum'):
            return [json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)]

        # Since id part
        since_id_sql = ''
        if qs_dict.get('since_id'):
            since_id = qs_dict['since_id'][0]
            try:
                since_id = int(since_id)
            except ValueError:
                return [json.dumps({"code": 3, "response": "Wrong since_id value"},
                                   indent=4)]
            since_id_sql = """AND User.user >= '{}'""".format(since_id)

        # Limit part
        limit_sql = ''
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]
            try:
                limit = int(limit)
            except ValueError:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            if limit < 0:
                return [json.dumps({"code": 3, "response": "Wrong limit value"}, indent=4)]
            limit_sql = """LIMIT {}""".format(limit)

        # Order part
        order = 'desc'
        if qs_dict.get('order'):
            order = qs_dict['order'][0]
            if order != 'asc' and order != 'desc':
                return [json.dumps({"code": 3, "response": "Wrong order value"}, indent=4)]
        order_sql = """ORDER BY User.name {}""".format(order)

        sql = """SELECT User.user, User.email, User.name, User.username, \
            User.isAnonymous, User.about FROM User \
            JOIN Post ON Post.user = User.email \
            WHERE Post.forum = %s {snc_sql} {ord_sql} {lim_sql};""".format(
            snc_sql=since_id_sql,
            lim_sql=limit_sql,
            ord_sql=order_sql)
        args = (qs_dict['forum'][0])

        db = MyDatabase()
        data = db.execute(sql, args)
        if not data:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        user_list = list()
        for user in data:
            user_dict = dict()
            user_dict['id'] = str_to_json(user[0])
            user_dict['email'] = str_to_json(user[1])
            user_dict['name'] = str_to_json(user[2])
            user_dict['username'] = str_to_json(user[3])
            user_dict['isAnonymous'] = str_to_json(user[4])
            user_dict['about'] = str_to_json(user[5])
            user_list.append(user_dict)

        return [json.dumps({"code": 0, "response": user_list}, indent=4)]
