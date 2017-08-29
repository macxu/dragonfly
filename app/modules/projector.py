"""Module for CPU related data parsing"""
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.coder import Coder

import os
import pprint
import json

class Projector:

    def __init__(self, projectName):

        self.coder = Coder()
        self.project = projectName

    def getTestJsonFiles(self):
        return self.coder.getTestJsonFiles(self.project)

    def loadTestDefinitions(self):
        testDefinitions = self.coder.loadTestDefinitionsByProjectName(self.project)


    def loadTestClassFiles(self):
        testClassFiles = self.coder.getTestClassFiles(self.project)
        return testClassFiles







if (__name__ == '__main__'):

    projector = Projector('qe-metadata-service-tests')
    pprint.pprint(projector.loadTestClassFiles())




