"""Module for MySql Client"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from pypresto import PrestoConnection


class PrestoClient:

    def __init__(self, flaskApp=None):


        # self.conn = prestodb.dbapi.connect(
        #     host='prod-lex-prestocoordinator-lv-1.prod.marinsw.net',
        #     port=8080,
        #     user='mxu',
        #     catalog='hive',
        #     schema='prod'
        # )
        # cur = self.conn.cursor()
        # cur.execute('SELECT * FROM campaigns LIMIT 2')
        # rows = cur.fetchall()
        #
        # self.conn.close()

        host = 'http://qa2-zod-prestocoordinator-lv-101.labs.marinsw.net'
        user = 'qa2'
        catalog = 'hive'
        port = 8080
        schema = 'qa2'
        password = ''


        conn = PrestoConnection(host, user, catalog,port, schema,password)
        query = 'select * from creative_dims limit 2'
        results = conn.run_query(query)

        sdf = 0

    """ Get the list of the test project names in the
    """
    def connect(self):
        pass
        # from flask_mysqldb import MySQL




if (__name__ == '__main__'):

    dbClient = PrestoClient()
    dbClient.connect()

