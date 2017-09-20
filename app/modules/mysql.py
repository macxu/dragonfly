"""Module for MySql Client"""


__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

# need to install module: Flask-MySQLdb===0.2.0
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from pprint import pprint
from decimal import Decimal

from flask import Flask

from app.modules.dcManager import DcManager

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

        for record in fetchResult:
            for key, value in record.items():
                if type(value) == Decimal:
                    record[key] = float(value)

        return fetchResult

    def close(self):
        if (self.conn):
            self.conn.close()

    def queryDmtCampaignDiscrepancy(self, clientId):
        # clients = ''
        # if type(clientIds) == str:
        #     clients = clientIds
        # elif type(clientIds) == list:
        #     clients = ','.join(map(str,clientIds))
        # else:
        #     return []

        sql = ""
        sql += "SELECT pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "pc.publisher_campaign_status AS status, "
        sql += "pc.publisher_campaign_operation_status AS operational_status, "
        sql += "COUNT(*) AS campaign_count, "
        sql += "COUNT(CONCAT( "
        sql += " CASE WHEN pa.publisher_id = 4 THEN "
        sql += "  google.client_customer_id "
        sql += "  WHEN pa.publisher_id = 6 THEN "
        sql += "  msn.account_id "
        sql += "ELSE "
        sql += "pca.alias "
        sql += "END, '|', pc.ext_id, '-')) AS combined_ext_id_count_total, "
        sql += "COUNT(DISTINCT concat( "
        sql += " CASE WHEN pa.publisher_id = 4 THEN "
        sql += "    google.client_customer_id "
        sql += "  WHEN pa.publisher_id = 6 THEN "
        sql += "    msn.account_id "
        sql += "  ELSE "
        sql += "    pca.alias "
        sql += " END, '|', pc.ext_id, '-')) AS combined_ext_id_count_distinct, "
        sql += "COUNT(pc.publisher_campaign_id) AS legacy_id_count_total, "
        sql += "SUM(IF(pc.publisher_campaign_id IS null, 1, 0)) AS legacy_id_count_null, "
        sql += "COUNT(DISTINCT pc.publisher_campaign_id) AS legacy_id_count_distinct, "
        sql += "COUNT(pc.publisher_campaign_id) AS id_count_total, "
        sql += "SUM(IF(pc.publisher_campaign_id IS null, 1, 0)) AS id_count_null, "
        sql += "COUNT(DISTINCT pc.publisher_campaign_id) AS id_count_distinct, "
        sql += "COUNT(DISTINCT "
        sql += "  CASE WHEN pc.ext_id IS NULL THEN "
        sql += "    pc.publisher_campaign_id "
        sql += "  END) AS ext_id_count_null, "
        sql += "SUM(daily_budget) AS budget_sum "
        sql += "FROM publisher_accounts pa "
        sql += "JOIN publisher_client_accounts pca ON pa.publisher_account_id = pca.publisher_account_id "
        sql += "JOIN publisher_campaigns pc ON pca.client_account_id = pc.client_account_id "
        sql += "LEFT JOIN google_client_accounts google ON pca.client_account_id = google.google_client_account_id "
        sql += "LEFT JOIN msn_client_accounts msn ON pca.client_account_id = msn.msn_client_account_id "
        sql += "WHERE pa.client_id IN ({}) ".format(clientId)
        sql += "AND pa.publisher_id IN (4,6) "
        sql += "GROUP BY pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "pc.publisher_campaign_status,"
        sql += "pc.publisher_campaign_operation_status;"

        results = self.query(sql)
        return self.convertToMap(results)


    def convertToMap(self, results):
        map = {}
        for result in results:
            key = 'publisherId={}; status={}; opstatus={}'.format(
                result['publisher_id'], result['status'], result['operational_status'])
            map[key] = result
        return map

if (__name__ == '__main__'):

    mysqlClient = MysqlClient()

    results = mysqlClient.queryDmtCampaignDiscrepancy(12654910)
    pprint(results)
    mysqlClient.close()

