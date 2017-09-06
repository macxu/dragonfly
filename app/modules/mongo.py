
"""Module for MongoDB"""
import pymongo

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import os
from flask import jsonify, json
from flask import request
from bson.json_util import dumps
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

    # """ return the mongo instance
    # """
    # def getReleases(self):
    #     with self.app.app_context():
    #         table = self.mongo.db.releases_stats
    #
    #         docId = table.insert_one({'release-007': 'xxxxxxxxxxx'}).inserted_id
    #         for doc in table.find():
    #             print(doc)

    """ get the stats of all releases
        """
    def getReleasesStats(self):
        with self.app.app_context():
            table = self.mongo.db.releases_stats

            # documents = dumps(table.find())
            documents = table.find().sort([
                ("created", pymongo.DESCENDING)
            ])

            records = dumps(documents)
            recordsJson = json.loads(records)
            return recordsJson


if (__name__ == '__main__'):
    mongo = Mongo()
