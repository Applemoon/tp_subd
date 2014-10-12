from Database import Database


class User:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
		if db_method == 'create':
			return self.create(html_method, request_body)
		elif db_method == 'details':
			return self.details(html_method, request_body)
		elif db_method == 'follow':
			return self.follow(html_method, request_body)
		elif db_method == 'unfollow':
			return self.unfollow(html_method, request_body)
		elif db_method == 'listPosts':
			return self.listPosts(html_method, request_body)
		elif db_method == 'updateProfile':
			return self.updateProfile(html_method, request_body)
		elif db_method == 'listFollowers':
			return self.listFollowers(html_method, request_body)
		elif db_method == 'listFollowing':
			return self.listFollowing(html_method, request_body)

		return [json.dumps({ "code": 3, "response": "Unknown user db method"}, indent=4)]


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return [json.dumps({ "code": 3, "response": "Wrong html method for 'user.create'"}, indent=4)]

		# TODO
		return True


	def details(self, html_method, request_body):
		# TODO
		return True


	def follow(self, html_method, request_body):
		# TODO
		return True


	def unfollow(self, html_method, request_body):
		# TODO
		return True


	def listPosts(self, html_method, request_body):
		# TODO
		return True


	def updateProfile(self, html_method, request_body):
		# TODO
		return True


	def listFollowers(self, html_method, request_body):
		# TODO
		return True


	def listFollowing(self, html_method, request_body):
		# TODO
		return True


		