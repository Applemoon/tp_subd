from Database import Database


class Post:
	def doMethod(self, db_method, html_method, request_body, qs_dict):
		if db_method == 'list':
			return self.list(html_method, request_body)
		elif db_method == 'create':
			return self.create(html_method, request_body)
		elif db_method == 'details':
			return self.details(html_method, request_body)
		elif db_method == 'remove':
			return self.remove(html_method, request_body)
		elif db_method == 'restore':
			return self.restore(html_method, request_body)
		elif db_method == 'update':
			return self.update(html_method, request_body)
		elif db_method == 'vote':
			return self.vote(html_method, request_body)

		return 'error: unknown post db method'


	def list(self, html_method, request_body):
		# TODO
		return True


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return ['error: wrong html method for "post.create"']

		# TODO build request using request_body
		sql = """ """ #TODO
		db = Database()
		db.execute(sql, True)
		data =  db.cursor.fetchall()
		return [json.dumps({
    "code": 0,
    "response": {
        "date": "2014-01-01 00:00:01",
        "forum": "forum1",
        "id": 1,
        "isClosed": True,
        "isDeleted": True,
        "message": "hey hey hey hey!",
        "slug": "Threadwithsufficientlylargetitle",
        "title": "Thread With Sufficiently Large Title",
        "user": "example3@mail.ru"
    }}, separators=(',',':'))] #TODO


	def details(self, html_method, request_body):
		# TODO
		return True


	def remove(self, html_method, request_body):
		# TODO
		return True


	def restore(self, html_method, request_body):
		# TODO
		return True


	def update(self, html_method, request_body):
		# TODO
		return True


	def vote(self, html_method, request_body):
		# TODO
		return True