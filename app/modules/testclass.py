"""Module for Java test class parsing"""
from javalang.tree import BinaryOperation, Literal

__author__    = "Copyright (c) 2017, Marin Software"
__copyright__ = "Licensed under GPLv2 or later."

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
        with open(self.javaFile) as file:
            content = file.read()
            tree = javalang.parse.parse(content)
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
                            if type(parameters) == Literal:
                                method['testData'].append(self.stringJoin(parameters))
                            else:
                                for csv in parameters.values:
                                    method['testData'].append(self.stringJoin(csv))

                        break
                if method:
                    testMethods.append(method)
        return testMethods















