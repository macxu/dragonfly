"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2016, Mac Xu <shinyxxn@hotmail.com>"
__copyright__ = "Licensed under GPLv2 or later."

import requests

class Rester:

    def __init__(self):
        pass
    
    def getJson(self, url, propertyKey=''):

        response = requests.get(url)
        jsonResponse = response.json()

        if (propertyKey == ''):
            return jsonResponse
        else:
            return jsonResponse[propertyKey]


