"""Module for a maven test project parsing"""

__author__    = "Copyright (c) 2017, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.maven import Mavener

import pprint

""" a parser for a test project used to get test JSON files, the test definitions in the project etc.
"""
class Projector:

    def __init__(self, projectName):

        self.mavener = Mavener()
        self.project = projectName

    """ Get the test JSON file paths in the Maven project.
    """
    def getTestJsonFiles(self):
        return self.mavener.getTestJsonFiles(self.project)

    """ Get all the test definitions defined in the test JSON's in the Maven project.
    """
    def getTestDefinitions(self):
        testDefinitions = self.mavener.loadTestDefinitionsByProjectName(self.project)
        return testDefinitions

    """ Get all the test class files in the Maven project.
    """
    def getTestClassFiles(self):
        testClassFiles = self.mavener.getTestClassFiles(self.project)
        return testClassFiles


if (__name__ == '__main__'):

    projector = Projector('qe-metadata-service-tests')
    pprint.pprint(projector.getTestClassFiles())




