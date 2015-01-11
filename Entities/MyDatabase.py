import MySQLdb
# import time

DB_HOST = 'localhost'
DB_USER = 'subd_user'
DB_DATABASE = 'tp_subd'
# DB_DATABASE = 'tp_subd2'

# current_milli_time = lambda: int(round(time.time() * 1000))


class MyDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.init_connection_and_cursor()

    def execute(self, sql, args=(), post=False):
        # tm = current_milli_time()

        self.cursor.execute(sql, args)
        if post:
            self.connection.commit()
            # tm = current_milli_time() - tm
            # if tm > 50:
            #    print tm, " ", sql
            return self.cursor.lastrowid

        # tm = current_milli_time() - tm
        # if tm > 50:
        #    print tm, " ", sql
        return self.cursor.fetchall()

    def close_connections(self):
        self.connection.close()

    def init_connection_and_cursor(self):
        if not self.connection or not self.connection.open:
            self.connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, db=DB_DATABASE, use_unicode=1, charset='utf8')
            self.cursor = self.connection.cursor()


db = MyDatabase()
