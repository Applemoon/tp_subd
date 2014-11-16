import MySQLdb
from common import *


class Thread:
    def __init__(self):
        pass

    def do_method(self, db_method, html_method, request_body, qs_dict):
        if db_method == 'list':
            return self.list(qs_dict)
        elif db_method == 'create':
            return self.create(html_method, request_body)
        elif db_method == 'details':
            return self.details(qs_dict)
        elif db_method == 'remove':
            return self.remove(html_method, request_body)
        elif db_method == 'open':
            return self.open(html_method, request_body)
        elif db_method == 'close':
            return self.close(html_method, request_body)
        elif db_method == 'restore':
            return self.restore(html_method, request_body)
        elif db_method == 'listPosts':
            return self.list_posts(qs_dict)
        elif db_method == 'update':
            return self.update(html_method, request_body)
        elif db_method == 'subscribe':
            return self.subscribe(html_method, request_body)
        elif db_method == 'unsubscribe':
            return self.unsubscribe(html_method, request_body)
        elif db_method == 'vote':
            return self.vote(html_method, request_body)

        return [json.dumps({"code": 3, "response": "Unknown thread db method"}, indent=4)]

    @staticmethod
    def list(qs_dict):
        if qs_dict.get('forum'):
            key = "forum"
        elif qs_dict.get('user'):
            key = "user"
        else:
            return [json.dumps({"code": 2, "response": "No 'forum' key"}, indent=4)]
        key_value = qs_dict[key][0]

        # Since part
        since = ""
        if qs_dict.get('since'):
            since = qs_dict['since'][0]

        # Order part
        order = ""
        if qs_dict.get('order'):
            order = qs_dict['order'][0]

        # Limit part
        limit = -1
        if qs_dict.get('limit'):
            limit = qs_dict['limit'][0]
        if key == "forum":
            thread_list = get_thread_list(forum=key_value, since=since, order=order, limit=limit)
        else:
            thread_list = get_thread_list(user=key_value, since=since, order=order, limit=limit)

        return [json.dumps({"code": 0, "response": thread_list}, indent=4)]

    @staticmethod
    def create(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3, "response": "Wrong html method for 'thread.create'"}, indent=4)]

        request_body = json.loads(request_body)

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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        args = (forum, title, is_closed, user, date, message, slug, is_deleted)
        db = MyDatabase()

        try:
            db.execute(sql, args, True)
        except MySQLdb.IntegrityError, message:
            print message[0]
        finally:
            thread_list = get_thread_list(title=title)
            if thread_list == list():
                return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

            return [json.dumps({"code": 0, "response": thread_list[0]}, indent=4)]

    @staticmethod
    def details(qs_dict):
        if not qs_dict.get('thread'):
            return [json.dumps({"code": 2, "response": "No 'thread' key"}, indent=4)]

        thread_id = qs_dict['thread'][0]
        thread_list = get_thread_list(id_value=thread_id)
        if thread_list == list():
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        thread = thread_list[0]

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

        if forum_related:
            thread['forum'] = get_forum_dict(short_name=thread['forum'])

        if user_related:
            thread['user'] = get_user_dict(thread['user'])

        return [json.dumps({"code": 0, "response": thread}, indent=4)]

    @staticmethod
    def remove(html_method, request_body, restore=False):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.remove/restore'"}, indent=4)]

        request_body = json.loads(request_body)

        thread = request_body.get('thread')
        if not restore:
            sql = """UPDATE Thread SET isDeleted = 1, posts = 0 WHERE thread = %s;"""
            post_list = get_post_list(thread=thread)
            for post in post_list:
                remove_post(post['id'], thread)
        else:
            sql = """UPDATE Thread SET isDeleted = 0 WHERE thread = %s;"""

        db = MyDatabase()
        db.execute(sql, thread, True)

        return [json.dumps({"code": 0, "response": thread}, indent=4)]

    @staticmethod
    def open(html_method, request_body, close=False):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.open/close'"}, indent=4)]

        request_body = json.loads(request_body)

        thread = request_body.get('thread')
        if not close:
            sql = """UPDATE Thread SET isClosed = 0 WHERE thread = %s;"""
        else:
            sql = """UPDATE Thread SET isClosed = 1 WHERE thread = %s;"""

        db = MyDatabase()
        db.execute(sql, thread, True)

        return [json.dumps({"code": 0, "response": thread}, indent=4)]

    @staticmethod
    def close(html_method, request_body):
        return Thread.open(html_method, request_body, True)

    @staticmethod
    def restore(html_method, request_body):
        return Thread.remove(html_method, request_body, True)

    @staticmethod
    def list_posts(qs_dict):
        thread = qs_dict.get('thread')[0]

        since = ""
        if qs_dict.get('since', ''):
            since = qs_dict['since'][0]

        limit = -1
        if qs_dict.get('limit', ''):
            limit = qs_dict['limit'][0]

        order = 'desc'
        if qs_dict.get('order'):
            order = qs_dict['order'][0]

        sort = 'flat'
        if qs_dict.get('sort'):
            sort = qs_dict['sort'][0]

        post_list = get_post_list(thread=thread, since=since, limit=limit, sort=sort, order=order)

        return [json.dumps({"code": 0, "response": post_list}, indent=4)]

    @staticmethod
    def update(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.update'"}, indent=4)]

        request_body = json.loads(request_body)

        message = request_body.get('message')
        message = try_encode(message)
        slug = request_body.get('slug')
        thread = request_body.get('thread')

        sql = """UPDATE Thread SET message = %s, slug = %s WHERE thread = %s;"""
        args = (message, slug, thread)
        db = MyDatabase()
        db.execute(sql, args, True)
        thread_list = get_thread_list(id_value=thread)
        if thread_list != list():
            thread_dict = thread_list[0]
        else:
            thread_dict = dict()

        return [json.dumps({"code": 0, "response": thread_dict}, indent=4)]

    @staticmethod
    def subscribe(html_method, request_body, unsubscribe=False):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.subscribe/unsubscribe'"}, indent=4)]

        request_body = json.loads(request_body)

        user = request_body.get('user')
        thread = request_body.get('thread')
        if not unsubscribe:
            sql = """INSERT INTO Subscription (subscriber, thread) VALUES (%s, %s);"""
        else:
            sql = """DELETE FROM Subscription WHERE subscriber = %s AND thread = %s;"""

        args = (user, thread)
        db = MyDatabase()
        db.execute(sql, args, True)
        result_dict = dict()
        result_dict['thread'] = thread
        result_dict['user'] = str_to_json(user)

        return [json.dumps({"code": 0, "response": result_dict}, indent=4)]

    @staticmethod
    def unsubscribe(html_method, request_body):
        return Thread.subscribe(html_method, request_body, True)

    @staticmethod
    def vote(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.vote'"}, indent=4)]

        request_body = json.loads(request_body)

        vote = request_body.get('vote')
        thread = request_body.get('thread')

        if vote == 1:
            sql = """UPDATE Thread SET likes = likes + 1, points = points + 1 WHERE thread = %s;"""
        else:
            sql = """UPDATE Thread SET dislikes = dislikes + 1, points = points - 1 WHERE thread = %s;"""

        db = MyDatabase()
        db.execute(sql, thread, True)

        thread_dict = dict()
        thread_list = get_thread_list(id_value=thread)
        if thread_list != list():
            thread_dict = thread_list[0]

        return [json.dumps({"code": 0, "response": thread_dict}, indent=4)]
