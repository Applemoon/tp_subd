import MySQLdb
import json

from MyDatabase import MyDatabase
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
			VALUES (%s, %s, %s, %s, %s);"""
		args = (username, about, name, email, isAnonymous)
		db = MyDatabase()

		try :
			db.execute(sql, args, True)
		except MySQLdb.IntegrityError, message:
			errorcode = message[0]
			if errorcode == MYSQL_DUPLICATE_ENTITY_ERROR:
				return [json.dumps({ "code": 5, 
					"response": "This user already exists"}, indent=4)]
			else:
				return [json.dumps({ "code": 4, 
					"response": "Oh, we have some realy bad error"}, indent=4)]

		user_dict = getUserDict(email)

		return [json.dumps({"code": 0, "response": user_dict}, indent=4)]


	def details(self, qs_dict):
		if not qs_dict.get('user'):
			return [json.dumps({ "code": 2, "response": "No 'user' key"}, indent=4)]

		email = qs_dict['user'][0]
		user_dict = getUserDict(email)

		sql = """SELECT follower FROM Follower WHERE following = %s;"""
		args = (email)
		dbase = MyDatabase()		
		followers_list = dbase.execute(sql, args)
		user_dict['followers'] = followers_list

		sql = """SELECT following FROM Follower WHERE follower = %s;"""
		args = (email)
		dbase = MyDatabase()		
		following_list = dbase.execute(sql, args)
		user_dict['following'] = following_list

		sql = """SELECT thread FROM Subscription WHERE subscriber = %s;"""
		dbase = MyDatabase()		
		subscriptions_list = dbase.execute(sql, (email))
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


		