"""Module for MySql Client"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

# need to install module: Flask-MySQLdb===0.2.0
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

from flask import Flask

class MysqlClient:

    def __init__(self, flaskApp=None):

        self.mysql = MySQL(cursorclass=DictCursor)

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

        self.mysql.init_app(flaskApp)

        self.conn = self.mysql.connect()
        cursor = self.conn.cursor()

        cursor.execute("SELECT * from publisher_campaigns LIMIT 2")
        fetchResult = cursor.fetchall()

        data = str(fetchResult)

        self.conn.close()

        sdf= 0



    """ Get the list of the test project names in the
    """
    def connect(self):
        pass
        # from flask_mysqldb import MySQL




if (__name__ == '__main__'):

    mysqlClient = MysqlClient()
    mysqlClient.connect()

