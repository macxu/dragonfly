
"""Module for MongoDB"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import os

class Mongo:

    def __init__(self):

        self.server = '10.14.0.8'
        if (os.environ.get('DB_SERVER')):
            self.server = os.environ['DB_SERVER']

        self.port = '29019'
        if (os.environ.get('DB_PORT')):
            self.port = os.environ['DB_PORT']

        self.collection = 'dragonfly'

    """ Connect to Mongo DB Server
    """
    def connect(self):
        pass


if (__name__ == '__main__'):
    mongo = Mongo()
