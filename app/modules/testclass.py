"""Module for Java test class parsing"""

__author__    = "Copyright (c) 2017, Marin Software"
__copyright__ = "Licensed under GPLv2 or later."

import pprint

""" Parser of a Java test class powered by JUnit
    including the module, class name, test methods, test cases, test JSON files etc.
"""
class TestClasser:

    def __init__(self, javaFilePath):

        self.javaFile = javaFilePath

        self.load()

    def load(self):
        pass



if (__name__ == '__main__'):

    testFile = '/Users/mxu/Workspace/qe/int/tests/qe-metadata-service-tests/src/test/java/com/marin/qa/metadata/CustomerTest.java'
    testClasser = TestClasser(testFile)
    pprint.pprint(testClasser.load())




