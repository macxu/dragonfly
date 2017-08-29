"""Module for CPU related data parsing"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2016, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

import pprint
import requests

class Jenkins:

    def __init__(self, server = 'http://ci.marinsw.net/'):

        self.server = server
        self.rester = Rester()
    
    def getJobsOfView(self, viewUrl):
        return self.getJenkinsJson(viewUrl, "jobs")

    def getLatestBuildNumber(self, jobUrl):
        pass

    def getJobConfigs(self, jobUrl):
        pass

    def isView(self, jenkinsUrl):
        return True

    def isJob(self, jenkinsUrl):
        return True

    def isBuild(self, jenkinsUrl):
        return True

    def getLatestBuildUrl(self, jobUrl):
        pass

    def getTestCasesByBuild(self, buildUrl):
        pass

    def report(self, testCases):
        pass

    def getJenkinsJson(self, url, propertyKey=''):
        apiPostfix = 'api/json?pretty=true'
        if (not url.endswith(apiPostfix)):
            if (not url.endswith('/')):
                url += '/'
            url += apiPostfix

        response = requests.get(url)
        jsonResponse = response.json()

        if (propertyKey == ''):
            return jsonResponse
        else:
            return jsonResponse[propertyKey]


if (__name__ == '__main__'):
    jenkins = Jenkins()

    viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
    jobs = jenkins.getJobsOfView(viewUrl)
    pprint.pprint(jobs)

