"""Module for Java test class parsing"""

__author__    = "Copyright (c) 2017, Marin Software"
__copyright__ = "Licensed under GPLv2 or later."

import pprint
import javalang

""" Parser of a Java test class powered by JUnit
    including the module, class name, test methods, test cases, test JSON files etc.
"""
class TestClasser:

    def __init__(self, javaFilePath):

        self.javaFile = javaFilePath

        self.load()

    def load(self):
        file = open(self.javaFile,'r').read()
        tree = javalang.parse.parse(file)
        className = tree.types[0].name
        testMethods = []
        for testMethod in tree.types[0].body:
            method = {}
            for testAnnotation in testMethod.annotations:
                if testAnnotation.name == 'Test':
                    method['name'] = testMethod.name
                    method['className'] = className
                if testAnnotation.name == 'FileParameters':
                    for parameter in testAnnotation.element:
                        if parameter.name == 'value':
                            method['testJson'] = parameter.value.value.replace('"','')
                            break
                    break
                if testAnnotation.name == 'Parameters':
                    for parameter in testAnnotation.element:
                        if parameter.name == 'method':
                            method['method'] = parameter.value.value.replace('"','')
                            break
                    break
            if method:
                testMethods.append(method)
        return testMethods





if (__name__ == '__main__'):

    testFile = '/Users/ssun/git/qe/int/tests/qe-metadata-service-tests/src/test/java/com/marin/qa/metadata/CustomerTest.java'
    #testFile = '/Users/ssun/git/qe/int/tests/qe-revenue-upload-validator-service-tests/src/test/java/com/marin/qa/revenueuploadvalidatorservice/BingRevenueUploadValidatorServiceTest.java'
    testClasser = TestClasser(testFile)
    pprint.pprint(testClasser.load())







