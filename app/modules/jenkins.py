
"""Module for Jenkins data parsing"""
from app.modules.jenkinsJobReporter import JenkinsJobReporter
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import pprint
import requests
import xml.dom.minidom as elements
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

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

    """ get the latest build urls by a view url
        the response is organized in key/value pair where the key is the job url and value as the build url
        if there is no build, the build url is set to empty string
    """
    def getLatestBuildUrlsByView(self, viewUrl):
        jobs = self.getJobsOfView(viewUrl)

        jobsCount = len(jobs)
        jobIndex = 0

        resters = []
        for job in jobs:
            jobIndex += 1
            jobUrl = job["url"]
            print("[" + str(jobIndex) + "/" + str(jobsCount) + "]: " + jobUrl)

            jobApiUrl = self.getJenkinsApiUrl(jobUrl)
            jobRester = Rester(jobApiUrl, "builds")
            jobRester.getMetadata()['job'] = jobUrl
            resters.append(jobRester)
            jobRester.start()

        for jobRester in resters:
            jobRester.join()

        builds = {}
        for jobRester in resters:
            resterResponse = jobRester.getResponse()

            if (not resterResponse or len(resterResponse) == 0):
                builds[jobRester.getMetadata()['job']] = ''
            else:
                builds[jobRester.getMetadata()['job']] = resterResponse[0]["url"]

        return builds

    """Compare between job lists, find jobs which they have the same short name
       Return a turple which left is old job , right is new job 
    """
    def findJobsWithSameShortName(self, oldJobs, newJobs):
        # # create dictionary, key is the job short name
        jobNameDictionary = {self.getJobShortName(job['url']): job for job in oldJobs if job}

        # if job short name is existed in the dictionary, we can assume two jobs are the same.
        return [(jobNameDictionary[self.getJobShortName(job['url'])], job) for job in newJobs if
                    self.getJobShortName(job['url']) in jobNameDictionary.keys()]

    """ Get the Jobs difference between two view
        first parameter is the old viewurl
        second parameter is the new viewurl
    """
    def compareViews(self, oldViewUrl, newViewUrl):
        report = {}
        oldJobs = self.getJobsOfView(oldViewUrl)
        newJobs = self.getJobsOfView(newViewUrl)
        sameJobs = self.findJobsWithSameShortName(oldJobs, newJobs)

        deletedJobs = [ job for job in oldJobs if job not in [ jobTurple[0] for jobTurple in sameJobs ]]
        report["deletedJobs"] = deletedJobs
        print("Deleted Jobs")
        pprint.pprint(deletedJobs)
        addedJobs = [ job for job in newJobs if job not in [ jobTurple[1] for jobTurple in sameJobs ]]
        report["addedJobs"] = addedJobs
        print("Added Jobs")
        pprint.pprint(addedJobs)
        report["test case"] = self.compareTestCases(sameJobs)

        return report

    """ Get the test cases difference between same job in the different view
        sameJobs is a turple, left is old job, right is new job
        return a dictionary, contains the added test cases and deleted test cases
    """
    def compareTestCases(self, sameJobs):
        deletedCases = []
        addedCases = []
        oldJobReporters = []
        newJobReporters = []
        report = {}
        for jobTurple in sameJobs:
            # Get old job test cases

            oldJobReporter = JenkinsJobReporter(jobTurple[0]['url'])
            oldJobReporter.start()

            oldJobReporters.append(oldJobReporter)

            # Get new job test cases
            newJobReporter = JenkinsJobReporter(jobTurple[1]['url'])
            newJobReporter.start()

            newJobReporters.append(newJobReporter)

        for reporter in newJobReporters:
            reporter.join()
        for reporter in oldJobReporters:
            reporter.join()

        for old, new in zip(oldJobReporters, newJobReporters):
            oldJobTestCases = old.getAllCases()
            newJobTestCases = new.getAllCases()
            if not len(newJobTestCases) or not len(oldJobTestCases):
                continue
            keySet = set([self.getTestCaseKey(testCase) for testCase in oldJobTestCases])
            addedCases += [testCase for testCase in newJobTestCases if self.getTestCaseKey(testCase) not in keySet]
            sameKeys = [self.getTestCaseKey(testCase) for testCase in newJobTestCases if
                        self.getTestCaseKey(testCase) in keySet]
            # Currently we assume if the new test case's test method, test class and name are the same to the old, they all the same.
            deletedCases += [testCase for testCase in oldJobTestCases if self.getTestCaseKey(testCase) not in sameKeys]

        print("Deleted Test Cases")
        report["deletedCases"] = deletedCases
        pprint.pprint(deletedCases)
        print("Added Test Cases")
        report["addedCases"] = addedCases
        pprint.pprint(addedCases)
        return report

    def getTestCaseKey(self, testCase):
        return testCase['name']+testCase['testClass']+testCase['testMethod']

    """ Get the test case reports of the specified Jenkins view
        It's the joint result of all the jobs of the view, with test case reports of the last build of each job
    """
    def getTestCasesByView(self, viewUrl):
        jobs = self.getJobsOfView(viewUrl)

        jobsCount = len(jobs)
        jobIndex = 0

        jobHunters = []
        for job in jobs:
            jobIndex += 1
            jobUrl = job["url"]
            print("[" + str(jobIndex) + "/" + str(jobsCount) + "]: " + jobUrl)

            jobHunter = JenkinsJobReporter(jobUrl)
            jobHunters.append(jobHunter)
            jobHunter.start()

        for jobHunter in jobHunters:
            jobHunter.join()

        testCases = []
        for jobHunter in jobHunters:
            testCases += jobHunter.getAllCases()

        return testCases

    """ Sort the reporters, default is to sort by the number of test cases being executed, desc
        Ordering:
        1. number of total test cases being executed, desc
        2. number of passed cases, desc 
    """
    def sortReporters(self, reporters):
        reporters = sorted(reporters, key = lambda k: (len(k.getAllCases()), len(k.casesPassed)), reverse=True)
        return reporters


    """ Get the test case reports of the specified Jenkins view
            It's the joint result of all the jobs of the view, with test case reports of the last build of each job
        """
    def getReportersByView(self, viewUrl):
        jobs = self.getJobsOfView(viewUrl)

        jobsCount = len(jobs)
        jobIndex = 0

        reporters = []
        for job in jobs:
            jobIndex += 1

            jobUrl = job["url"]
            print("[" + str(jobIndex) + "/" + str(jobsCount) + "]: " + jobUrl)

            reporter = JenkinsJobReporter(jobUrl)
            reporter.setViewUrl(viewUrl)
            reporter.start()
            reporters.append(reporter)

        for reporter in reporters:
            reporter.join()

        orderedReporters = self.sortReporters(reporters)
        return orderedReporters

    """ Report the test case stats of the specified Jenkins view
            It's the joint result of all the jobs of the view, with test case reports of the last build of each job
        """
    def reportByView(self, viewUrl):

        testCases = self.getTestCasesByView(viewUrl)

        passedCount = 0
        failedCount = 0
        skippedCount = 0
        for testCase in testCases:

            if (testCase['status'] == 'PASSED' or testCase['status'] == 'FIXED'):
                passedCount += 1
            elif (testCase['status'] == "FAILED"):
                failedCount += 1
            elif (testCase['status'] == "SKIPPED"):
                skippedCount += 1
            else:
                print("unrecognized status: " + testCase['status'])

        stats = {
            "passed": passedCount,
            "failed": failedCount,
            "skipped": skippedCount,
            "total": passedCount + failedCount + skippedCount
        }

        return stats




    """ Get the test case count history data for the recent releases
        Might need to cache the data in DB for frozen releases so we don't have to hit Jenkins for each requests.
    """
    def getTestCaseCountForReleases(self):

        testCaseStats = {}

        testCaseStats['release-008'] = {
            "passed": 892,
            "failed": 116,
            "skipped": 0
        }

        testCaseStats['release-009'] = {
            "passed": 927,
            "failed": 88,
            "skipped": 0
        }

        testCaseStats['release-010'] = {
            "passed": 653,
            "failed": 456,
            "skipped": 0
        }

        testCaseStats['release-011'] = {
            "passed": 952,
            "failed": 155
        }

        testCaseStats['release-012-qa2'] = {
            "passed": 1052,
            "failed": 72,
            "skipped": 15
        }

        return testCaseStats

    """ Get the test case reports of the specified Jenkins build
    """
    def getTestCasesByBuild(self, buildUrl):

        reporter = self.getReporterByBuild(buildUrl)

        return reporter.getAllCases()

    """ Get the test case reports of the specified Jenkins build
        """
    def getReporterByBuild(self, buildUrl):
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
                    methodName = methodName[methodNameBracketIndex + 2: serialMethodNameBracketIndex]

                testCase['testMethod'] = methodName

                # set testCase
                caseName = testCase['name']
                if methodNameBracketIndex > -1:
                    serialCountClosingBracketIndex = caseName.find("] ")
                    caseName = caseName[serialCountClosingBracketIndex + 2: methodNameBracketIndex]

                testCase["name"] = caseName
                testCases.append(testCase)

        print("        done getting cases for " + buildUrl)
        reporter = JenkinsJobReporter()
        reporter.latestBuildUrl = buildUrl
        reporter.jobShortName = self.getJobShortName(buildUrl)
        reporter.setCases(testCases)

        return reporter

    def getJobShortName(self, jenkinsUrl):
        # form: http://ci.marinsw.net/job/qe-bulk-bing-sync-tests-qa2-release-012/1
        # to:   bulk-bing-sync
        matchObj = re.match(r'.*/job/(.*)/.*', jenkinsUrl, re.M | re.I)

        if (not matchObj):
            return ''

        jobName = matchObj.group(1)
        matchObj = re.match(r'.*/job/qe-(.*)-test[s]?-.*', jenkinsUrl, re.M | re.I)

        if (not matchObj):
            return ''

        return matchObj.group(1)

    def getJenkinsApiUrl(self, url):
        apiPostfix = 'api/json?pretty=true'
        if (not url.endswith(apiPostfix)):
            if (not url.endswith('/')):
                url += '/'
            url += apiPostfix

        return url

    """ Get the API response of a specified Jenkins URL
        This is how Jenkins exposes it REST APIs, just appending "/api/json?pretty=true" to the url and get the data in JSON
    """
    def getJenkinsJson(self, url, propertyKey=''):
        url = self.getJenkinsApiUrl(url)

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
    releaseViewUrlOld = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'

    # reporter = JenkinsJobReporter('http://ci.marinsw.net/job/qe-google-bulk-campaign-tests-qa2-release-012/')
    # reporter.start()
    # reporter.join()
    # reporter.getAllCases()

    report = jenkins.compareViews(releaseViewUrlOld,releaseViewUrl)

    # pprint.pprint(jenkins.getTestCasesByView(releaseViewUrl))

    # reporters = jenkins.getReportersByView(releaseViewUrl)
    #
    # for reporter in reporters:
    #     pprint.pprint(reporter.getReport())
    # # pprint.pprint(jenkins.getReportersByView(releaseViewUrl))

    #pprint.pprint(jenkins.reportByView(releaseViewUrl))