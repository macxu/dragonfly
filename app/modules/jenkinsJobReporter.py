
"""Module for Jenkins reporting"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."


class JenkinsJobReporter:

    def __init__(self, ):
        self.jobUrl = ''
        self.latestBuildUrl = ''
        self.latestBuildNumber = 0

        self.cases = []

        self.casesFailed = []
        self.casesPassed = []
        self.casesSkipped = []

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

        return report

    def setCases(self, testCases):
        self.cases = testCases

        for testCase in self.cases:
            if (testCase['status'] == 'PASSED' or testCase['status'] == 'FIXED'):
                self.casesPassed.append(testCase)
            elif (testCase['status'] == "FAILED"):
                self.casesFailed.append(testCase)
            elif (testCase['status'] == "SKIPPED"):
                self.casesSkipped.append(testCase)
            else:
                print("unrecognized status: " + testCase['status'])


    def getAllCases(self):
        return self.cases

    def getPassedCases(self):
        return self.casesPassed

    def getPassCount(self):
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


if (__name__ == '__main__'):
    jenkinsReporter = JenkinsJobReporter()
