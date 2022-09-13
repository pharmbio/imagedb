#!/usr/bin/env python3
"""
This is where most of the logic goes.

This file has the ListAllPlatesQueryHandler, which parses the search form and does database
queries.
"""
import json
import logging

import tornado.web

from dbqueries import list_all_plates, get_plate, list_image_analyses


def make_totally_real_query(data):
    """
    Makes a totally real query to a totally real database and returns totally
    real data for testing
    """
    import random
    real_data = []
    for i in range(random.randint(3,14)):
        real_data += ["bild_%i" % random.randint(16,1853)]
    return real_data


class ListAllPlatesQueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The query handler handles form posts and returns list of results
    """
    def post(self):
        """Handles POST requests.
        """
        try:
            form_data = self.request.body_arguments

        except Exception as e:
            logging.error("Exception: %s", e)
            form_data = []

        logging.debug("form_data:" + str(form_data))

        hide_unpublished = self.get_argument("hide-unpublished-cb")

        results = list_all_plates(hide_unpublished)
        logging.debug(results)
        self.finish({'results':results})


class GetPlateQueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def get(self, plate):
        """Handles GET requests.
        """
        logging.info("plate_name: " + str(plate))

        plates_dict = get_plate(plate)

        data = {"data": plates_dict}

        # Serialize to json the data with the plates dict containing the platemodel objects
        # use other function than tornado default json serializer since we are serializing
        # custom objects
        json_string = json.dumps(data, default=lambda x: x.__dict__).replace("</", "<\\/")

        self.write(json_string)


#####
#####  From pipelinegui
#####

class ListImageAnalysesHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def get(self, limit, sortorder, plate_barcode):
        """Handles GET requests.
        """
        logging.info("inside ListImageAnalysesHandler, limit=" + str(limit))

        result = list_image_analyses(plate_barcode)

        logging.debug(result)
        self.finish({'result':result})