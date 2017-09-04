
"""Module for Jenkins data parsing"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import pprint
import requests
import xml.dom.minidom as elements
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Jenkins:

    """ TODO: need a better way to specify the Jenkins server to make it good for general use """
    def __init__(self):

        self.rester = Rester()

    """ Get the jobs of the specified Jenkins view URL  """
    def getJobsOfView(self, viewUrl):
        return self.getJenkinsJson(viewUrl, "jobs")

    """ Get the latest build number of the specified Jenkins job URL
        If the URL is not of a job, throw exception
        If there is no build, return 0
    """
    def getLatestBuildNumber(self, jobUrl):
        jobData = self.getJenkinsJson(jobUrl)
        return jobData['lastCompletedBuild']['number']

    """ Get the job configurations, including the git branch, environments etc.
        The response data are organized as key value pairs
    """
    def getJobConfigs(self, jobOrBuildUrl):
        if not jobOrBuildUrl.endswith("/"):
            jobOrBuildUrl += "/"

        if self.isBuild(jobOrBuildUrl):
            targetUrl = "/".join(jobOrBuildUrl.split("/")[0:-2])
            targetUrl += "/"
        elif self.isJob(jobOrBuildUrl):
            targetUrl = jobOrBuildUrl
        else:
            return {}

        targetUrl += "config.xml"

        response = requests.get(targetUrl)

        if response.status_code != 200:
            return {}

        dom = elements.parseString(response.content).getElementsByTagName("targets")[0]
        jobConfigString = dom.childNodes[0].nodeValue

        resultConfig = {}
        isRequireParamValue = False

        for mvnCommandPart in jobConfigString.split("\n"):
            if mvnCommandPart.startswith("-D"):
                separator = mvnCommandPart.find("=")
                resultConfig[mvnCommandPart[2:separator]] = mvnCommandPart[separator+1:]
                isRequireParamValue = mvnCommandPart[separator+1:].startswith("$") or isRequireParamValue
            else:
                pass


        if isRequireParamValue:
            if self.isBuild(jobOrBuildUrl):
                return self.__getBuildConfigParametersForGivenBuildUrl(jobOrBuildUrl, resultConfig)
            elif self.isJob(jobOrBuildUrl):
                return self.__getBuildConfigParametersForGivenBuildUrl(self.getLatestBuildUrl(jobOrBuildUrl), resultConfig)
            else:
                return {}

        else:
            return resultConfig

    """ Get the job configurations, including the git branch, environments etc. for develop branch,
           which requires to specify the build version
    """
    def __getBuildConfigParametersForGivenBuildUrl(self, buildUrl, protoConfig):

        if protoConfig.__len__() == 0:
            return {}

        if not buildUrl.endswith("/"):
            buildUrl += "/"
        buildUrl += "parameters/"
        responseForParam = requests.get(buildUrl)

        if responseForParam.status_code != 200:
            return {}

        soup = BeautifulSoup(responseForParam.content, "html.parser")

        for (propertyName, propertyValue) in protoConfig.items():
            if propertyValue.startswith("$"):
                protoConfig[propertyName] = soup.find('td', attrs={'class': "setting-name"}, text=propertyValue[1:]).nextSibling.input["value"]

        return protoConfig

    """ Tell if the specified Jenkins URL is of a view
    """
    def isView(self, jenkinsUrl):
        if jenkinsUrl.find("view") > -1 and jenkinsUrl.find("job") == -1:
            return True
        else:
            return False

    """ Tell if the specified Jenkins URL is of a job
    """
    def isJob(self, jenkinsUrl):
        if "job" in jenkinsUrl:
            urlStringArray = jenkinsUrl.split("/")
            urlStringArray.reverse()
            return not (urlStringArray[1]).isdigit()
        else:
            return False

    """ Tell if the specified Jenkins URL is of a build
    """
    def isBuild(self, jenkinsUrl):
        if "job" in jenkinsUrl:
            urlStringArray = jenkinsUrl.split("/")
            urlStringArray.reverse()
            return (urlStringArray[1]).isdigit()
        else:
            return False


    """ Get the URL of the latest build of the specified Jenkins job
    """
    def getLatestBuildUrl(self, jobUrl):
        builds = self.getJenkinsJson(jobUrl, 'builds')
        if (not builds):
            return ''

        if (len(builds) == 0):
            return ''

        return self.getJenkinsJson(jobUrl, 'builds')[0]["url"]

    """ Get the test case reports of the specified Jenkins view
        It's the joint result of all the jobs of the view, with test case reports of the last build of each job
    """
    def getTestCasesByView(self, viewUrl):
        jobs = self.getJobsOfView(viewUrl)
        testCases = []
        for job in jobs:
            buildUrl = self.getLatestBuildUrl(job["url"])
            if (not self.getLatestBuildUrl(job["url"])):
                continue

            jobTestCases = self.getTestCasesByBuild(buildUrl)
            if (not jobTestCases):
                continue

            if (len(jobTestCases) == 0):
                continue

            testCases.append(jobTestCases)

        return testCases

    """ Get the test case count history data for the recent releases
        Might need to cache the data in DB for frozen releases so we don't have to hit Jenkins for each requests.
    """
    def getTestCaseCountForReleases(self):

        testCaseStats = {}

        testCaseStats['Release 008'] = {
            "passed": 892,
            "failed": 116
        }

        testCaseStats['Release 009'] = {
            "passed": 927,
            "failed": 88
        }

        testCaseStats['Release 010'] = {
            "passed": 653,
            "failed": 456
        }

        testCaseStats['Release 011'] = {
            "passed": 952,
            "failed": 155
        }

        return testCaseStats

    """ Get the test case reports of the specified Jenkins build
    """
    def getTestCasesByBuild(self, buildUrl):
        reportUrl = urljoin(buildUrl, 'testReport')
        testSuites = self.getJenkinsJson(reportUrl, 'suites')

        testCases = []
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
                    methodName = methodName[methodNameBracketIndex+2 : serialMethodNameBracketIndex]

                testCase['testMethod'] = methodName

                # set testCase
                caseName = testCase['name']
                if methodNameBracketIndex > -1:
                    serialCountClosingBracketIndex = caseName.find("] ")
                    caseName = caseName[serialCountClosingBracketIndex+2 : methodNameBracketIndex]

                testCase["name"] = caseName
                testCases.append(testCase)

        print("done getting cases for " + buildUrl)
        return testCases

    """ Get the API response of a specified Jenkins URL
        This is how Jenkins exposes it REST APIs, just appending "/api/json?pretty=true" to the url and get the data in JSON
    """
    def getJenkinsJson(self, url, propertyKey=''):
        apiPostfix = 'api/json?pretty=true'
        if (not url.endswith(apiPostfix)):
            if (not url.endswith('/')):
                url += '/'
            url += apiPostfix

        response = requests.get(url)
        if response.status_code != 200:
            return {}

        jsonResponse = response.json()

        if (propertyKey == ''):
            return jsonResponse

        if (propertyKey in jsonResponse):
            return jsonResponse[propertyKey]

        print("'" + propertyKey + "' is not a property of the response for url: " + url)
        return {}


if (__name__ == '__main__'):
    jenkins = Jenkins()

    # viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
    # jobs = jenkins.getJobsOfView(viewUrl)
    # pprint.pprint(jobs)

    jobUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-audience-tests-qa2-release-011/'
    # buildNumber = jenkins.getLatestBuildNumber(jobUrl)
    # print(buildNumber)


    #buildUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-mars-tests-qa2-release-011/5/'
    buildUrl='http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-bulk-bing-tests-qa2-release-011/1/'
    #cases = jenkins.getTestCasesByBuild(buildUrl)
    #pprint.pprint(cases)

    viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
    # cases = jenkins.getTestCasesByView(viewUrl)
    # pprint.pprint(cases)

    developBuildUrl = "http://ci.marinsw.net/view/Qe/view/Develop/view/Tests/view/Microservices/job/qe-conversiontype-tests-develop/14/"
    developJobUrl = "http://ci.marinsw.net/view/Qe/view/Develop/view/Tests/view/Microservices/job/qe-conversiontype-tests-develop/"

    # pprint.pprint(jenkins.getJobConfigs(developBuildUrl))
    # pprint.pprint(jenkins.getJobConfigs(jobUrl))
    #
    # pprint.pprint(jenkins.getJobConfigs(buildUrl))
    # pprint.pprint(jenkins.getJobConfigs(developJobUrl))
    # print(jenkins.getJobConfigs('http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-audience-tests-qa2-release-011'))

    releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-012-qa2/view/Tests/'
    pprint.pprint(jenkins.getTestCasesByView(releaseViewUrl))