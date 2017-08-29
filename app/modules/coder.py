"""Module for CPU related data parsing"""

__author__    = "Copyright (c) 2016, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

import os
import pprint
import json

class Coder:

    def __init__(self, root = '/Users/mxu/Workspace/qe/int'):

        self.codeRoot = root
        self.testsRoot = os.path.join(self.codeRoot, 'tests')
        self.testJsonPath = 'src/test/resources/com'
        self.testClassPath = 'src/test/java/com'

        self.testJsonExtension = 'Tests.json'
        self.testClassExtension = 'Test.java'

    def getTestProjects(self):

        projectNames = []
        dirs = os.listdir(self.testsRoot)
        for dirName in dirs:
            if (not os.path.isdir(os.path.join(self.testsRoot, dirName))):
                continue
            projectNames.append(dirName)

        return projectNames

    def getTestClassFiles(self, testProjectName):

        dirToScan = self.testsRoot + "/" + testProjectName + "/" + self.testClassPath

        testClassFiles = []
        for root, dirs, files in os.walk(dirToScan):
            for file in files:
                if (not file.endswith(self.testClassExtension)):
                    continue
                testClassFiles.append(os.path.join(root, file))

        return testClassFiles

    def getTestJsonFiles(self, testProjectName):

        dirToScan = self.testsRoot + "/" + testProjectName + "/" + self.testJsonPath

        testFiles = []
        for root, dirs, files in os.walk(dirToScan):
            for file in files:
                if (not file.endswith(self.testJsonExtension)):
                    continue
                testFiles.append(os.path.join(root, file))

        return testFiles

    def loadTestDefinitionsByProjectName(self, projectName):

        testJsonFiles = self.getTestJsonFiles(projectName);

        tests = [];
        for testJsonFile in testJsonFiles:
            testsByProject = self.loadTestDefinitionsByFilePath(testJsonFile)
            tests += testsByProject

        return tests


    def loadTestDefinitionsByFilePath(self, testJsonFullPath):

        with open(testJsonFullPath) as data_file:
            jsonData = json.load(data_file)
            return jsonData



if (__name__ == '__main__'):

    coder = Coder()
    # projects = coder.getTestProjects()

    # project = 'qe-metadata-service-tests'
    # testFiles = coder.getTestJsonFiles(project)
    # pprint.pprint(testFiles)

    # testJsonFile = '/Users/mxu/Workspace/qe/int/tests/qe-metadata-service-tests/src/test/resources/com/marin/qa/metadata/client/clientCreateTests.json'
    # testDefinitions = coder.loadTestDefinitionsByFilePath(testJsonFile)
    # pprint.pprint(testDefinitions)

    testProjectName = 'qe-metadata-service-tests'
    testDefinitions = coder.loadTestDefinitionsByProjectName(testProjectName)
    pprint.pprint(testDefinitions)



