"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import unittest

from app.modules.jenkins.jenkinsJob import JenkinsJob


class JenkinsJobReporterTest(unittest.TestCase):

    def test_jenkinsJobReporter(self):
        jenkinsReporter = JenkinsJob('http://ci.marinsw.net/job/qe-mars-tests-qa2-release-011/')
        jenkinsReporter.run()

        testCases = jenkinsReporter.getAllCases()
        self.assertEqual(len(testCases), 441, "Total 441 test cases, actual is " + str(len(testCases)))

    def test_jenkinsJob_getUser(self):
        releaseJob = 'http://ci.marinsw.net/job/qe-sso-tests-qa2-release-011/'
        jenkinsJob = JenkinsJob(releaseJob)
        jenkinsJob.load()
        self.assertDictEqual({'id': 'adilbagi', 'name': 'Anuradha Dilbagi'}, jenkinsJob.user)


    def test_jenkinsJob_getConfig(self):
        releaseJob = 'http://ci.marinsw.net/job/qe-costrev-bing-cost-tests-qa2-release-011/'
        jenkinsJob = JenkinsJob(releaseJob)
        jenkinsJob.load()
        self.assertDictEqual({'it.test': 'BingCostTest', 'marin.env': 'qa2', 'marin.cluster': 'zod', 'BRANCH_VERSION': 'release-011-SNAPSHOT' }, jenkinsJob.jobConfig)
