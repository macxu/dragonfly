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
        # Return empty  when result is empty, otherwise when result is empty will report error
        result = self.conn.run_query(sql, True)
        # Convert the result from dataframe to list of dictionary
        return result.to_dict('records')


    def queryDmtCampaignDiscrepancy(self, clientIds='4338988'):

        if type(clientIds) == str:
            clients = clientIds
        elif type(clientIds) == list:
            clients = ','.join(map(str, clientIds))
        else:
            return []

        sql = "SELECT "
        sql += "campaigns.cltid AS client_id, "
        sql += "campaigns.pubid AS publisher_id, "
        sql += "campaigns.stts AS publisher_campaign_status, "
        sql += "campaigns.opstts AS publisher_campaign_operation_status, "

        sql += "COUNT(*) AS campaign_count, "
        sql += "COUNT(CONCAT(accounts.extid,coalesce(campaigns.extid, '-'))) AS combined_ext_id_count_total, "
        sql += "COUNT(DISTINCT concat(accounts.extid,coalesce(campaigns.extid, '-'))) AS combined_ext_id_count_distinct, "
        sql += "COUNT(campaigns.id) AS id_count_total, "
        sql += "SUM(IF(campaigns.id IS null, 1, 0)) AS id_count_null, "
        sql += "COUNT(DISTINCT campaigns.id) AS id_count_distinct, "
        sql += "COUNT(DISTINCT "
        sql += "  CASE WHEN campaigns.extid IS null THEN "
        sql += "    campaigns.id "
        sql += "  END) AS ext_id_count_null, "

        sql += "COUNT(campaigns.lgcyid) AS legacy_id_count, "
        sql += "SUM(IF(campaigns.lgcyid IS null, 1, 0)) AS legacy_id_count_null, "
        sql += "COUNT(distinct campaigns.lgcyid) AS legacy_id_count_distinct,"

        sql += "CAST(SUM(campaigns.dailybudget) AS double)/1000000 AS budget_sum "

        sql += "FROM campaigns "
        sql += "LEFT JOIN accounts ON campaigns.accid = accounts.id "

        sql += "WHERE campaigns.cltid IN ({}) ".format(clients)

        sql += "GROUP BY campaigns.cltid, "
        sql += "campaigns.pubid, "
        sql += "campaigns.stts, "
        sql += "campaigns.opstts"

        results = self.query(sql)

        return self.convertToMap(results)

    def convertToMap(self, results):
        map = {}
        for result in results:
            key = 'publisherId={};status={};opstatus={}'.format(result['publisher_id'], result['publisher_campaign_status'], result['publisher_campaign_operation_status'])
            map[key] = result
        return map


if (__name__ == '__main__'):

    dbClient = PrestoClient()

    results = dbClient.queryDmtCampaignDiscrepancy()
    pprint(results)

    results = dbClient.queryDmtCampaignDiscrepancy(['4338988', 1231])
    pprint(results)

