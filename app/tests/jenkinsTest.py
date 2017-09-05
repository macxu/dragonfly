"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.jenkins import Jenkins
from app.modules.jenkinsJobReporter import JenkinsJobReporter

import unittest

class JenkinsTest(unittest.TestCase):


    def test_getJobsOfViews(self):
        url = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-009/view/Tests/'

        jenkins = Jenkins()
        jobs = jenkins.getJobsOfView(url)

        self.assertTrue(len(jobs) > 0, "no jobs were found")

        jobUrl = 'http://ci.marinsw.net/job/qe-costrev-google-cost-tests-qa2-release-009/'
        jobFound = False
        for job in jobs:
            if (job['url'] == jobUrl):
                jobFound = True
                break
        self.assertTrue(jobFound, "costrev google job NOT found")

    def test_sortedReportors(self):
        reporters = []
        reporter1 = JenkinsJobReporter()
        reporter1.casesFailed = []
        reporter1.casesPassed = []
        reporter1.casesSkipped = [None]
        reporters.append(reporter1)

        reporter2 = JenkinsJobReporter()
        reporter2.casesFailed = [None]*2
        reporter2.casesPassed = [None]*2
        reporters.append(reporter2)

        reporter3 = JenkinsJobReporter()

        reporter3.casesFailed = [None]*1
        reporter3.casesPassed = [None]*2
        reporter3.casesSkipped = [None]
        reporters.append(reporter3)

        reporter4 = JenkinsJobReporter()

        reporter4.casesFailed = [None]
        reporter4.casesPassed = [None]*3
        reporters.append(reporter4)

        reporter5 = JenkinsJobReporter()
        reporter5.casesFailed = [None]
        reporter5.casesPassed = [None]*3
        reporter5.casesSkipped = [None]
        reporters.append(reporter5)

        jenkins = Jenkins()
        actual = jenkins.sortReporters(reporters)

        expected = [reporter5, reporter4, reporter2, reporter3, reporter1]

        self.assertNotEqual(actual, reporters, "Should not equal")
        self.assertEqual(actual, expected, 'Not equal')


if( __name__ =='__main__' ):
    unittest.main()
