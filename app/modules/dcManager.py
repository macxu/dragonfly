"""Module for DC Manager"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.rester import Rester

class DcManager:

    def __init__(self):
        self.rester = Rester()

        self.dcLookupUrl = 'http://lookup-vip.marinsoftware.com:4567/clients/'

    def getDc(self, clientId):
        # http://lookup-vip.marinsoftware.com:4567/clients/32327

        # {
        #     "id": 32327,
        #     "customerId": 1,
        #     "name": "Ming PowPow Sports",
        #     "trackingId": "18yd32327",
        #     "messageQueue": "Diagnosis",
        #     "status": "ACTIVE",
        #     "currency": "USD",
        #     "locale": "en_US",
        #     "extId": null,
        #     "dataCloud": "DC80",
        #     "attributeRevenueAcrossClients": false,
        #     "revenueSource": [],
        #     "approxKeywordCount": 2450,
        #     "timeZone": "America/Los_Angeles"
        # }

        url = self.dcLookupUrl + str(clientId)
        json = self.rester.getJson(url)

        dataCloud = json['dataCloud']

        return dataCloud

    # from dc name like : DC80
    # to dbp162.rod.marinsw.net
    def getDcDomainByName(self, dcName):

        print(dcName)
        dcNumber = int(dcName.replace("DC", ""))

        if (dcNumber == 1):
            domainId = 1
        elif (dcNumber == 2):
            domainId = 3
        elif (dcNumber == 3):
            domainId = 5
        elif (dcNumber == 4):
            domainId = 7
        else:
            domainId = dcNumber * 2 + 1

        #dbp162.rod.marinsw.net
        fullDomain = "dbp" + str(domainId) + ".rod.marinsw.net"
        return fullDomain

if (__name__ == '__main__'):

    dcManager = DcManager()
    domainId = dcManager.getDcDomainByName("DC80")
    print(domainId)

