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

		sql = """SELECT forum, name, short_name, user FROM `tp_subd`.`Forum` \
			WHERE forum = '{forum_name}';""".format(forum_name = qs_dict['forum'][0])
		dbase = Database()		
		forum_data = dbase.execute(sql)
		if not forum_data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		forum_details = forum_data[0]
		user = forum_details[3]

		if qs_dict.get('related') and qs_dict.get('related')[0] == 'user':
			sql = """SELECT about, email,\
				user, isAnonimous, name, \
				# , subscriptions, \ #TODOs
				username \
				FROM `tp_subd`.`User` \
				WHERE email = '{user_email}';""".format(user_email = forum_details[3])
			dbase2 = Database()		
			user_data = dbase2.execute(sql)
			user_details = user_data[0]

			user = dict()
			user['about'] = user_details[0]
			user['email'] = user_details[1]
			# user['followers'] = user_details[2] #TODO
			# user['following'] = user_details[3] #TODO
			user['id'] = user_details[2]
			user['isAnonymous'] = user_details[3]
			user['name'] = user_details[4]
			# user['subscriptions'] = user_details[5] #TODO
			user['username'] = user_details[5]
		
		return [json.dumps({
			"code": 0,
			"response": {
				"id": forum_details[0],
				"name": forum_details[1],
				"short_name": forum_details[2],
				"user": user
			}}, indent=4)]
		

	def listPosts(self, qs_dict):
		if not qs_dict.get('forum'):
			return [json.dumps({ "code": 2, "response": "No 'forum' key"}, indent=4)]

		since_sql = ''
		if qs_dict.get('since'):
			since_sql = """AND Post.date > '{}'""".format(qs_dict['since'][0])

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

		# TODO sort
		sort = 'flat'
		if qs_dict.get('sort'):
			sort = qs_dict['sort'][0]
			if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
				return [json.dumps({ "code": 3, "response": "Wrong sort value"}, indent=4)]
		# sort_sql = """ORDER BY Post.date {}""".format(sort)
		sort_sql = """"""
		
		order = 'desc'
		if qs_dict.get('order'):
			order = qs_dict['order'][0]
			if order != 'asc' and order != 'desc':
				return [json.dumps({ "code": 3, "response": "Wrong order value"}, indent=4)]
		order_sql = """ORDER BY Post.date {}""".format(order)

		# TODO related

		sql = """SELECT Post.post, Post.user, Post.thread, Post.forum, Post.message, Post.parent, Post.date, \
			Post.likes, Post.dislikes, Post.isSpam, Post.isEdited, Post.isDeleted, Post.isHighlighted, Post.isApproved \
			FROM `tp_subd`.`Post` \
			JOIN Thread ON Post.thread = Thread.thread \
			JOIN Forum ON Forum.short_name = Thread.forum \
			WHERE Forum.short_name = '{short_name_value}' {sd_sql} {lim_sql} {ord_sql} {srt_sql};""".format( \
				short_name_value = qs_dict['forum'][0], \
				sd_sql = since_sql, \
				lim_sql = limit_sql,
				ord_sql = order_sql,
				srt_sql = sort_sql)
		print sql # TODO delete
		dbase = Database()		
		data = dbase.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		post_list = list()
		for post in data:
			post_dict = dict()
			post_dict['id'] = post[0] 
			post_dict['user'] = post[1] 
			post_dict['thread'] = post[2] 
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
		# TODO
		return True


	def listUsers(self, qs_dict):
		# TODO
		return True