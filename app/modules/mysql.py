"""Module for MySql Client"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

# need to install module: Flask-MySQLdb===0.2.0
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from pprint import pprint

from flask import Flask

class MysqlClient:

    def __init__(self, flaskApp=None):

        if (flaskApp == None):
            flaskApp = Flask(__name__)


        # flaskApp.config['MYSQL_DATABASE_USER'] = 'XXXXX'
        # flaskApp.config['MYSQL_DATABASE_PASSWORD'] = 'XXXXXXXX'
        # flaskApp.config['MYSQL_DATABASE_DB'] = 'marin'
        # flaskApp.config['MYSQL_DATABASE_HOST'] = 'dbp105.prod.marinsw.net'

        flaskApp.config['MYSQL_DATABASE_USER'] = 'marin'
        flaskApp.config['MYSQL_DATABASE_PASSWORD'] = 'wawptw'
        flaskApp.config['MYSQL_DATABASE_DB'] = 'marin'
        flaskApp.config['MYSQL_DATABASE_HOST'] = 'qa2-dbp-lv-103.labs.marinsw.net'

        self.flaskApp = flaskApp

        self.mysql = MySQL(cursorclass=DictCursor)

        self.mysql.init_app(self.flaskApp)

        self.conn = self.mysql.connect()

    def query(self, sql):

        cursor = self.conn.cursor()
        cursor.execute(sql)
        fetchResult = cursor.fetchall()

        return fetchResult

    def close(self):
        if (self.conn):
            self.conn.close()


if (__name__ == '__main__'):

    mysqlClient = MysqlClient()
    results = mysqlClient.query("SELECT * from publisher_campaigns LIMIT 2")

    pprint(results)

    mysqlClient.close()

