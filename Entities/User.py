import MySQLdb
import json

from Database import Database
from common import *


class User:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
		if db_method == 'create':
			return self.create(html_method, request_body)
		elif db_method == 'details':
			return self.details(qs_dict)
		elif db_method == 'follow':
			return self.follow(html_method, request_body)
		elif db_method == 'unfollow':
			return self.unfollow(html_method, request_body)
		elif db_method == 'listPosts':
			return self.listPosts(qs_dict)
		elif db_method == 'updateProfile':
			return self.updateProfile(html_method, request_body)
		elif db_method == 'listFollowers':
			return self.listFollowers(qs_dict)
		elif db_method == 'listFollowing':
			return self.listFollowing(qs_dict)

		return [json.dumps({ "code": 3, "response": "Unknown user db method"}, indent=4)]


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, 
				"response": "Wrong html method for 'user.create'"}, indent=4)]

		request_body = json.loads(request_body)
		username = request_body.get('username')
		username = tryEncode(username)
		about = request_body.get('about')
		name = request_body.get('name')
		name = tryEncode(name)
		email = request_body.get('email')
		isAnonymousKey = request_body.get('isAnonymous', False)
		if isAnonymousKey:
			isAnonymous = 1
		else:
			isAnonymous = 0
		sql = """INSERT INTO User (username, about, name, email, isAnonymous) \
			VALUES ('{username_value}', '{about_value}', \
			'{name_value}', '{email_value}', {isAnonymous_value});""".format( \
			username_value = username, about_value = about, name_value = name, 
			email_value = email, isAnonymous_value = isAnonymous)
		db = Database()

		try :
			db.execute(sql, True)
		except MySQLdb.IntegrityError, message:
			errorcode = message[0]
			if errorcode == MYSQL_DUPLICATE_ENTITY_ERROR:
				return [json.dumps({ "code": 5, 
					"response": "This user already exists"}, indent=4)]
			else:
				return [json.dumps({ "code": 4, 
					"response": "Oh, we have some realy bad error"}, indent=4)]

		sql = """SELECT user FROM User \
			WHERE email = '{email_value}';""".format(email_value = email);
		db2 = Database()
		data = db2.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		if not data[0]:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]
		data = data[0]
		
		user_dict = dict()
		for field in data:
			user_dict["about"] = strToJson(about)
			user_dict["email"] = strToJson(email)
			user_dict["id"] = strToJson(data[0])
			user_dict["isAnonymous"] = strToJson(isAnonymous, True)
			user_dict["name"] = strToJson(name)
			user_dict["username"] = strToJson(username)

		return [json.dumps({"code": 0, "response": user_dict}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('user'):
			return [json.dumps({ "code": 2, "response": "No 'user' key"}, indent=4)]

		email = qs_dict['user'][0]
		sql = """SELECT user, name, username, email, about, isAnonymous FROM User \
			WHERE email = '{}';""".format(email)
		dbase = Database()		
		data = dbase.execute(sql)
		if not data:
			return [json.dumps({ "code": 1, "response": "Empty set"}, indent=4)]

		user_details = data[0]
		user_dict = dict()
		user_dict['id'] = strToJson(user_details[0])
		user_dict['name'] = strToJson(user_details[1])
		user_dict['username'] = strToJson(user_details[2])
		user_dict['email'] = strToJson(user_details[3])
		user_dict['about'] = strToJson(user_details[4])
		user_dict['isAnonymous'] = strToJson(user_details[5], True)

		sql = """SELECT follower FROM Follower WHERE following = '{}';""".format(email)
		dbase = Database()		
		followers_list = dbase.execute(sql)
		user_dict['followers'] = followers_list

		sql = """SELECT following FROM Follower WHERE follower = '{}';""".format(email)
		dbase = Database()		
		following_list = dbase.execute(sql)
		user_dict['following'] = following_list

		sql = """SELECT Subscription.thread FROM Subscription \
			JOIN Thread ON Thread.thread = Subscription.thread
			WHERE Subscription.subscriber = '{}';""".format(email)
		dbase = Database()		
		subscriptions_list = dbase.execute(sql)
		user_dict['subscriptions'] = subscriptions_list
		
		return [json.dumps({"code": 0, "response": user_dict}, indent=4)]


	def follow(self, html_method, request_body):
		# TODO
		return True


	def unfollow(self, html_method, request_body):
		# TODO
		return True


	def listPosts(self, qs_dict):
		# TODO
		return True


	def updateProfile(self, html_method, request_body):
		# TODO
		return True


	def listFollowers(self, qs_dict):
		# TODO
		return True


	def listFollowing(self, qs_dict):
		# TODO
		return True


		