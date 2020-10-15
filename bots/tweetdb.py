import psycopg2
import os


class TweetData:
    def __init__(self):
        self.conn = None
        self.cursor = None

        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(os.getenv("PG_DB_URI"), sslmode='require')
            self.cursor = self.conn.cursor()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def disconnect(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("PostgreSQL connection is closed")
