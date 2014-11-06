import MySQLdb
import json


class MyDatabase:
    def __init__(self):
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="1",
                                  db="tp_subd", use_unicode=1, charset='utf8')
        self.cursor = self.db.cursor()
        pass

    def execute(self, sql, args=(), post=False):
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="1",
                                  db="tp_subd", use_unicode=1, charset='utf8')
        self.cursor = self.db.cursor()
        self.cursor.execute(sql, args)
        if post:
            self.db.commit()
        self.db.close()
        return self.cursor.fetchall()

    def clear(self):
        self.execute("""TRUNCATE TABLE Forum;""")
        self.execute("""TRUNCATE TABLE User;""")
        self.execute("""TRUNCATE TABLE Post;""")
        self.execute("""TRUNCATE TABLE Thread;""")
        self.execute("""TRUNCATE TABLE Subscription;""")
        self.execute("""TRUNCATE TABLE Follower;""")

        return [json.dumps({"code": 0, "response": "OK"})]

    def get_last_row_id(self):
        return self.cursor.lastrowid


        # TODO
        # Exception _mysql_exceptions.OperationalError:
        # (2013, 'Lost connection to MySQL server during query')
        # in <bound method Cursor.__del__ of <MySQLdb.cursors.Cursor object at 0x7f380ccd73d0>>
        # ignored