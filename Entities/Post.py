import json

from MyDatabase import MyDatabase
from common import *


class Post:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
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

		return [json.dumps({ "code": 3, "response": "Unknown post db method"}, indent=4)]


	def list(self, qs_dict):
		if not qs_dict.get('forum') or not qs_dict.get('thread'):
			return [json.dumps({ "code": 2, "response": "No 'forum' or 'thread' key"}, 
				indent=4)]

		# TODO


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'post.create'"}, indent=4)]

		# Requried
		request_body = json.loads(request_body)
		date = request_body.get('date')
		thread = request_body.get('thread')
		message = request_body.get('message')
		message = tryEncode(message)
		user = request_body.get('user')
		forum = request_body.get('forum')
		forum = tryEncode(forum)

		# Optional
		parent = request_body.get('parent', None)
		isApprovedKey = request_body.get('isApproved', False)
		if isApprovedKey:
			isApproved = 1
		else:
			isApproved = 0
		isHighlightedKey = request_body.get('isHighlighted', False)
		if isHighlightedKey:
			isHighlighted = 1
		else:
			isHighlighted = 0
		isEditedKey = request_body.get('isEdited', False)
		if isEditedKey:
			isEdited = 1
		else:
			isEdited = 0
		isSpamKey = request_body.get('isSpam', False)
		if isSpamKey:
			isSpam = 1
		else:
			isSpam = 0
		isDeletedKey = request_body.get('isDeleted', False)
		if isDeletedKey:
			isDeleted = 1
		else:
			isDeleted = 0

		sql = """INSERT INTO Post (user, thread, forum, message, parent, date, isSpam, \
			isEdited, isDeleted, isHighlighted, isApproved) \
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
		args = (user, thread, forum, message, parent, date, isSpam, isEdited, 
				isDeleted, isHighlighted, isApproved)

		db = MyDatabase()
		
		try :
			db.execute(sql, args, True)
		except MySQLdb.IntegrityError, message:
			print message[0]
		finally:
			post_list = getPostList(id = db.cursor.lastrowid)
			if post_list == list():
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
			if not post_list[0]:
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

			return [json.dumps({"code": 0, "response": post_list[0]}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('post'):
			return [json.dumps({ "code": 2, "response": "No 'post' key"}, indent=4)]

		id = qs_dict['post'][0]
		post_list = getPostList(id = id)
		if post_list == list():
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not post_list[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, \
						indent=4)]

		if thread_related:
			thread_list = getThreadList(id = post['thread'])
			if thread_list == list():
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
			else:
				post['thread'] = thread_list[0]

		if forum_related:
			post['forum'] = getForumDict(short_name = post['forum'])

		if user_related:
			post['user'] = getUserDict(post['user'])

		return [json.dumps({"code": 0, "response": post}, indent=4)]


	def remove(self, html_method, request_body, doRemove = True):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'post.remove'"}, indent=4)]

		request_body = json.loads(request_body)
		id = request_body.get('post')

		if doRemove:
			sql = """UPDATE Post SET isDeleted = 1 WHERE post = %s;"""
		else:
			sql = """UPDATE Post SET isDeleted = 0 WHERE post = %s;"""
		db = MyDatabase()
		db.execute(sql, (id), True)

		return [json.dumps({"code": 0, "response": {"post": id}}, indent=4)]


	def restore(self, html_method, request_body):
		return self.remove(html_method, request_body, False)


	def update(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'post.remove'"}, indent=4)]

		request_body = json.loads(request_body)
		id = request_body.get('post')
		message = request_body.get('message')

		sql = """UPDATE Post SET message = %s WHERE post = %s;"""

		db = MyDatabase()
		db.execute(sql, (message, id), True)

		post = getPostList(id = id)
		if not post:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not post[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		return [json.dumps({"code": 0, "response": post[0]}, indent=4)]


	def vote(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'post.remove'"}, indent=4)]

		request_body = json.loads(request_body)
		id = request_body.get('post')
		vote = request_body.get('vote')
		if vote != 1 and vote != -1:
			print "VERY BAD ERROR"
			# TODO return error

		if vote == 1:
			sql = """UPDATE Post SET likes = likes + 1 WHERE post = %s;"""
		else:
			sql = """UPDATE Post SET dislikes = dislikes + 1 WHERE post = %s;"""


		db = MyDatabase()
		db.execute(sql, (id), True)

		post = getPostList(id = id)
		if not post:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not post[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		return [json.dumps({"code": 0, "response": post[0]}, indent=4)]