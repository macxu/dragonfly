"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import unittest

from app.modules.jenkins.jenkinsJobReporter import JenkinsJobReporter


class JenkinsJobReporterTest(unittest.TestCase):

    def test_jenkinsJobReporter(self):
        jenkinsReporter = JenkinsJobReporter('http://ci.marinsw.net/job/qe-mars-tests-qa2-release-011/')
        jenkinsReporter.run()

        testCases = jenkinsReporter.getAllCases()
        self.assertEqual(len(testCases), 441, "Total 441 test cases, actual is " + str(len(testCases)))
