
"""Module for RESTful API with helpful utilities"""

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

import requests
import threading

class Rester(threading.Thread):

    def __init__(self, url = '', propertyKey = ''):
        threading.Thread.__init__(self)

        self.url = url
        self.responseKey = propertyKey

        self.response = {}

        self.metadata = {}

    def getUrl(self):
        return self.url

    def getResponse(self):
        return self.response

    def getMetadata(self):
        return self.metadata

    """ Send rest request to get JSON, return the whole response as JSON or the sub-JSON by the specified key
        This method is to be called in multi-threading
    """
    def run(self):
        self.response = self.getJson(self.url, self.responseKey)
        return self.response


    """ Send rest request to get JSON, return the whole response as JSON or the sub-JSON by the specified key
    """
    def getJson(self, url, propertyKey=''):

        print(url)

        jsonResponse = {}
        try:
            response = requests.get(url)
            jsonResponse = response.json()
        except:
            asf= ""

        if (propertyKey == ''):
            return jsonResponse

        if (propertyKey in jsonResponse):
            return jsonResponse[propertyKey]

        print(propertyKey + " is not a property of the response for url: " + url)
        return {}


