
"""Module for MongoDB"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import os
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

class Mongo:

    def __init__(self, flaskApp):

        self.server = '10.14.0.8'
        if (os.environ.get('DB_SERVER')):
            self.server = os.environ['DB_SERVER']

        self.port = '29019'
        if (os.environ.get('DB_PORT')):
            self.port = os.environ['DB_PORT']

        self.collection = 'dragonfly'

        flaskApp.config['MONGO_DBNAME'] = self.collection
        flaskApp.config['MONGO_URI'] = 'mongodb://' + self.server + ':' + self.port + '/' + self.collection

        self.app = flaskApp
        self.mongo = PyMongo(flaskApp)

    """ return the mongo instance
    """
    def getReleases(self):
        with self.app.app_context():
            table_releases = self.mongo.db.releases

            docId = table_releases.insert_one({'release-007': 'xxxxxxxxxxx'}).inserted_id
            for doc in table_releases.find():
                print(doc)


if (__name__ == '__main__'):
    mongo = Mongo()
