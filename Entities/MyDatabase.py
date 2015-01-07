import MySQLdb


class MyDatabase:
    def __init__(self):
        # self.connection = None
        #     self.cursor = None
        # self.connection, self.cursor = self.init_connection_and_cursor()
        pass

    def execute(self, sql, args=(), post=False):
        # self.connection, self.cursor = self.init_connection_and_cursor()
        connection, cursor = self.init_connection_and_cursor()
        cursor.execute(sql, args)
        if post:
            connection.commit()
            connection.close()
            return cursor.lastrowid

        connection.close()
        return cursor.fetchall()

    @staticmethod
    def init_connection_and_cursor():
        # connection = MySQLdb.connect(host="localhost", user="subd_user", db="tp_subd", use_unicode=1, charset='utf8')
        connection = MySQLdb.connect(host="localhost", user="subd_user", db="tp_subd2", use_unicode=1, charset='utf8')
        cursor = connection.cursor()
        return connection, cursor


db = MyDatabase()