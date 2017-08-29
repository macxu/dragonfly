"""Module for CPU related data parsing"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2016, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

import os
import pprint

class Coder:

    def __init__(self, root = '/Users/mxu/Workspace/qe/int'):

        self.codeRoot = root
        self.testsRoot = os.path.join(self.codeRoot, 'tests')
        self.testJsonPath = 'src/test/resources/com'

        self.testJsonExtension = 'Tests.json'

    def getTestProjects(self):

        dirs = os.listdir(self.testsRoot)
        for dirName in dirs:
            if (not os.path.isdir(os.path.join(self.testsRoot, dirName))):
                continue

            print(dirName)


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



if (__name__ == '__main__'):

    coder = Coder()
    # projects = coder.getTestProjects()

    project = 'qe-metadata-service-tests'
    testFiles = coder.getTestJsonFiles(project)
    pprint.pprint(testFiles)

