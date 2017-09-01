"""Module for Java test class parsing"""
from javalang.tree import BinaryOperation, Literal

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

    def removeQuotationMark(self, str):
        if str[0] == '"' and str[-1] == '"':
            return str[1:-1]
        return str

    def stringJoin(self, operationBinary):
        # if operationBinary is a literal return its value else return its operandl + operandr value
        if type(operationBinary) == Literal:
            return self.removeQuotationMark(operationBinary.value)
        return self.stringJoin(operationBinary.operandl) + self.stringJoin(operationBinary.operandr)

    def load(self):
        file = open(self.javaFile,'r').read()
        tree = javalang.parse.parse(file)
        className = tree.types[0].name
        packageName = tree.package.name
        testMethods = []
        for testMethod in tree.types[0].body:
            method = {}
            for testAnnotation in testMethod.annotations:
                # if there is a "@Ignore", it means this test method should be ignored
                if testAnnotation.name == 'Ignore':
                    method = {}
                    break
                if testAnnotation.name == 'Test':
                    # if there is a "@Test" annotation, it means this method is a test method
                    method['methodName'] = testMethod.name
                    method['packageName'] = packageName
                    method['className'] = className
                if testAnnotation.name == 'FileParameters':
                    # if method is empty, it means @Test is commented out. Ignore this method
                    if method:
                        # if there is a "@FileParameter" annotation, it means this method is driven by data file
                        for parameter in testAnnotation.element:
                            if parameter.name == 'value':
                                method['testData'] = []
                                # remove 'classpath:'
                                method['testData'].append(self.removeQuotationMark(parameter.value.value).split('classpath:')[-1])
                                break
                    break
                if testAnnotation.name == 'Parameters':
                    parameters = testAnnotation.element
                    # if parameter is a list it means it has a 'method' to define test data
                    if type(parameters)==list:
                        for parameter in parameters:
                            if parameter.name == 'method':
                                method['method'] = self.removeQuotationMark(parameter.value.value)
                                break
                    else:
                    # if it is not list it means it has multiple files as the test data
                        method['testData'] = []
                        for csv in parameters.values:
                            method['testData'].append(self.stringJoin(csv))

                    break
            if method:
                testMethods.append(method)
        return testMethods





if (__name__ == '__main__'):

    #testFile = '/Users/ssun/git/qe/int/tests/qe-metadata-service-tests/src/test/java/com/marin/qa/metadata/CustomerTest.java'   #Normal case
    #testFile = '/Users/ssun/git/qe/int/tests/qe-revenue-upload-validator-service-tests/src/test/java/com/marin/qa/revenueuploadvalidatorservice/BingRevenueUploadValidatorServiceTest.java' # @Parameter with method
    testFile = '/Users/ssun/git/qe/int/tests/qe-bulk-bing-tests/src/test/java/com/marin/qa/bulkbing/campaign/BingCampaignEditTest.java'      # Has an array of csv file


    #testFile = '/Users/ssun/git/qe/int/tests/qe-google-pacman-tests/src/test/java/com/marin/qa/pacman/google/GooglePacmanCampaignTest.java'    # Has three string combined with '+'
    #testFile = '/Users/ssun/git/qe/int/tests/qe-metadataservice-contract-tests/src/test/java/com/marin/qa/metadataservice/ClientTests.java'
    #testFile = '/Users/ssun/git/qe/int/tests/qe-job-manager-service-tests/src/test/java/com/marin/qa/jobmanagerservice/GetJobByJobIdTest.java'
    #testFile = '/Users/ssun/git/qe/int/tests/qe-search2-urlb-google-tests/src/test/java/com/marin/qa/search2urlbgoogle/GoogleKeywordUrlbSettingDbTest.java'   # has ignore
    #testFile = '/Users/ssun/git/qe/int/tests/qe-repman-tests/src/test/java/com/marin/qa/repman/bing/BingRepmanExtraTests.java'   # @Test has been commented out
    #testFile = '/Users/ssun/git/qe/int/tests/qe-spark-etl-tests/src/test/java/com/marin/qa/sparketl/IncrementalFactSparkTest.java'
    #testFile = '/Users/ssun/git/qe/int/tests/qe-trackingvalueparser-v2-tests/src/test/java/com/marin/qa/trackingvalueparser2/TrackingValueParserV2GoogleGroupsTest.java'
    testClasser = TestClasser(testFile)
    testMethods = testClasser.load()
    pprint.pprint(testMethods)







