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
			return self.listPosts(html_method, request_body)
		elif db_method == 'listThreads':
			return self.listThreads(html_method, request_body)
		elif db_method == 'listUsers':
			return self.listUsers(html_method, request_body)

		return 'error: unknown forum db method'


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return ['error: wrong html method for "forum.create"']

		request_body = ast.literal_eval(request_body)
		name = request_body.get('name')
		short_name = request_body.get('short_name')
		user = request_body.get('user')
		sql = """INSERT INTO Forum (name, short_name, user) \
			VALUES ('{name_value}', '{short_name_value}', '{user_value}');""".format( \
				name_value = name, short_name_value = short_name, user_value = user)
		db = Database()
		data = db.execute(sql, True)
		return [json.dumps({
			"code": 0,
			"response": {
				"id": ..., # TODO правильный id
				"name": name,
				"short_name": short_name,
				"user": user
			}})]


	def details(self, qs_dict):
		dbase = Database()
		forum_key = qs_dict.get('forum', False)
		if forum_key == False:
			return [json.dumps({ "code": 2, "response": "No 'forum' key"})]

		sql = """SELECT forum, name, short_name, user FROM `tp_subd`.`Forum` \
			WHERE forum = '{forum_name}';""".format(forum_name = qs_dict['forum'][0])
		forum_data = dbase.execute(sql)
		if not forum_data:
			return [json.dumps({ "code": 1, "response": "Empty set"})]

		forum_details = forum_data[0]

		related_key = qs_dict.get('related', '')
		if related_key == 'user':
			sql = """SELECT about, email, followers, following, \
				user, isAnonimous, name \
				# , subscriptions, \
				username \
			 	FROM `tp_subd`.`User` \
				WHERE email = '{user_email}';""".format(user_email = forum_details[2])
			cur.execute(sql)
			user_data = cur.fetchall()
			user_details = user_data[0]

			return [json.dumps({
				"code": 0,
				"response": {
					"id": 1,
					"name": forum_details[0],
					"short_name": forum_details[1],
					"user": {
						"about": user_details[2],
						"email": user_details[3],
						"followers": user_details[4],
						"following": user_details[5],
						"id": user_details[6],
						"isAnonymous": user_details[7],
						"name": user_details[8],
						# "subscriptions": user_details[9],
						# "username": user_details[10]
						"username": user_details[9]
					}
				}})] #TODO

		return [json.dumps({
			"code": 0,
			"response": {
				"id": forum_details[0],
				"name": forum_details[1],
				"short_name": forum_details[2],
				"user": forum_details[3]
			}})] #TODO
		

	def listPosts(self, html_method, request_body):
		# TODO
		return True


	def listThreads(self, html_method, request_body):
		# TODO
		return True


	def listUsers(self, html_method, request_body):
		# TODO
		return True