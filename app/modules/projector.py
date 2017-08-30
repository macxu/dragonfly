"""Module for a maven test project parsing"""

__author__    = "Copyright (c) 2017, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.maven import Mavener

import pprint


class Projector:

    def __init__(self, projectName):

        self.mavener = Mavener()
        self.project = projectName

    def getTestJsonFiles(self):
        return self.mavener.getTestJsonFiles(self.project)

    def getTestDefinitions(self):
        testDefinitions = self.mavener.loadTestDefinitionsByProjectName(self.project)


    def getTestClassFiles(self):
        testClassFiles = self.mavener.getTestClassFiles(self.project)
        return testClassFiles







if (__name__ == '__main__'):

    projector = Projector('qe-metadata-service-tests')
    pprint.pprint(projector.getTestClassFiles())




