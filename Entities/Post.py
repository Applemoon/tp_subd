import MySQLdb
from common import *


class Post:
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
        elif db_method == 'restore':
            return self.restore(html_method, request_body)
        elif db_method == 'update':
            return self.update(html_method, request_body)
        elif db_method == 'vote':
            return self.vote(html_method, request_body)

        return [json.dumps({"code": 3, "response": "Unknown post db method"}, indent=4)]

    @staticmethod
    def list(qs_dict):
        if not qs_dict.get('forum') or not qs_dict.get('thread'):
            return [json.dumps({"code": 2, "response": "No 'forum' or 'thread' key"},
                               indent=4)]

        forum = qs_dict['forum'][0]
        thread = qs_dict['thread'][0]
        since = qs_dict.get('since', '')
        limit = qs_dict.get('limit', -1)
        order = qs_dict.get('order', 'desc')
        if forum != "":
            post_list = get_post_list(forum=forum, since=since, limit=limit, order=order)
        else:
            post_list = get_post_list(thread=thread, since=since, limit=limit, order=order)

        return [json.dumps({"code": 0, "response": post_list}, indent=4)]

    @staticmethod
    def create(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'post.create'"}, indent=4)]

        request_body = json.loads(request_body)

        # Required
        date = request_body.get('date')
        thread = request_body.get('thread')
        message = request_body.get('message')
        message = try_encode(message)
        user = request_body.get('user')
        forum = request_body.get('forum')
        forum = try_encode(forum)

        # Optional
        parent = request_body.get('parent', None)
        is_approved_key = request_body.get('isApproved', False)
        if is_approved_key:
            is_approved = 1
        else:
            is_approved = 0
        is_highlighted_key = request_body.get('isHighlighted', False)
        if is_highlighted_key:
            is_highlighted = 1
        else:
            is_highlighted = 0
        is_edited_key = request_body.get('isEdited', False)
        if is_edited_key:
            is_edited = 1
        else:
            is_edited = 0
        is_spam_key = request_body.get('isSpam', False)
        if is_spam_key:
            is_spam = 1
        else:
            is_spam = 0
        is_deleted_key = request_body.get('isDeleted', False)
        if is_deleted_key:
            is_deleted = 1
        else:
            is_deleted = 0

        sql = """INSERT INTO Post (user, thread, forum, message, parent, date, isSpam, \
            isEdited, isDeleted, isHighlighted, isApproved) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        args = (user, thread, forum, message, parent, date, is_spam, is_edited,
                is_deleted, is_highlighted, is_approved)

        db = MyDatabase()

        try:
            db.execute(sql, args, True)
        except MySQLdb.IntegrityError, message:
            print message[0]
        finally:
            post_list = get_post_list(id_value=db.cursor.lastrowid)
            if post_list == list():
                return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
            if not post_list[0]:
                return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

            return [json.dumps({"code": 0, "response": post_list[0]}, indent=4)]

    @staticmethod
    def details(qs_dict):
        if not qs_dict.get('post'):
            return [json.dumps({"code": 2, "response": "No 'post' key"}, indent=4)]

        post_id = qs_dict['post'][0]
        post_list = get_post_list(id_value=post_id)
        if post_list == list():
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        if not post_list[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        else:
            post = post_list[0]

        thread_related = False
        forum_related = False
        user_related = False
        if qs_dict.get('related'):
            for related_value in qs_dict['related']:
                if related_value == 'forum':
                    forum_related = True
                elif related_value == 'user':
                    user_related = True
                elif related_value == 'thread':
                    thread_related = True
                else:
                    return [json.dumps({"code": 3, "response": "Wrong related value"},
                                       indent=4)]

        if thread_related:
            thread_list = get_thread_list(id_value=post['thread'])
            if thread_list == list():
                return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
            else:
                post['thread'] = thread_list[0]

        if forum_related:
            post['forum'] = get_forum_dict(short_name=post['forum'])

        if user_related:
            post['user'] = get_user_dict(post['user'])

        return [json.dumps({"code": 0, "response": post}, indent=4)]

    @staticmethod
    def remove(html_method, request_body, do_remove=True):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'post.remove'"}, indent=4)]

        request_body = json.loads(request_body)
        post_id = request_body.get('post')

        if do_remove:
            sql = """UPDATE Post SET isDeleted = 1 WHERE post = %s;"""
        else:
            sql = """UPDATE Post SET isDeleted = 0 WHERE post = %s;"""
        db = MyDatabase()
        db.execute(sql, post_id, True)

        return [json.dumps({"code": 0, "response": {"post": post_id}}, indent=4)]

    def restore(self, html_method, request_body):
        return self.remove(html_method, request_body, False)

    @staticmethod
    def update(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3,
                                "response": "Wrong html method for 'post.remove'"}, indent=4)]

        request_body = json.loads(request_body)
        post_id = request_body.get('post')
        message = request_body.get('message')

        sql = """UPDATE Post SET message = %s WHERE post = %s;"""

        db = MyDatabase()
        db.execute(sql, (message, post_id), True)

        post = get_post_list(id_value=post_id)
        if not post:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        if not post[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        return [json.dumps({"code": 0, "response": post[0]}, indent=4)]

    @staticmethod
    def vote(html_method, request_body):
        if html_method != 'POST':
            return [json.dumps({"code": 3, "response": "Wrong html method for 'post.remove'"}, indent=4)]

        request_body = json.loads(request_body)
        post_id = request_body.get('post')
        vote = request_body.get('vote')
        if vote != 1 and vote != -1:
            return [json.dumps({"code": 3, "response": "Wrong 'vote' value'"}, indent=4)]

        if vote == 1:
            sql = """UPDATE Post SET likes = likes + 1, points = points + 1 WHERE post = %s;"""
        else:
            sql = """UPDATE Post SET dislikes = dislikes + 1, points = points - 1 WHERE post = %s;"""

        db = MyDatabase()
        db.execute(sql, post_id, True)

        post = get_post_list(id_value=post_id)
        if not post:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]
        if not post[0]:
            return [json.dumps({"code": 1, "response": "Empty set"}, indent=4)]

        return [json.dumps({"code": 0, "response": post[0]}, indent=4)]