"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.testclass import TestClasser

import unittest

class TestClassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        testClasser = TestClasser("data/ForTest.java")
        cls.methods = testClasser.load()

    def test_getTestMethods_fileParameter(self):
        self.assertEqual(TestClassTest.methods[0]['methodName'], 'test1', 'test1 not found')
        self.assertIn('test.json', TestClassTest.methods[0]['testData'], 'test data not found')
    def test_getTestMethods_method(self):
        self.assertEqual(TestClassTest.methods[1]['methodName'], 'test2', 'test2 not found')
        self.assertEqual(TestClassTest.methods[1]['method'], 'callMethod', 'test data not found')

    def test_getTestMethods_OneFile(self):
        self.assertEqual(TestClassTest.methods[2]['methodName'], 'test3', 'test3 not found')
        self.assertIn('test.json', TestClassTest.methods[2]['testData'], 'test data not found')

    def test_getTestMethods_csvFiles(self):
        self.assertEqual(TestClassTest.methods[4]['methodName'], 'test7', 'test7 not found')
        self.assertListEqual(TestClassTest.methods[4]['testData'], ['test1.json', 'test.json, test2.json, test3.json', 'test4.json'], 'test data not correct')

    def test_getTestMethods_combinationWithPlus(self):
        self.assertEqual(TestClassTest.methods[3]['methodName'], 'test4', 'test4 not found')
        self.assertIn('test.json, test2.json, test3.json', TestClassTest.methods[3]['testData'], 'test data not found')


    def test_getTestMethods_hasIgnore(self):
        self.assertFalse(any(d['methodName'] == 'test6' for d in TestClassTest.methods))



    def test_getTestMethods_commentedOut(self):
        self.assertFalse(any(d['methodName'] == 'test5' for d in TestClassTest.methods))



