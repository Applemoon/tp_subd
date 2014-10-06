import Database


class Forum:
	def doMethod(self, db_method, html_method, request_body):
		if db_method == 'create':
			return self.create(html_method, request_body)
		elif db_method == 'details':
			return self.details(html_method, request_body)
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

		# TODO build request using request_body
		# name = ...
		# short_name = ...
		# user = ...
		sql = """ """ #TODO
		db = Database()
		db.execute(sql, true)
		data =  db.cursor.fetchall()
		return [json.dumps({
			"code": 0,
			"response": {
			"id": 1,
			"name": name,
			"short_name": short_name,
			"user": user
			}}, separators=(',',':'))] #TODO


	def details(self, html_method, request_body):
		# TODO
		return true


	def listPosts(self, html_method, request_body):
		# TODO
		return true


	def listThreads(self, html_method, request_body):
		# TODO
		return true


	def listUsers(self, html_method, request_body):
		# TODO
		return true