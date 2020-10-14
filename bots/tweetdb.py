import psycopg2
import os


class TweetData:
    def __init__(self):
        self.conn = self._connect()

    @staticmethod
    def _connect():
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
        return conn
