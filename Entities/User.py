import Database


class User:
	def doMethod(self, db_method, html_method, request_body):
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

		return 'error: unknown user db_method'


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return ['error: wrong html method for "user.create"']

		# TODO build request using request_body
		sql = """ """ #TODO
		db = Database()
		db.execute(sql, true)
		data =  db.cursor.fetchall()
		return [json.dumps({
    "code": 0,
    "response": {
        "date": "2014-01-01 00:00:01",
        "forum": "forum1",
        "id": 1,
        "isClosed": true,
        "isDeleted": true,
        "message": "hey hey hey hey!",
        "slug": "Threadwithsufficientlylargetitle",
        "title": "Thread With Sufficiently Large Title",
        "user": "example3@mail.ru"
    }}, separators=(',',':'))] #TODO


	def details(self, html_method, request_body):
		# TODO
		return true


	def follow(self, html_method, request_body):
		# TODO
		return true


	def unfollow(self, html_method, request_body):
		# TODO
		return true


	def listPosts(self, html_method, request_body):
		# TODO
		return true


	def updateProfile(self, html_method, request_body):
		# TODO
		return true


	def listFollowers(self, html_method, request_body):
		# TODO
		return true


	def listFollowing(self, html_method, request_body):
		# TODO
		return true


		