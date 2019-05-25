#!/usr/bin/env python3
"""
This is where most of the logic goes.

This file has the QueryHandler, which parses the search form and does database
queries.
"""
import json
import logging

import tornado.web

from dbqueries import list_plates, list_plate


def make_totally_real_query(data):
    """
    Makes a totally real query to a totally real database and returns totally
    real data.
    """
    import random
    real_data = []
    for i in range(random.randint(3,14)):
        real_data += ["bild_%i" % random.randint(16,1853)]
    return real_data

def search_db(query):
    result = list_plates()
    return result

def list_projects(query):
    logging.info('list projs')

    result = list_plates()
    return result


class QueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The query handler handles form posts and returns a list of hits.
    """
    def post(self):
        """Handles POST requests.
        """
        logging.info("Hej")
        try:
            form_data = self.request.body_arguments

        except Exception as e:
            logging.error("Exception: %s", e)
            form_data = []

        logging.info("Hej")
        logging.info("form_data:" + str(form_data))

        results = list_projects(form_data)
        logging.debug(results)
        self.finish({'results':results})


class ListImagesQueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The image list handler returns lists of image names
    """
    def get(self, plate):
        """Handles GET requests.
        """
        logging.info("plate: " + str(plate))

        result = list_plate(plate)

        self.finish({'data':result})