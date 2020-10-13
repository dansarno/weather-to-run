import psycopg2
import os


class tweetData:
    def __init__(self):
        self.con = self.connect()

    def connect(self):
        con = psycopg2.connect(database=os.getenv("DB_NAME"),
                               user=os.getenv("DB_USER"),
                               password=os.getenv("DB_PWD"),
                               host=os.getenv("DB_HOST"),
                               port=os.getenv("DB_PORT")
                               )
        return con
