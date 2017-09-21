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
        return self.convertToMap(result.to_dict('records'))


    def queryDmtDiscrepancyGroup(self, clientId):

        sql = ""
        sql += "select g.cltId as client_id, "
        sql += "g.pubId as publisher_id, "

        sql += "g.stts as status, "
        sql += "g.opStts as operational_status, "

        sql += "count(*) as object_count, "
        sql += "count(concat(a.extId, '|', c.extId, '|', g.extId)) as combined_ext_id_count_total, "

        sql += "count(distinct concat(a.extId, '|', c.extId, '|', g.extId)) as combined_ext_id_count_distinct, "
        sql += "count(g.lgcyId) as legacy_id_count_total, "
        sql += "sum(if(g.lgcyId is null, 1, 0)) as legacy_id_count_null, "
        sql += "count(distinct g.lgcyId) as legacy_id_count_distinct, "

        sql += "COUNT(g.id) AS id_count_total, "
        sql += "SUM(IF(g.id IS null, 1, 0)) AS id_count_null, "
        sql += "COUNT(DISTINCT g.id) AS id_count_distinct, "

        sql += "count(distinct "
        sql += "case when g.extId is null then "
        sql += "g.id "
        sql += "end) as ext_id_count_null, "

        sql += "cast(sum(g.bid) as double)/1000000 as bid_sum "
        sql += "from accounts a "
        sql += "join campaigns c on a.id = c.accId "
        sql += "join adgroups g on c.id = g.cpgnId "
        sql += "where g.cltId in (%s) " % clientId
        sql += "group by g.cltId, "
        sql += "g.pubId, "
        sql += "g.stts, "
        sql += "g.opStts"

        return self.query(sql)

    def queryDmtDiscrepancyKeyword(self, clientId):

        sql = ""
        sql += "select k.cltId as client_id, "
        sql += "k.pubId as publisher_id, "

        sql += "k.stts as status, "
        sql += "k.opStts as operational_status, "
        sql += "count(*) as object_count, "

        sql += "count(concat(a.extId, '|', c.extId, '|', g.extId, '|', k.extId)) as combined_ext_id_count_total, "
        sql += "count(distinct concat(a.extId, '|', c.extId, '|', g.extId, '|', k.extId)) as combined_ext_id_count_distinct, "
        sql += "count(k.lgcyId) as legacy_id_count_total, "
        sql += "sum(if(k.lgcyId is null, 1, 0)) as legacy_id_count_null, "
        sql += "count(distinct k.lgcyId) as legacy_id_count_distinct, "

        sql += "COUNT(k.id) AS id_count_total, "
        sql += "SUM(IF(k.id IS null, 1, 0)) AS id_count_null, "
        sql += "COUNT(DISTINCT k.id) AS id_count_distinct, "

        sql += "count(distinct "
        sql += "case when k.extId is null then "
        sql += "k.id "
        sql += "end) as ext_id_count_null, "

        sql += "cast(sum(k.bid) as double)/1000000 as bid_sum, "
        sql += "sum(length(k.destUrl)) as url_length_sum "
        sql += "from accounts a "
        sql += "join campaigns c on a.id = c.accId "
        sql += "join adgroups g on c.id = g.cpgnId "
        sql += "join keywords k on g.id = k.adGrpId "
        sql += "where k.cltId in (%s) " % clientId
        sql += "group by k.cltId, "
        sql += "k.pubId, "

        sql += "k.stts, "
        sql += "k.opStts"

        return self.query(sql)




    def queryDmtDiscrepancyCreative(self, clientId):

        sql = ""
        sql += "select cr.cltId as client_id, "
        sql += "cr.pubId as publisher_id, "

        sql += "cr.stts as status, "
        sql += "cr.opStts as operational_status, "
        sql += "count(*) as object_count, "
        sql += "count(concat(a.extId, '|', c.extId, '|', g.extId, '|', cr.extId)) as combined_ext_id_count_total, "

        sql += "count(distinct concat(a.extId, '|', c.extId, '|', g.extId, '|', cr.extId)) as combined_ext_id_count_distinct, "
        sql += "count(cr.lgcyId) as legacy_id_count_total, "
        sql += "sum(if(cr.lgcyId is null, 1, 0)) as legacy_id_count_null, "
        sql += "count(distinct cr.lgcyId) as legacy_id_count_distinct, "

        sql += "COUNT(cr.id) AS id_count_total, "
        sql += "SUM(IF(cr.id IS null, 1, 0)) AS id_count_null, "
        sql += "COUNT(DISTINCT cr.id) AS id_count_distinct, "

        sql += "count(distinct "
        sql += "case when cr.extId is null then "
        sql += "cr.id "
        sql += "end) as ext_id_count_null, "

        sql += "sum(length(cr.destUrl)) as url_length_sum "
        sql += "from accounts a "
        sql += "join campaigns c on a.id = c.accId "
        sql += "join adgroups g on c.id = g.cpgnId "
        sql += "join ad_creatives cr on g.id = cr.adGrpId "
        sql += "where cr.cltId in (%s) " % clientId
        sql += "group by cr.cltId, "
        sql += "cr.pubId, "

        sql += "cr.stts, "
        sql += "cr.opStts"

        return self.query(sql)


    def queryDmtDiscrepancyCampaign(self, clientId):

        sql = "SELECT "
        sql += "campaigns.cltid AS client_id, "
        sql += "campaigns.pubid AS publisher_id, "
        sql += "campaigns.stts AS status, "
        sql += "campaigns.opstts AS operational_status, "

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

        sql += "WHERE campaigns.cltid IN (%s) " % clientId

        sql += "GROUP BY campaigns.cltid, "
        sql += "campaigns.pubid, "
        sql += "campaigns.stts, "
        sql += "campaigns.opstts"

        return self.query(sql)



    def convertToMap(self, results):
        map = {}
        for result in results:
            key = 'publisherId={}; status={}; opstatus={}'.format(
                result['publisher_id'],
                result['status'],
                result['operational_status'])

            # scan the result, if there is any value of "nan", change it to None
            # otherwise we cannot see the result by JQuery, even we can see the result in browser.
            for propertyKey in result:
                if (str(result[propertyKey]) == 'nan'):
                    result[propertyKey] = None

            map[key] = result

        return map


if (__name__ == '__main__'):

    dbClient = PrestoClient()

    results = dbClient.queryDmtDiscrepancyCampaign(4338988)
    pprint(results)

    results = dbClient.queryDmtDiscrepancyGroup(4338988)
    pprint(results)

    results = dbClient.queryDmtDiscrepancyCreative(4338988)
    pprint(results)

    results = dbClient.queryDmtDiscrepancyKeyword(4338988)
    pprint(results)