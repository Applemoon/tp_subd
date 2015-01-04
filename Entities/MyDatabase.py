import MySQLdb
import json


class MyDatabase:
    def __init__(self):
        self.connection, self.cursor = self.init_connection_and_cursor()
        pass

    def execute(self, sql, args=(), post=False):
        self.connection, self.cursor = self.init_connection_and_cursor()

        # try:
        self.cursor.execute(sql, args)
        # except Exception as e:
        #     print "Error %d: %s" % (e.args[0], e.args[1])

        if post:
            self.connection.commit()
        self.connection.close()
        return self.cursor.fetchall()

    def clear(self):
        self.execute("""TRUNCATE TABLE Forum;""", post=True)
        self.execute("""TRUNCATE TABLE User;""", post=True)
        self.execute("""TRUNCATE TABLE Post;""")
        self.execute("""TRUNCATE TABLE Thread;""", post=True)
        self.execute("""TRUNCATE TABLE Subscription;""", post=True)
        self.execute("""TRUNCATE TABLE Follower;""", post=True)

        return json.dumps({"code": 0, "response": "OK"})

    def get_last_row_id(self):
        return self.cursor.lastrowid

    @staticmethod
    def init_connection_and_cursor():
        connection = MySQLdb.connect(host="localhost", user="subd_user",
                                     db="tp_subd", use_unicode=1, charset='utf8')
        cursor = connection.cursor()
        return connection, cursor
