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

		sql = """SELECT thread FROM Thread \
			WHERE title = '{title_value}';""".format(title_value = title);
		db = Database()
		data = db.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not data[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		data = data[0]
		
		thread_dict = dict()
		for field in data:
			thread_dict["id"] = strToJson(data[0])		
			thread_dict["forum"] = strToJson(forum)
			thread_dict["title"] = strToJson(title)
			thread_dict["isClosed"] = strToJson(isClosed, True)
			thread_dict["user"] = strToJson(user)
			thread_dict["date"] = strToJson(date)
			thread_dict["message"] = strToJson(message)
			thread_dict["slug"] = strToJson(slug)
			thread_dict["isDeleted"] = strToJson(isDeleted, True)

		return [json.dumps({"code": 0, "response": thread_dict}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('thread'):
			return [json.dumps({ "code": 2, "response": "No 'thread' key"}, indent=4)]

		sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
			date, slug, likes, dislikes, points FROM Thread \
			WHERE thread = {thread_id};""".format(thread_id = qs_dict['thread'][0])
		
		dbase = Database()
		data = dbase.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not data[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		thread_details = data[0]
		thread_dict = dict()
		thread_dict['id'] = strToJson(thread_details[0])
		thread_dict['title'] = strToJson(thread_details[1])
		thread_dict['user'] = strToJson(thread_details[2])
		thread_dict['message'] = strToJson(thread_details[3])
		thread_dict['forum'] = strToJson(thread_details[4])
		thread_dict['isDeleted'] = strToJson(thread_details[5], True)
		thread_dict['isClosed'] = strToJson(thread_details[6], True)
		date = thread_details[7].strftime('%Y-%m-%d %H:%M:%S')
		thread_dict['date'] = strToJson(date)
		thread_dict['slug'] = strToJson(thread_details[8])
		thread_dict['likes'] = strToJson(thread_details[9])
		thread_dict['dislikes'] = strToJson(thread_details[10])
		thread_dict['points'] = strToJson(thread_details[11])

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
			sql = """SELECT Forum.forum, Forum.name, Forum.short_name, Forum.user \
				FROM Forum \
				JOIN Thread ON Forum.short_name = Thread.forum \
				WHERE Thread.thread = '{}';""".format(thread_details[0])
			dbase = Database()
			forum_data = dbase.execute(sql)
			if not forum_data:
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
			if not forum_data[0]:
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

			forum_data = forum_data[0]
			forum_dict = dict()
			forum_dict['id'] = strToJson(forum_data[0])
			forum_dict['name'] = strToJson(forum_data[1])
			forum_dict['short_name'] = strToJson(forum_data[2])
			forum_dict['user'] = strToJson(forum_data[3])
			thread_dict['forum'] = strToJson(forum_dict)

		if user_related:
			sql = """SELECT User.user, User.email, User.name, User.username, \
				User.isAnonymous, User.about FROM User \
				JOIN Thread ON User.email = Thread.user
				WHERE Thread.thread = '{}';""".format(thread_details[0])
			dbase = Database()
			user_data = dbase.execute(sql)
			if not user_data:
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
			if not user_data[0]:
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

			user_data = user_data[0]
			user_dict = dict()
			user_dict['id'] = strToJson(user_data[0])
			user_dict['email'] = strToJson(user_data[1])
			user_dict['name'] = strToJson(user_data[2])
			user_dict['username'] = strToJson(user_data[3])
			user_dict['isAnonymous'] = strToJson(user_data[4], True)
			user_dict['about'] = strToJson(user_data[5])
			thread_dict['user'] = strToJson(user_dict)

		return [json.dumps({"code": 0, "response": thread_dict}, indent=4)]


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