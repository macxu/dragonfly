"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import unittest

from app.modules.jenkins.jenkins import Jenkins
from app.modules.jenkins.jenkinsJob import JenkinsJob


class JenkinsTest(unittest.TestCase):

    def setUp(self):
        self.jenkins = Jenkins()

    def test_getJobsOfViews(self):
        url = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-009/view/Tests/'


        jobs = self.jenkins.getJobsOfView(url)

        self.assertTrue(len(jobs) > 0, "no jobs were found")

        jobUrl = 'http://ci.marinsw.net/job/qe-costrev-google-cost-tests-qa2-release-009/'
        jobFound = False
        for job in jobs:
            if (job.getUrl() == jobUrl):
                jobFound = True
                break
        self.assertTrue(jobFound, "costrev google job NOT found")

    def test_sortedReportors(self):
        reporters = []
        reporter1 = JenkinsJob()
        reporter1.casesFailed = []
        reporter1.casesPassed = []
        reporter1.casesSkipped = [None]
        reporters.append(reporter1)

        reporter2 = JenkinsJob()
        reporter2.casesFailed = [None]*2
        reporter2.casesPassed = [None]*2
        reporters.append(reporter2)

        reporter3 = JenkinsJob()

        reporter3.casesFailed = [None]*1
        reporter3.casesPassed = [None]*2
        reporter3.casesSkipped = [None]
        reporters.append(reporter3)

        reporter4 = JenkinsJob()

        reporter4.casesFailed = [None]
        reporter4.casesPassed = [None]*3
        reporters.append(reporter4)

        reporter5 = JenkinsJob()
        reporter5.casesFailed = [None]
        reporter5.casesPassed = [None]*3
        reporter5.casesSkipped = [None]
        reporters.append(reporter5)

        actual = self.jenkins.sortJobs(reporters)

        expected = [reporter5, reporter4, reporter2, reporter3, reporter1]

        self.assertNotEqual(actual, reporters, "Should not equal")
        self.assertEqual(actual, expected, 'Not equal')

    def test_compareViews_sameView(self):
        oldViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
        newViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'

        report = self.jenkins.compareViews(oldViewUrl, newViewUrl)
        self.assertEqual(len(report['added']), 0, 'Same view should has no added jobs')
        self.assertEqual(len(report['deleted']), 0, 'Same view should has no deleted jobs')
        # self.assertEqual(len(report['test case']['deletedCases']), 0, 'Same view should has no deleted test cases')
        # self.assertEqual(len(report['test case']['addedCases']), 0, 'Same view should has no added test cases')

    def test_compareViews(self):
        oldViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-010/view/Tests/'
        newViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'

        report = self.jenkins.compareViews(oldViewUrl, newViewUrl)
        self.assertEqual(len(report['deleted']), 7, 'Should 7 jobs be deleted, actual is '+str(len(report['deleted'])))
        self.assertEqual(len(report['added']), 16, 'Should 16 jobs be added, actual is '+str(len(report['added'])))

        # self.assertEqual(len(report['test case']['addedCases']), 112,'Should 112 test cases be added, actual is '+str(len(report['test case']['addedCases'])))
        # self.assertEqual(len(report['test case']['deletedCases']), 94, 'Should 16 test cases be deleted, acutal is ' + str(len(report['test case']['deletedCases'])))

    def test_findJobsWithSameShortName(self):
        oldJobs=[
            {'url': 'http://ci.marinsw.net/job/qe-activity-log-service-tests-qa2-release-011/'},
            {'url': 'http://ci.marinsw.net/job/qe-audience-tests-qa2-release-011/'},
            {'url':'http://ci.marinsw.net/job/qe-ui-dimensions-tab-tests-qa2-release-011/'}
        ]
        newJobs=[
            {'url': 'http://ci.marinsw.net/job/qe-google-bulk-sync-tests-qa2-release-012/'},
            {'url': 'http://ci.marinsw.net/job/qe-revenue-upload-validator-service-google-tests-qa2-release-012/'},
            {'url': 'http://ci.marinsw.net/job/qe-audience-tests-qa2-release-012/'}
        ]
        expected = [({'url': 'http://ci.marinsw.net/job/qe-audience-tests-qa2-release-011/'},{'url': 'http://ci.marinsw.net/job/qe-audience-tests-qa2-release-012/'})]

        sameJobs = self.jenkins.findJobsWithSameShortName(oldJobs,newJobs)
        self.assertEqual(sameJobs, expected,'actual is ' + str(sameJobs))

    def test_getTestCasesByView(self):

         viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
         cases = self.jenkins.getTestCasesByView(viewUrl)
         self.assertEqual((len(cases)), 1134, "actual total test cases is " + str(len(cases)))

    def test_getLatestBuilUrlsdByView(self):
        viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/'
        jobBuildDic = self.jenkins.getLatestBuildUrlsByView(viewUrl)
        checkJob = 'http://ci.marinsw.net/job/qe-costrev-bing-cost-tests-qa2-release-011/'
        expectBuildUrl = 'http://ci.marinsw.net/job/qe-costrev-bing-cost-tests-qa2-release-011/3/'
        self.assertEqual(jobBuildDic[checkJob], expectBuildUrl)

    def test_isView(self):
        # positive cases
        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-010/view/Tests/'
        self.assertTrue(self.jenkins.isView(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-013-qa2/'
        self.assertTrue(self.jenkins.isView(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-007-labs03-labs03/'
        self.assertTrue(self.jenkins.isView(releaseViewUrl))

        developViewUrl = 'http://ci.marinsw.net/view/Qe/view/Develop/view/Tests/view/Microservices/'
        self.assertTrue(self.jenkins.isView(developViewUrl))

        # negative cases
        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-revenue-bulk-upload-tests-qa2-release-011/'
        self.assertFalse(self.jenkins.isView(releaseJobUrl))

        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-column-selector-bubble-bat-tests-labs03-release-007/'
        self.assertFalse(self.jenkins.isView(releaseJobUrl))

        developJobUrl = 'http://ci.marinsw.net/job/qe-urlb-google-creative-tests-develop/'
        self.assertFalse(self.jenkins.isView(developJobUrl))

        releaseBuildUrl = 'http://ci.marinsw.net/job/qe-tvp-keyword-tests-labs03-release-007/'
        self.assertFalse(self.jenkins.isView(releaseBuildUrl))

        developBuildUrl = 'http://ci.marinsw.net/job/qe-searchetl-product-tests-develop/1/'
        self.assertFalse(self.jenkins.isView(developBuildUrl))

    def test_isJob(self):
        # positive cases
        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-revenue-bulk-upload-tests-qa2-release-011/'
        self.assertTrue(self.jenkins.isJob(releaseJobUrl))

        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-column-selector-bubble-bat-tests-labs03-release-007/'
        self.assertTrue(self.jenkins.isJob(releaseJobUrl))

        developJobUrl = 'http://ci.marinsw.net/job/qe-urlb-google-creative-tests-develop/'
        self.assertTrue(self.jenkins.isJob(developJobUrl))

        # negative cases
        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-010/view/Tests/'
        self.assertFalse(self.jenkins.isJob(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-013-qa2/'
        self.assertFalse(self.jenkins.isJob(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-007-labs03-labs03/'
        self.assertFalse(self.jenkins.isJob(releaseViewUrl))

        developViewUrl = 'http://ci.marinsw.net/view/Qe/view/Develop/view/Tests/view/Microservices/'
        self.assertFalse(self.jenkins.isJob(developViewUrl))

        releaseBuildUrl = 'http://ci.marinsw.net/job/qe-tvp-keyword-tests-labs03-release-007/2/'
        self.assertFalse(self.jenkins.isJob(releaseBuildUrl))

        developBuildUrl = 'http://ci.marinsw.net/job/qe-searchetl-product-tests-develop/1/'
        self.assertFalse(self.jenkins.isJob(developBuildUrl))

    def test_isBuild(self):
        # positive cases
        releaseBuildUrl = 'http://ci.marinsw.net/job/qe-tvp-keyword-tests-labs03-release-007/2/'
        self.assertTrue(self.jenkins.isBuild(releaseBuildUrl))

        developBuildUrl = 'http://ci.marinsw.net/job/qe-searchetl-product-tests-develop/1/'
        self.assertTrue(self.jenkins.isBuild(developBuildUrl))

        # negative cases
        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-010/view/Tests/'
        self.assertFalse(self.jenkins.isBuild(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-013-qa2/'
        self.assertFalse(self.jenkins.isBuild(releaseViewUrl))

        releaseViewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-007-labs03-labs03/'
        self.assertFalse(self.jenkins.isBuild(releaseViewUrl))

        developViewUrl = 'http://ci.marinsw.net/view/Qe/view/Develop/view/Tests/view/Microservices/'
        self.assertFalse(self.jenkins.isBuild(developViewUrl))


        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-revenue-bulk-upload-tests-qa2-release-011/'
        self.assertFalse(self.jenkins.isBuild(releaseJobUrl))

        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-column-selector-bubble-bat-tests-labs03-release-007/'
        self.assertFalse(self.jenkins.isBuild(releaseJobUrl))

        developJobUrl = 'http://ci.marinsw.net/job/qe-urlb-google-creative-tests-develop/'
        self.assertFalse(self.jenkins.isBuild(developJobUrl))

    def test_getJobByBuild(self):
        releaseBuildUrl = 'http://ci.marinsw.net/job/qe-tvp-keyword-tests-labs03-release-007/2/'
        actual = self.jenkins.getJobByBuild(releaseBuildUrl)
        expected = 'http://ci.marinsw.net/job/qe-tvp-keyword-tests-labs03-release-007/'
        self.assertEqual(actual, expected)

        developBuildUrl = 'http://ci.marinsw.net/job/qe-searchetl-product-tests-develop/1/'
        actual = self.jenkins.getJobByBuild(developBuildUrl)
        expected = 'http://ci.marinsw.net/job/qe-searchetl-product-tests-develop/'
        self.assertEqual(actual, expected)

        releaseJobUrl = 'http://ci.marinsw.net/job/qe-ui-revenue-bulk-upload-tests-qa2-release-011/'
        self.assertEqual(self.jenkins.getJobByBuild(releaseJobUrl), releaseJobUrl)

if( __name__ =='__main__' ):
    unittest.main()
