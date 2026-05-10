import sqlite3
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()
