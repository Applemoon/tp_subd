import Database


class Thread:
	def doMethod(self, db_method):
		if db_method == 'list':
			return self.list(html_method, request_body)
		elif db_method == 'create':
			return self.create(html_method, request_body)
		elif db_method == 'details':
			return self.details(html_method, request_body)
		elif db_method == 'remove':
			return self.remove(html_method, request_body)
		elif db_method == 'open':
			return self.open(html_method, request_body)
		elif db_method == 'close':
			return self.close(html_method, request_body)
		elif db_method == 'restore':
			return self.restore(html_method, request_body)
		elif db_method == 'listPosts':
			return self.listPosts(html_method, request_body)
		elif db_method == 'update':
			return self.update(html_method, request_body)
		elif db_method == 'subscribe':
			return self.subscribe(html_method, request_body)
		elif db_method == 'unsubscribe':
			return self.unsubscribe(html_method, request_body)
		elif db_method == 'vote':
			return self.vote(html_method, request_body)

		return 'error: unknown thread db method'


	def list(self, html_method, request_body):
		# TODO
		return true


	def create(self, html_method, request_body):
		if html_method != 'POST':
			return ['error: wrong html method for "thread.create"']

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


	def remove(self, html_method, request_body):
		# TODO
		return true


	def open(self, html_method, request_body):
		# TODO
		return true


	def close(self, html_method, request_body):
		# TODO
		return true


	def restore(self, html_method, request_body):
		# TODO
		return true


	def listPosts(self, html_method, request_body):
		# TODO
		return true


	def update(self, html_method, request_body):
		# TODO
		return true


	def subscribe(self, html_method, request_body):
		# TODO
		return true


	def unsubscribe(self, html_method, request_body):
		# TODO
		return true


	def vote(self, html_method, request_body):
		# TODO
		return true