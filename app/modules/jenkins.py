
"""Module for Jenkins data parsing"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import pprint
import requests

class Jenkins:

    """ TODO: need a better way to specify the Jenkins server to make it good for general use """
    def __init__(self, server = 'http://ci.marinsw.net/'):

        self.server = server
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
    """
    def getJobConfigs(self, jobUrl):
        pass

    """ Tell if the specified Jenkins URL is of a view
    """
    def isView(self, jenkinsUrl):
        return True

    """ Tell if the specified Jenkins URL is of a job
    """
    def isJob(self, jenkinsUrl):
        return True

    """ Tell if the specified Jenkins URL is of a build
    """
    def isBuild(self, jenkinsUrl):
        return True

    """ Get the URL of the latest build of the specified Jenkins job
    """
    def getLatestBuildUrl(self, jobUrl):
        pass

    """ Get the test case reports of the specified Jenkins view
        It's the joint result of all the jobs of the view, with test case reports of the last build of each job
    """
    def getTestCasesByView(self, viewUrl):
        pass


    """ Get the test case reports of the specified Jenkins build
    """
    def getTestCasesByBuild(self, buildUrl):
        reportUrl = buildUrl + 'testReport/'
        testSuites = self.getJenkinsJson(reportUrl)['suites']

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
                    testCase['testMethod'] = methodName[methodNameBracketIndex+2 : serialMethodNameBracketIndex]

                # set testCase
                caseName = testCase['name']
                if methodNameBracketIndex > -1:
                    serialCountClosingBracketIndex = caseName.find("] ");
                    testCase["name"] = caseName[serialCountClosingBracketIndex+2 : methodNameBracketIndex]

                testCases.append(testCase)

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
        jsonResponse = response.json()

        if (propertyKey == ''):
            return jsonResponse
        else:
            return jsonResponse[propertyKey]


if (__name__ == '__main__'):
    jenkins = Jenkins()

    # viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
    # jobs = jenkins.getJobsOfView(viewUrl)
    # pprint.pprint(jobs)

    jobUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-audience-tests-qa2-release-011/'
    # buildNumber = jenkins.getLatestBuildNumber(jobUrl)
    # print(buildNumber)


    buildUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/job/qe-mars-tests-qa2-release-011/5/'
    cases = jenkins.getTestCasesByBuild(buildUrl)
    pprint.pprint(cases)

