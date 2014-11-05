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
			return self.listPosts(qs_dict)
		elif db_method == 'listThreads':
			return self.listThreads(qs_dict)
		elif db_method == 'listUsers':
			return self.listUsers(qs_dict)

		return [json.dumps({ "code": 3, "response": "Unknown forum db method"}, indent=4)]


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, "response": "Wrong html method \
				for 'forum.create'"}, indent=4)]

		request_body = json.loads(request_body)
		name = request_body.get('name')
		name = tryEncode(name)
		short_name = request_body.get('short_name')
		short_name = tryEncode(short_name)
		user = request_body.get('user')
		sql = """INSERT INTO Forum (name, short_name, user) VALUES (%s, %s, %s);"""	
		args = (name, short_name, user)
		db = MyDatabase()

		try :
			db.execute(sql, args, True)
		except MySQLdb.IntegrityError, message:
			print message[0]
		finally:
			forum_dict = dict()
			forum_dict['id'] = db.cursor.lastrowid
			forum_dict['name'] = name
			forum_dict['short_name'] = short_name
			forum_dict['user'] = user

			return [json.dumps({"code": 0, "response": forum_dict}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

		short_name = qs_dict['forum'][0]
		forum_dict = getForumDict(short_name = short_name)
		if forum_dict == dict():
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		if qs_dict.get('related') and qs_dict.get('related')[0] == 'user':
			user = getUserDict(forum_dict['user'])
			if user == dict():
				return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

			sql = """SELECT follower FROM Follower WHERE following = %s"""
			args = (user['email'])
			dbase = MyDatabase()
			data = dbase.execute(sql, args)
			
			followers_list = list()
			for line in data:
				followers_list.append(line[0])
			user['followers'] = followers_list

			sql = """SELECT following FROM Follower WHERE follower = %s"""
			args = (user['email'])
			dbase = MyDatabase()
			data = dbase.execute(sql, args)
			following_list = list()
			for line in data:
				following_list.append(line[0])
			user['following'] = strToJson(following_list)


			sql = """SELECT thread FROM Subscription WHERE subscriber = %s"""
			args = (user['email'])
			dbase = MyDatabase()
			data = dbase.execute(sql, args)
			data_list = list()
			for line in data:
				data_list.append(line[0])
			user['subscriptions'] = data_list
		
			forum_dict['user'] = user

		return [json.dumps({"code": 0, "response": forum_dict}, indent=4)]
		

	def listPosts(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, \
						indent=4)]

		if qs_dict.get('since'):
			since = qs_dict['since'][0]

		if qs_dict.get('limit'):
			limit = qs_dict['limit'][0]

		if qs_dict.get('sort'):
			sort = qs_dict['sort'][0]

		if qs_dict.get('order'):
			order = qs_dict['order'][0]

		post_list = getPostList(forum = qs_dict['forum'][0], since = since, limit = limit,
			sort = sort, order = order)

		if not post_list:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		if not post_list[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		post_list = list()
		for post in post_list:
			if user_related:
				post['user'] = getUserDict(post[1])

			if thread_related:
				post['thread'] = getThread(id = post[2])

			if forum_related:
				post['forum'] = getForumDict(short_name = post[3])
				
			post_list.append(post)

		return [json.dumps({ "code": 0, "response": post_list}, indent=4)]


	def listThreads(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

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
		order_sql = """ORDER BY Thread.date {}""".format(order)

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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, \
						indent=4)]

		sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
			date, slug FROM Thread \
			WHERE forum = %s {snc_sql} {ord_sql} {lim_sql};""".format(snc_sql = since_sql,
				ord_sql = order_sql, lim_sql = limit_sql)
		args = (qs_dict['forum'][0], since_sql, limit_sql, order_sql)

		db = MyDatabase()
		data = db.execute(sql, args)
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
			
			if user_related:
				sql = """SELECT user, email, name, username, isAnonymous, about FROM User \
					WHERE email = %s;"""
				args = (thread[2])
				dbase = MyDatabase()
				user_data = dbase.execute(sql, args)
				if not user_data:
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

			if forum_related:
				sql = """SELECT forum, name, short_name, user FROM Forum \
					WHERE short_name = %s;"""
				args = (thread[4])

				dbase = MyDatabase()
				forum_data = dbase.execute(sql, args)
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

			thread_list.append(thread_dict)

		return [json.dumps({ "code": 0, "response": thread_list}, indent=4)]


	def listUsers(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

		# Since id part
		since_id_sql = ''
		if qs_dict.get('since_id'):
			since_id = qs_dict['since_id'][0]
			try:
				since_id = int(since_id)
			except ValueError:
				return [json.dumps({ "code": 3, "response": "Wrong since_id value"}, \
					indent=4)]
			since_id_sql = """AND User.user >= '{}'""".format(since_id)

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
		order_sql = """ORDER BY User.name {}""".format(order)

		sql = """SELECT User.user, User.email, User.name, User.username, \
			User.isAnonymous, User.about FROM User \
			JOIN Post ON Post.user = User.email \
			WHERE Post.forum = %s {snc_sql} {ord_sql} {lim_sql};""".format(
				snc_sql = since_id_sql, 
				lim_sql = limit_sql,
				ord_sql = order_sql)
		args = (qs_dict['forum'][0])

		db = MyDatabase()
		data = db.execute(sql, args)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		user_list = list()
		for user in data:
			user_dict = dict()
			user_dict['id'] = strToJson(user[0])
			user_dict['email'] = strToJson(user[1])
			user_dict['name'] = strToJson(user[2])
			user_dict['username'] = strToJson(user[3])
			user_dict['isAnonymous'] = strToJson(user[4])
			user_dict['about'] = strToJson(user[5])
			user_list.append(user_dict)

		return [json.dumps({ "code": 0, "response": user_list}, indent=4)]
