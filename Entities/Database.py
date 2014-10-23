import MySQLdb
import json


class Database:
	def __init__(self):
		self.db = MySQLdb.connect(host="localhost", user="root", passwd="1", 
			db="tp_subd", charset='utf8')
		self.cursor = self.db.cursor()
		

	def execute(self, sql, post=False):
		self.cursor.execute(sql)
		if post:
			self.db.commit()
		self.db.close()
		return self.cursor.fetchall()


	def clear(self):
		sql = 'SET FOREIGN_KEY_CHECKS=0;' + \
		' TRUNCATE TABLE Forum;' + \
		' TRUNCATE TABLE User;' + \
		' TRUNCATE TABLE Post;' + \
		' TRUNCATE TABLE Thread;' + \
		' SET FOREIGN_KEY_CHECKS=1;'
		data = self.execute(sql)
		return [json.dumps({"code": 0, "response": "OK"})]

# TODO
# Exception _mysql_exceptions.OperationalError: 
# (2013, 'Lost connection to MySQL server during query') 
# in <bound method Cursor.__del__ of <MySQLdb.cursors.Cursor object at 0x7f380ccd73d0>>
# ignored