"""Module for MySql Client"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.Py3PrestoConnection import Py3PrestoConnection
from pprint import pprint

class PrestoClient:

    def __init__(self):

        self.host = 'http://qa2-zod-prestocoordinator-lv-101.labs.marinsw.net'
        self.user = 'qa2'
        self.catalog = 'hive'
        self.port = 8080
        self.schema = 'qa2'
        self.password = ''

        self.conn = Py3PrestoConnection(self.host, self.user, self.catalog, self.port, self.schema, self.password)

    def query(self, sql):
        return self.conn.run_query(sql)


if (__name__ == '__main__'):

    dbClient = PrestoClient()

    sql = 'SELECT * FROM campaigns LIMIT 2'
    results = dbClient.query(sql)
    pprint(results)

