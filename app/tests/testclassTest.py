"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.testclass import TestClasser

import unittest

class TestClassTest(unittest.TestCase):

    def test_getTestMethods_fileParameter(self):
        testFile = '/Users/ssun/git/qe/int/tests/qe-metadata-service-tests/src/test/java/com/marin/qa/metadata/CustomerTest.java' # @FileParameter with one file
        testClasser = TestClasser(testFile)
        testMethods = testClasser.load()
        totalTestData = len(testMethods[0]['testData'])
        print("test data number: " + str(totalTestData))
        self.assertEqual(totalTestData, 1, "Should only one file")

    def test_getTestMethods_method(self):
        testFile = '/Users/ssun/git/qe/int/tests/qe-revenue-upload-validator-service-tests/src/test/java/com/marin/qa/revenueuploadvalidatorservice/BingRevenueUploadValidatorServiceTest.java' # @Parameter with method
        testClasser = TestClasser(testFile)
        testMethods = testClasser.load()
        self.assertIsNotNone(testMethods[0]['method'], "Method field should not be none")

    def test_getTestMethods_csvFiles(self):
        testFile = '/Users/ssun/git/qe/int/tests/qe-bulk-bing-tests/src/test/java/com/marin/qa/bulkbing/campaign/BingCampaignEditTest.java'  # Has an array of csv file
        testClasser = TestClasser(testFile)
        testMethods = testClasser.load()
        totalTestData = len(testMethods[0]['testData'])
        print("test data number: "+ str(totalTestData))
        self.assertGreater( totalTestData, 1, "Should more than one testData")