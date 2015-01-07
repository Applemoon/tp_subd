import MySQLdb

DB_HOST = 'localhost'
DB_USER = 'subd_user'
DB_DATABASE = 'tp_subd'
# DB_DATABASE = 'tp_subd2'


class MyDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def execute(self, sql, args=(), post=False):
        self.cursor.execute(sql, args)
        if post:
            self.connection.commit()
            return self.cursor.lastrowid

        return self.cursor.fetchall()

    def close_connections(self):
        self.connection.close()

    def init_connection_and_cursor(self):
        self.connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, db=DB_DATABASE, use_unicode=1, charset='utf8')
        self.cursor = self.connection.cursor()


db = MyDatabase()