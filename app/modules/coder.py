"""Module for CPU related data parsing"""
from app.modules.rester import Rester

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

        self.testJsonExtension = 'Tests.json'

    def getTestProjects(self):

        projectNames = []
        dirs = os.listdir(self.testsRoot)
        for dirName in dirs:
            if (not os.path.isdir(os.path.join(self.testsRoot, dirName))):
                continue
            projectNames.append(dirName)

        return projectNames


    def getTestJsonFiles(self, testProjectName):

        testJsonPathToScan = self.testsRoot + "/" + testProjectName + "/" + self.testJsonPath

        testFiles = []
        for root, dirs, files in os.walk(testJsonPathToScan):
            path = root.split(os.sep)
            for file in files:
                if (not file.endswith(self.testJsonExtension)):
                    continue
                testFiles.append(os.path.join(root, file))

        return testFiles


    def loadTests(self, testJsonFullPath):

        with open(testJsonFullPath) as data_file:
            jsonData = json.load(data_file)
            return jsonData



if (__name__ == '__main__'):

    coder = Coder()
    # projects = coder.getTestProjects()

    # project = 'qe-metadata-service-tests'
    # testFiles = coder.getTestJsonFiles(project)
    # pprint.pprint(testFiles)

    testJsonFile = '/Users/mxu/Workspace/qe/int/tests/qe-metadata-service-tests/src/test/resources/com/marin/qa/metadata/client/clientCreateTests.json'
    testDefinitions = coder.loadTests(testJsonFile)
    pprint.pprint(testDefinitions)



