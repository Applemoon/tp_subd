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
        since_sql = ''
        if qs_dict.get('since'):
            since_sql = """AND Thread.date >= '{}'""".format(qs_dict['since'][0])

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

        sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
            date, slug FROM Thread"""
        if key == "forum":
            sql += """ WHERE forum = %s"""
        else:
            sql += """ WHERE user = %s"""

        sql += """ {snc_sql} {ord_sql} {lim_sql};""".format(snc_sql=since_sql,
                                                            ord_sql=order_sql, lim_sql=limit_sql)

        db = MyDatabase()
        data = db.execute(sql, key_value)
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

            thread_list.append(thread_dict)

        return [json.dumps({"code": 0, "response": thread_list}, indent=4)]

    @staticmethod
    def create(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'thread.create'"}, indent=4)]

        request_body = json.loads(request_body)

        # Required
        forum = request_body.get('forum')
        forum = try_encode(forum)
        title = request_body.get('title')
        title = try_encode(title)
        is_closed_key = request_body.get('isClosed')
        if is_closed_key:
            is_closed = 1
        else:
            is_closed = 0
        user = request_body.get('user')
        date = request_body.get('date')
        message = request_body.get('message')
        message = try_encode(message)
        slug = request_body.get('slug')
        slug = try_encode(slug)

        # Optional
        is_deleted_key = request_body.get('isDeleted', False)
        if is_deleted_key:
            is_deleted = 1
        else:
            is_deleted = 0

        sql = """INSERT INTO Thread (forum, title, isClosed, user, date, \
            message, slug, isDeleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
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
    def remove(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def open(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def close(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def restore(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def list_posts(qs_dict):
        # TODO
        return True

    @staticmethod
    def update(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def subscribe(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def unsubscribe(html_method, request_body):
        # TODO
        return True

    @staticmethod
    def vote(html_method, request_body):
        # TODO
        return True
