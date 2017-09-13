
"""Module for Jenkins Job reporting"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import threading
import re
import pprint
from urllib.parse import urljoin
import xml.dom.minidom as elements



class JenkinsJob(threading.Thread):

    def __init__(self, jobUrl=''):
        threading.Thread.__init__(self)

        self.jobUrl = jobUrl

        self.viewUrl = ''

        self.jobShortName = jobUrl
        self.setJobShortName()

        self.latestBuildUrl = ''
        self.latestBuildNumber = 0

        self.casesFailed = []
        self.casesPassed = []
        self.casesSkipped = []
        self.user = {}
        self.rester = Rester()
        self.jobConfig = {}

    def setViewUrl(self, url):
        self.viewUrl = url

    def run(self):
        self.load()

    def load(self):
        self.setJobShortName()
        self.getLatestBuildInfo()
        self.getUser()
        self.getJobConfigs()
        if (self.latestBuildUrl):
            self.getTestCasesInfo()

    def getUrl(self):
        return self.jobUrl

    """ Get the latest build number of the job
            If the URL is not of a job, throw exception
            If there is no build, return 0
        """
    def getLatestBuildNumber(self):
        jobData = self.getJenkinsJson(self.jobUrl)
        return jobData['lastCompletedBuild']['number']


    def setJobShortName(self):
        # form: http://ci.marinsw.net/job/qe-bulk-bing-sync-tests-qa2-release-012/1
        # to:   bulk-bing-sync
        matchObj = re.match(r'.*/job/qe-(.*)-test[s]?-.*', self.jobUrl, re.M | re.I)
        if (matchObj):
            self.jobShortName = matchObj.group(1)
        else:
            self.jobShortName = self.jobUrl

    def getUser(self):
        if self.latestBuildUrl:
            actions = self.getJenkinsJson(self.latestBuildUrl, 'actions')
            for action in actions:
                if ('causes') in action:
                    for cause in action['causes']:
                        if 'userName' in cause:
                            self.user['name'] = cause['userName']
                            self.user['id'] = cause['userId']
                            break
                    break


    def getJobShortName(self):
        return self.jobShortName


    def getTestCasesInfo(self):
        reportUrl = urljoin(self.latestBuildUrl, 'testReport')
        testSuites = self.getJenkinsJson(reportUrl, 'suites')

        for testSuite in testSuites:
            for testCase in testSuite['cases']:
                #set user
                testCase['user'] = self.user
                # set testClass
                className = testCase['className']
                testCase['testClass'] = className.split('.')[-1]

                testCase['view'] = self.viewUrl
                testCase['job'] = self.jobUrl
                testCase['jobShortName'] = self.jobShortName
                testCase['build'] = self.latestBuildUrl
                testCase['buildNumber'] = self.latestBuildNumber

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
                elif (testCase['status'] == "FAILED" or testCase['status'] == 'REGRESSION'):
                    self.casesFailed.append(testCase)
                elif (testCase['status'] == "SKIPPED"):
                    self.casesSkipped.append(testCase)
                else:
                    print("unrecognized status: " + testCase['status'])
                    pprint.pprint(self.jobUrl)


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

    """ Get the job configurations, including the git branch, environments etc.
        The response data are organized as key value pairs.      
        if some parameter is depended on build, we will get the build parameter
    """
    def getJobConfigs(self):
        if not self.jobUrl.endswith("/"):
            self.jobUrl += "/"

        configUrl = self.jobUrl + "config.xml"

        content = self.rester.getXml(configUrl)

        if content == {}:
            return {}

        dom = elements.parseString(content).getElementsByTagName("targets")[0]
        jobConfigString = dom.childNodes[0].nodeValue


        isRequireParamValue = False

        for mvnCommandPart in jobConfigString.split("\n"):
            if mvnCommandPart.startswith("-D"):
                separator = mvnCommandPart.find("=")
                self.jobConfig[mvnCommandPart[2:separator]] = mvnCommandPart[separator+1:]
                isRequireParamValue = mvnCommandPart[separator+1:].startswith("$") or isRequireParamValue

        if isRequireParamValue:
            parameter = self.getBuildParameter(self.latestBuildUrl)
            for (propertyName, propertyValue) in self.jobConfig.items():
                if propertyValue.startswith("$"):
                        self.jobConfig[propertyName] = parameter[propertyValue[1:]]


    """ Get the buils configurations, including the git branch, environments etc.
    """
    def getBuildParameter(self, buildUrl):

        actions = self.getJenkinsJson(buildUrl, 'actions')
        param = {}
        for action in actions:
            if 'parameters' in action:
                for parameter in action['parameters']:
                    param[parameter['name']] = parameter['value']
                break
        return param

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


    jenkinsJob = JenkinsJob('http://ci.marinsw.net/job/qe-sso-tests-develop/')
    jenkinsJob.load




