class Database:
	def __init__(self):
		self.db = MySQLdb.connect(host="localhost", user="root", passwd="1", db="tp_subd", charset='utf8')
		self.cursor = db.cursor()
		


	def execute(self, sql, post=False):
		self.cursor.execute(sql)
		if post:
			self.db.commit()
		self.db.close()
		return self.cursor.fetchall()


	def clear(self):
		# TODO
		sql = """ """ # TODO
		data = self.execute(sql)
		return [json.dumps({"code": 0, "response": "OK"}, separators=(',',':'))]