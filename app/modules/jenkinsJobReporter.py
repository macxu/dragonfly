
"""Module for Jenkins Job reporting"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import threading
import re
from urllib.parse import urljoin


class JenkinsJobReporter(threading.Thread):

    def __init__(self, jobUrl=''):
        threading.Thread.__init__(self)

        self.jobUrl = jobUrl

        self.jobShortName = jobUrl
        self.latestBuildUrl = ''
        self.latestBuildNumber = 0

        self.casesFailed = []
        self.casesPassed = []
        self.casesSkipped = []

        self.rester = Rester()

    def run(self):
        self.getJobShortName()
        self.getLatestBuildInfo()
        if (self.latestBuildUrl):
            self.getTestCasesInfo()

    def getJobShortName(self):
        # form: http://ci.marinsw.net/job/qe-bulk-bing-sync-tests-qa2-release-012/1
        # to:   bulk-bing-sync
        matchObj = re.match(r'.*/job/qe-(.*)-test[s]?-.*', self.jobUrl, re.M | re.I)
        if (matchObj):
            self.jobShortName = matchObj.group(1)
            return




    def getTestCasesInfo(self):
        reportUrl = urljoin(self.latestBuildUrl, 'testReport')
        testSuites = self.getJenkinsJson(reportUrl, 'suites')

        for testSuite in testSuites:
            for testCase in testSuite['cases']:
                # set testClass
                className = testCase['className']
                testCase['testClass'] = className.split('.')[-1]

                # set testMethod
                methodName = testCase['name']
                methodNameBracketIndex = methodName.rfind(' (')
                if methodNameBracketIndex > -1:
                    serialMethodNameBracketIndex = methodName.rfind(')')
                    methodName = methodName[methodNameBracketIndex + 2: serialMethodNameBracketIndex]

                testCase['testMethod'] = methodName

                # set testCase
                caseName = testCase['name']
                if methodNameBracketIndex > -1:
                    serialCountClosingBracketIndex = caseName.find("] ")
                    caseName = caseName[serialCountClosingBracketIndex + 2: methodNameBracketIndex]

                testCase["name"] = caseName

                if (testCase['status'] == 'PASSED' or testCase['status'] == 'FIXED'):
                    self.casesPassed.append(testCase)
                elif (testCase['status'] == "FAILED"):
                    self.casesFailed.append(testCase)
                elif (testCase['status'] == "SKIPPED"):
                    self.casesSkipped.append(testCase)
                else:
                    print("unrecognized status: " + testCase['status'])


    def getJenkinsApiUrl(self, url):
        apiPostfix = 'api/json?pretty=true'
        if (not url.endswith(apiPostfix)):
            if (not url.endswith('/')):
                url += '/'
            url += apiPostfix

        return url

    """ Get the URL of the latest build of the specified Jenkins job
        """
    def getLatestBuildInfo(self):
        jobInfo = self.getJenkinsJson(self.jobUrl)
        if (not jobInfo):
            self.latestBuildUrl = ''
            return self.latestBuildUrl

        lastCompletedBuild = jobInfo['lastCompletedBuild']
        if (not lastCompletedBuild):
            self.latestBuildUrl = ''
            return self.latestBuildUrl

        self.latestBuildUrl = lastCompletedBuild['url']
        return self.latestBuildUrl


    def getReport(self):
        report = {}

        report['cases'] = {}
        report['cases']['passed'] = []
        report['cases']['passed'] += self.casesPassed

        report['cases']['failed'] = []
        report['cases']['failed'] += self.casesFailed

        report['cases']['skipped'] = []
        report['cases']['skipped'] += self.casesSkipped

        report['build'] = self.latestBuildUrl
        report['job'] = self.jobShortName

        return report

    def getAllCases(self):
        return self.casesPassed + self.casesFailed + self.casesSkipped

    def getPassedCases(self):
        return self.casesPassed

    def getPassedCount(self):
        return len(self.casesPassed)

    def getFailedCases(self):
        return self.casesFailed

    def getFailedCount(self):
        return len(self.casesFailed)

    def getSkippedCases(self):
        return self.casesSkipped

    def getSkippedCount(self):
        return len(self.casesSkipped)

    def getBuildCount(self):
        return 0

    """ Get the API response of a specified Jenkins URL
            This is how Jenkins exposes it REST APIs, just appending "/api/json?pretty=true" to the url and get the data in JSON
        """

    def getJenkinsJson(self, url, propertyKey=''):
        url = self.getJenkinsApiUrl(url)
        return self.rester.getJson(url, propertyKey)

if (__name__ == '__main__'):
    # jenkinsReporter = JenkinsJobReporter('http://ci.marinsw.net/job/qe-activity-log-service-tests-qa2-release-012/')
    # jenkinsReporter.getLatestBuildInfo()

    jenkinsReporter = JenkinsJobReporter('http://ci.marinsw.net/job/qe-google-bulk-bat-tests-qa2-release-012/')
    # jenkinsReporter.getLatestBuildInfo()
    # jenkinsReporter.getTestCasesInfo()

    jenkinsReporter.run()
