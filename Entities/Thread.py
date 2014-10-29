import MySQLdb
import json

from Database import Database
from common import *


class Thread:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
		if db_method == 'list':
			return self.list(html_method, request_body)
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
			return self.listPosts(qs_dict)
		elif db_method == 'update':
			return self.update(html_method, request_body)
		elif db_method == 'subscribe':
			return self.subscribe(html_method, request_body)
		elif db_method == 'unsubscribe':
			return self.unsubscribe(html_method, request_body)
		elif db_method == 'vote':
			return self.vote(html_method, request_body)

		return [json.dumps({ "code": 3, "response": "Unknown thread db method"}, indent=4)]


	def list(self, html_method, request_body):
		# TODO
		return True


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'thread.create'"}, indent=4)]

		request_body = json.loads(request_body)

		# Requried
		forum = request_body.get('forum')
		forum = tryEncode(forum)
		title = request_body.get('title')
		title = tryEncode(title)
		isClosedKey = request_body.get('isClosed')
		if isClosedKey:
			isClosed = 1
		else:
			isClosed = 0
		user = request_body.get('user')
		date = request_body.get('date')
		message = request_body.get('message')
		message = tryEncode(message)
		slug = request_body.get('slug')
		slug = tryEncode(slug)

		# Optional
		isDeletedKey = request_body.get('isDeleted', False)
		if isDeletedKey:
			isDeleted = 1
		else:
			isDeleted = 0

		sql = """INSERT INTO Thread (forum, title, isClosed, user, date, \
			message, slug, isDeleted) \
			VALUES ('{forum_value}', '{title_value}', {isClosed_value}, '{user_value}', \
			'{date_value}', '{message_value}', '{slug_value}', \
			{isDeleted_value});""".format( \
				forum_value = forum, title_value = title, isClosed_value = isClosed, 
				user_value = user, date_value = date, message_value = message, 
				slug_value = slug, isDeleted_value = isDeleted)
		db = Database()

		try :
			db.execute(sql, True)
		except MySQLdb.IntegrityError, message:
			errorcode = message[0]
			if errorcode == MYSQL_DUPLICATE_ENTITY_ERROR:
				return [json.dumps({ "code": 5, 
					"response": "This thread already exists"}, indent=4)]
			else:
				return [json.dumps({ "code": 4, 
					"response": "Oh, we have some realy bad error"}, indent=4)]

		thread_list = getThreadList(title = title)
		if thread_list == list():
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		return [json.dumps({"code": 0, "response": thread_list[0]}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('thread'):
			return [json.dumps({ "code": 2, "response": "No 'thread' key"}, indent=4)]

		id = qs_dict['thread'][0]
		thread_list = getThreadList(id = id)
		if thread_list == list():
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, \
						indent=4)]

		if forum_related:
			thread['forum'] = getForumDict(short_name = thread['forum'])

		if user_related:
			thread['user'] = getUserDict(thread['user'])

		return [json.dumps({"code": 0, "response": thread}, indent=4)]


	def remove(self, html_method, request_body):
		# TODO
		return True


	def open(self, html_method, request_body):
		# TODO
		return True


	def close(self, html_method, request_body):
		# TODO
		return True


	def restore(self, html_method, request_body):
		# TODO
		return True


	def listPosts(qs_dict):
		# TODO
		return True


	def update(self, html_method, request_body):
		# TODO
		return True


	def subscribe(self, html_method, request_body):
		# TODO
		return True


	def unsubscribe(self, html_method, request_body):
		# TODO
		return True


	def vote(self, html_method, request_body):
		# TODO
		return True