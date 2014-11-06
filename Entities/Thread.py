import MySQLdb
import json

from MyDatabase import MyDatabase
from common import *


class Thread:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
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


	def list(self, qs_dict):
		if qs_dict.get('forum'):
			key = "forum"
		elif qs_dict.get('user'):
			key = "user"
		else:
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]
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
				return [json.dumps({ "code": 3, "response": "Wrong limit value"}, indent=4)]
			if limit < 0:
				return [json.dumps({ "code": 3, "response": "Wrong limit value"}, indent=4)]
			limit_sql = """LIMIT {}""".format(limit)

		# Order part
		order = 'desc'
		if qs_dict.get('order'):
			order = qs_dict['order'][0]
			if order != 'asc' and order != 'desc':
				return [json.dumps({ "code": 3, "response": "Wrong order value"}, indent=4)]
		order_sql = """ORDER BY date {}""".format(order)

		sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
			date, slug FROM Thread"""
		if key == "forum":
			sql += """ WHERE forum = %s"""
		else:
			sql += """ WHERE user = %s"""

		sql += """ {snc_sql} {ord_sql} {lim_sql};""".format(snc_sql = since_sql,
				ord_sql = order_sql, lim_sql = limit_sql)

		db = MyDatabase()
		data = db.execute(sql, (key_value))
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		thread_list = list()
		for thread in data:
			thread_dict = dict()
			thread_dict['id'] = strToJson(thread[0])
			thread_dict['title'] = strToJson(thread[1])
			thread_dict['user'] = strToJson(thread[2])
			thread_dict['message'] = strToJson(thread[3])
			thread_dict['forum'] = strToJson(thread[4])
			thread_dict['isDeleted'] = strToJson(thread[5], True)
			thread_dict['isClosed'] = strToJson(thread[6], True)
			date = thread[7].strftime('%Y-%m-%d %H:%M:%S')
			thread_dict['date'] = strToJson(date)
			thread_dict['slug'] = strToJson(thread[8])
		
			thread_list.append(thread_dict)

		return [json.dumps({ "code": 0, "response": thread_list}, indent=4)]


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
			message, slug, isDeleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
		args = (forum, title, isClosed, user, date, message, slug, isDeleted) 
		db = MyDatabase()

		try :
			db.execute(sql, args, True)
		except MySQLdb.IntegrityError, message:
			print message[0]
		finally:
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


	def listPosts(self, qs_dict):
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