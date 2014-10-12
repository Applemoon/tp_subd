import MySQLdb
import json
import ast

from Database import Database


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
			return [json.dumps({ "code": 3, "response": "Wrong html method for 'forum.create'"}, indent=4)]

		request_body = ast.literal_eval(request_body)
		name = request_body.get('name')
		short_name = request_body.get('short_name')
		user = request_body.get('user')
		sql = """INSERT INTO Forum (name, short_name, user) \
			VALUES ('{name_value}', '{short_name_value}', '{user_value}');""".format( \
				name_value = name, short_name_value = short_name, user_value = user)
		db = Database()
		db.execute(sql, True)

		sql = """SELECT forum FROM `tp_subd`.`Forum` \
			WHERE name = '{name_value}';""".format(name_value = name);
		db2 = Database()
		data = db2.execute(sql)
		if not data and not data[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		data = data[0]
		return [json.dumps({
			"code": 0,
			"response": {
				"id": data[0],
				"name": name,
				"short_name": short_name,
				"user": user
			}}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

		sql = """SELECT forum, name, short_name, user FROM Forum \
			WHERE forum = '{forum_name}';""".format(forum_name = qs_dict['forum'][0])
		dbase = Database()		
		data = dbase.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		forum_details = data[0]
		user = forum_details[3]

		if qs_dict.get('related') and qs_dict.get('related')[0] == 'user':
			sql = """SELECT about, email, user, isAnonymous, name, username \
				FROM `tp_subd`.`User` \
				WHERE email = '{user_email}';""".format(user_email = forum_details[3])
			dbase = Database()		
			user_data = dbase.execute(sql)
			user_details = user_data[0]

			user = dict()
			user['about'] = user_details[0]
			user['email'] = user_details[1]

			sql = """SELECT follower FROM Followers WHERE following = '{}'""".format(user_details[1])
			dbase = Database()
			data = dbase.execute(sql)
			data_list = list()
			for line in data:
				data_list.append(line[0])
			user['followers'] = data_list

			sql = """SELECT following FROM Followers WHERE follower = '{}'""".format(user_details[1])
			dbase = Database()
			data = dbase.execute(sql)
			data_list = list()
			for line in data:
				data_list.append(line[0])
			user['following'] = data_list

			user['id'] = user_details[2]
			user['isAnonymous'] = user_details[3]
			user['name'] = user_details[4]
			user['username'] = user_details[5]

			sql = """SELECT thread FROM Subscription \
				WHERE subscriber = '{}'""".format(user_details[1])
			dbase = Database()
			data = dbase.execute(sql)
			data_list = list()
			for line in data:
				data_list.append(line[0])
			user['subscriptions'] = data_list
		
		forum_dict = dict()
		forum_dict['id'] = forum_details[0]
		forum_dict['name'] = forum_details[1]
		forum_dict['short_name'] = forum_details[2]
		forum_dict['user'] = user

		return [json.dumps({"code": 0, "response": forum_dict}, indent=4)]
		

	def listPosts(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

		# Since part
		since_sql = ''
		if qs_dict.get('since'):
			since_sql = """AND Post.date > ='{}'""".format(qs_dict['since'][0])

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

		# TODO Sort part
		sort = 'flat'
		if qs_dict.get('sort'):
			sort = qs_dict['sort'][0]
			if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
				return [json.dumps({ "code": 3, "response": "Wrong sort value"}, indent=4)]
		# sort_sql = """ORDER BY Post.date {}""".format(sort)
		sort_sql = """"""
		
		# Order part
		order = 'desc'
		if qs_dict.get('order'):
			order = qs_dict['order'][0]
			if order != 'asc' and order != 'desc':
				return [json.dumps({ "code": 3, "response": "Wrong order value"}, indent=4)]
		order_sql = """ORDER BY Post.date {}""".format(order)

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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, indent=4)]

		sql = """SELECT Post.post, Post.user, Post.thread, Post.forum, Post.message, \
			Post.parent, Post.date, Post.likes, Post.dislikes, Post.isSpam, Post.isEdited, \
			Post.isDeleted, Post.isHighlighted, Post.isApproved \
			FROM `tp_subd`.`Post` \
			JOIN Thread ON Post.thread = Thread.thread \
			JOIN Forum ON Forum.short_name = Thread.forum \
			WHERE Forum.short_name = '{short_name_value}' {snc_sql} {lim_sql} {ord_sql} {srt_sql};""".format(
				short_name_value = qs_dict['forum'][0], \
				snc_sql = since_sql,
				lim_sql = limit_sql,
				ord_sql = order_sql,
				srt_sql = sort_sql)
		dbase = Database()		
		data = dbase.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		post_list = list()
		for post in data:
			post_dict = dict()
			post_dict['id'] = post[0]

			if user_related:
				sql = """SELECT user, email, name, username, isAnonymous, about FROM User \
					WHERE email = '{post_email}';""".format(post_email = post[1])
				dbase = Database()
				user_data = dbase.execute(sql)
				if not user_data:
					return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
				user_data = user_data[0]
				user_dict = dict()
				user_dict['id'] = user_data[0]
				user_dict['email'] = user_data[1]
				user_dict['name'] = user_data[2]
				user_dict['username'] = user_data[3]
				user_dict['isAnonymous'] = user_data[4]
				user_dict['about'] = user_data[5]
				post_dict['user'] = user_dict
			else:
				post_dict['user'] = post[1]

			if thread_related:
				sql = """SELECT thread, title, user, message, forum, isDeleted, \
					isClosed, date, slug FROM Thread \
					WHERE thread = {post_thread};""".format(post_thread = post[2])
				dbase = Database()
				thread_data = dbase.execute(sql)
				if not thread_data:
					return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
				thread_data = thread_data[0]
				thread_dict = dict()
				thread_dict['id'] = thread_data[0]
				thread_dict['title'] = thread_data[1]
				thread_dict['user'] = thread_data[2]
				thread_dict['message'] = thread_data[3]
				thread_dict['forum'] = thread_data[4]
				thread_dict['isDeleted'] = thread_data[5]
				thread_dict['isClosed'] = thread_data[6]
				thread_dict['data'] = thread_data[7].strftime('%Y-%m-%d %H:%M:%S')
				thread_dict['slug'] = thread_data[8]
				post_dict['thread'] = thread_dict
			else:
				post_dict['thread'] = post[2]

			if forum_related:
				sql = """SELECT forum, name, short_name, user FROM Forum \
					WHERE short_name = '{post_forum}';""".format(post_forum = post[3])
				dbase = Database()
				forum_data = dbase.execute(sql)
				if not forum_data:
					return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
				forum_data = forum_data[0]
				forum_dict = dict()
				forum_dict['id'] = forum_data[0]
				forum_dict['name'] = forum_data[1]
				forum_dict['short_name'] = forum_data[2]
				forum_dict['user'] = forum_data[3]
				post_dict['forum'] = forum_dict
			else:
				post_dict['forum'] = post[3]

			post_dict['message'] = post[4]
			post_dict['parent'] = post[5]
			post_dict['date'] = post[6].strftime('%Y-%m-%d %H:%M:%S')
			post_dict['likes'] = post[7]
			post_dict['dislikes'] = post[8]
			post_dict['isSpam'] = post[9]
			post_dict['isEdited'] = post[10]
			post_dict['isDeleted'] = post[11]
			post_dict['isHighlighted'] = post[12]
			post_dict['isApproved'] = post[13]
			post_list.append(post_dict)

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
					return [json.dumps({ "code": 3, "response": "Wrong related value"}, indent=4)]

		sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, \
			date, slug FROM Thread \
			WHERE forum = '{forum_value}' {snc_sql} {ord_sql} {lim_sql};""".format(
				forum_value = qs_dict['forum'][0], 
				snc_sql = since_sql, 
				lim_sql = limit_sql,
				ord_sql = order_sql)
		db = Database()
		data = db.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		thread_list = list()
		for thread in data:
			thread_dict = dict()
			thread_dict['id'] = thread[0]
			thread_dict['title'] = thread[1]
			
			if user_related:
				sql = """SELECT user, email, name, username, isAnonymous, about FROM User \
					WHERE email = '{thread_email}';""".format(thread_email = thread[2])
				dbase = Database()
				user_data = dbase.execute(sql)
				if not user_data:
					return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
				user_data = user_data[0]
				user_dict = dict()
				user_dict['id'] = user_data[0]
				user_dict['email'] = user_data[1]
				user_dict['name'] = user_data[2]
				user_dict['username'] = user_data[3]
				user_dict['isAnonymous'] = user_data[4]
				user_dict['about'] = user_data[5]
				thread_dict['user'] = user_dict
			else:
				thread_dict['user'] = thread[2]

			thread_dict['message'] = thread[3]

			if forum_related:
				sql = """SELECT forum, name, short_name, user FROM Forum \
					WHERE short_name = '{thread_forum}';""".format(thread_forum = thread[4])
				dbase = Database()
				forum_data = dbase.execute(sql)
				if not forum_data:
					return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
				forum_data = forum_data[0]
				forum_dict = dict()
				forum_dict['id'] = forum_data[0]
				forum_dict['name'] = forum_data[1]
				forum_dict['short_name'] = forum_data[2]
				forum_dict['user'] = forum_data[3]
				thread_dict['forum'] = forum_dict
			else:
				thread_dict['forum'] = thread[4]

			thread_dict['isDeleted'] = thread[5]
			thread_dict['isClosed'] = thread[6]
			thread_dict['date'] = thread[7].strftime('%Y-%m-%d %H:%M:%S')
			thread_dict['slug'] = thread[8]
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
				return [json.dumps({ "code": 3, "response": "Wrong since_id value"}, indent=4)]
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

		sql = """SELECT User.user, User.email, User.name, User.username, User.isAnonymous, \
			User.about FROM User \
			JOIN Post ON Post.user = User.email \
			WHERE Post.forum = '{forum_value}' {snc_sql} {ord_sql} {lim_sql};""".format(
				forum_value = qs_dict['forum'][0], 
				snc_sql = since_id_sql, 
				lim_sql = limit_sql,
				ord_sql = order_sql)
		print sql
		db = Database()
		data = db.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		user_list = list()
		for user in data:
			user_dict = dict()
			user_dict['id'] = user[0]
			user_dict['email'] = user[1]
			user_dict['name'] = user[2]
			user_dict['username'] = user[3]
			user_dict['isAnonymous'] = user[4]
			user_dict['about'] = user[5]
			user_list.append(user_dict)

		return [json.dumps({ "code": 0, "response": user_list}, indent=4)]
