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

        return self.convertToMap(fetchResult)

    def close(self):
        if (self.conn):
            self.conn.close()

    def queryDmtDiscrepancyGroup(self, clientId):

        sql = ""
        sql += "SELECT pa.client_id as client_id,"
        sql += "pa.publisher_id as publisher_id,"
        sql += "pg.publisher_group_status as status, "
        sql += "pg.publisher_group_operation_status as operational_status, "

        sql += "count(*) as object_count, "
        sql += "count(concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id)) as combined_ext_id_count_total, "
        sql += "count(distinct concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id)) as combined_ext_id_count_distinct, "
        sql += "count(pg.publisher_group_id) as id_count_total, "

        sql += "sum(if(pg.publisher_group_id is null, 1, 0)) as id_count_null, "  # can never happen, field is primary key, can't be null
        sql += "count(distinct pg.publisher_group_id) as id_count_distinct, "
        sql += "count(pg.publisher_group_id) as legacy_id_count_total, "

        sql += "sum(if(pg.publisher_group_id is null, 1, 0)) as legacy_id_count_null, " # can never happen, field is primary key, can't be null
        sql += "count(distinct pg.publisher_group_id) as legacy_id_count_distinct, "

        sql += "count(distinct "
        sql += "case when pg.ext_id is null then "
        sql += "pg.publisher_group_id "
        sql += "end) as ext_id_count_null, "
        sql += "sum(pg.max_cpc) as bid_sum "
        sql += "from publisher_accounts pa "
        sql += "join publisher_client_accounts pca on pa.publisher_account_id = pca.publisher_account_id "
        sql += "join publisher_campaigns pc on pca.client_account_id = pc.client_account_id "
        sql += "join publisher_groups pg on pc.publisher_campaign_id = pg.publisher_campaign_id "
        sql += "left join google_client_accounts google on pca.client_account_id = google.google_client_account_id "
        sql += "left join msn_client_accounts msn on pca.client_account_id = msn.msn_client_account_id "
        sql += "where pa.client_id in (%s) " % clientId
        sql += "and pa.publisher_id in (4,6) "
        sql += "group by pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "pg.publisher_group_status, "
        sql += "pg.publisher_group_operation_status; "

        return self.query(sql)


    def queryDmtDiscrepancyKeyword(self, clientId):

        sql = ""
        sql += "select pa.client_id as client_id, "
        sql += "pa.publisher_id as publisher_id, "
        sql += " k.keyword_status as status, "
        sql += "k.keyword_operation_status as operational_status, "

        sql += "count(distinct k.id) as object_count, "
        sql += "count(concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id, '|', k.ext_id)) as combined_ext_id_count_total, "
        sql += "count(distinct concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id, '|', k.ext_id)) as combined_ext_id_count_distinct, "

        sql += "count(k.id) as id_count_total, "
        sql += "sum(if(k.id is null, 1, 0)) as id_count_null, "  # can never happen, field is primary key, can't be null
        sql += "count(distinct k.id) as id_count_distinct, "

        sql += "count(k.id) as legacy_id_count_total, "
        sql += "sum(if(k.id is null, 1, 0)) as legacy_id_count_null, "  # can never happen, field is primary key, can't be null
        sql += "count(distinct k.id) as legacy_id_count_distinct, "

        sql += "count(distinct "
        sql += "case when k.ext_id is null then "
        sql += "k.id "
        sql += "end) as ext_id_count_null, "

        sql += "sum(k.max_cpc) as bid_sum, "
        sql += "sum(length(k.destination_url)) as url_length_sum "
        sql += "from publisher_accounts pa "
        sql += "join publisher_client_accounts pca on pa.publisher_account_id = pca.publisher_account_id "
        sql += "join publisher_campaigns pc on pca.client_account_id = pc.client_account_id "
        sql += "join publisher_groups pg on pc.publisher_campaign_id = pg.publisher_campaign_id "
        sql += "join keyword_instances k on pg.publisher_group_id = k.publisher_group_id "
        sql += "left join google_client_accounts google on pca.client_account_id = google.google_client_account_id "
        sql += "left join msn_client_accounts msn on pca.client_account_id = msn.msn_client_account_id "
        sql += "where pa.client_id in (%s) " % clientId
        sql += "and pa.publisher_id in (4,6) "
        sql += "group by pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "k.keyword_status, "
        sql += "k.keyword_operation_status "

        return self.query(sql)


    def queryDmtDiscrepancyCreative(self, clientId):

        sql = ""
        sql += "select pa.client_id as client_id, "
        sql += "pa.publisher_id as publisher_id, "
        sql += "c.creative_status as status, "
        sql += "c.publisher_creative_operation_status as operational_status, "
        sql += "count(distinct c.creative_id) as object_count, "
        sql += "count(concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id, '|', c.ext_id)) as combined_ext_id_count_total, "
        sql += "count(distinct concat( "
        sql += "case when pa.publisher_id = 4 then "
        sql += "google.client_customer_id "
        sql += "when pa.publisher_id = 6 then "
        sql += "msn.account_id "
        sql += "else "
        sql += "pca.alias "
        sql += "end, '|', pc.ext_id, '|', pg.ext_id, '|', c.ext_id, '-')) as combined_ext_id_count_distinct, "
        sql += "count(c.creative_id) as id_count_total, "
        sql += "sum(if(c.creative_id is null, 1, 0)) as id_count_null, " # can never happen, field is primary key, can't be null
        sql += "count(distinct c.creative_id) as id_count_distinct, "
        sql += "sum(if(c.creative_id is null, 1, 0)) as legacy_id_count_null, " # can never happen, field is primary key, can't be null
        sql += "count(distinct c.creative_id) as legacy_id_count_distinct, "
        sql += "count(distinct "
        sql += "case when c.ext_id is null then "
        sql += "c.creative_id "
        sql += "end) as ext_id_count_null, "
        sql += "sum(length(c.destination_url)) as url_length_sum "
        sql += "from publisher_accounts pa "
        sql += "join publisher_client_accounts pca on pa.publisher_account_id = pca.publisher_account_id "
        sql += "join publisher_campaigns pc on pca.client_account_id = pc.client_account_id "
        sql += "join publisher_groups pg on pc.publisher_campaign_id = pg.publisher_campaign_id "
        sql += "join publisher_creatives c on pg.publisher_group_id = c.publisher_group_id "
        sql += "left join google_client_accounts google on pca.client_account_id = google.google_client_account_id "
        sql += "left join msn_client_accounts msn on pca.client_account_id = msn.msn_client_account_id "
        sql += "where pa.client_id in (%s) " % clientId
        sql += "and pa.publisher_id in (4,6) "
        sql += "group by pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "c.creative_status, "
        sql += "c.publisher_creative_operation_status; "

        return self.query(sql)



    def queryDmtDiscrepancyCampaign(self, clientId):

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
        sql += "WHERE pa.client_id IN (%s) " % clientId
        sql += "AND pa.publisher_id IN (4,6) "
        sql += "GROUP BY pa.client_id, "
        sql += "pa.publisher_id, "
        sql += "pc.publisher_campaign_status,"
        sql += "pc.publisher_campaign_operation_status;"

        return self.query(sql)



    def convertToMap(self, results):
        map = {}
        for result in results:
            key = 'publisherId={}; status={}; opstatus={}'.format(
                result['publisher_id'], result['status'], result['operational_status'])
            map[key] = result
        return map

if (__name__ == '__main__'):

    mysqlClient = MysqlClient()

    results = mysqlClient.queryDmtDiscrepancyCampaign(12654910)
    pprint(results)

    results = mysqlClient.queryDmtDiscrepancyGroup(12654910)
    pprint(results)

    results = mysqlClient.queryDmtDiscrepancyCreative(12654910)
    pprint(results)

    results = mysqlClient.queryDmtDiscrepancyKeyword(12654910)
    pprint(results)

    mysqlClient.close()

