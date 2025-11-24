#!/usr/bin/env python3
"""
This is where most of the logic goes.

This file has the ListAllPlatesQueryHandler, which parses the search form and does database
queries.
"""
import logging
import jsonpickle
import tornado.web
import json
import datetime
import decimal
from tornado.web import RequestHandler

from dbqueries import list_all_plates, get_plate, list_image_analyses, move_plate_acq_to_trash, search_compounds, SearchLimits

def myserialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.date):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, datetime.time):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    return obj.__dict__

class ListAllPlatesQueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The query handler handles form posts and returns list of results
    """
    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def post(self):
        """Handles POST requests.
        """
        try:
            form_data = self.request.body_arguments
        except Exception as e:
            logging.error("Exception: %s", e)
            form_data = {}

        logging.debug("form_data:" + str(form_data))

        results = list_all_plates()

        retval = {"results": results}
        logging.info("before jsonpickle")
        json_string = jsonpickle.encode(retval, unpicklable=False)
        logging.info("done with jsonpickle")

         # Ensure json_string is a proper string
        if not isinstance(json_string, str):
            json_string = str(json_string)

        self.write(json_string)
        self.finish()


class GetPlateQueryHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def get(self, plate, acqID, wells):
        """Handles GET requests.
        """
        logging.info(f"plate_name: {plate}, acqID: {acqID}, wells: {wells}")

        plates_dict = get_plate(plate)

        data = {"data": plates_dict}

        # Serialize to json the data with the plates dict containing the platemodel objects
        # use other function than tornado default json serializer since we are serializing
        # custom objects

        json_string = json.dumps(data, default=myserialize) # default=lambda x: x.__dict__)
        logging.info("done with json.dumps")

        #json_string = jsonpickle.encode(data, unpicklable=False)
        #logging.info("done with jsonpickle")
        json_string = json_string.replace("</", "<\\/")
        logging.info("done replace jsonstring")

        self.write(json_string)

        logging.info("done write json_string")


class MoveAcqIDToTrashHandler(tornado.web.RequestHandler):
    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def get(self, acqID):
        """Handles GET requests.
        """
        logging.info(f"MoveAcqIDToTrashHandler: {acqID}")

        try:
            result = move_plate_acq_to_trash(acqID)
            if result["status"] == "success":
                self.write(result)
            else:
                self.set_status(500)
                self.write(result)
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})


class SearchCompoundQueryHandler(RequestHandler):

    def get(self):
        q = self.get_argument("q", "").strip()
        if not q:
            self.set_status(400)
            self.write({"error": "missing q"})
            return

        limits = SearchLimits(
            raw_limit      = self._int(self.get_argument("limit", ""), 100000, 1, 1000000),
            plates         = self._opt_int(self.get_argument("limit_plates", "")),
            acqs_per_plate = self._opt_int(self.get_argument("limit_acqs", "")),
            wells_per_acq  = self._opt_int(self.get_argument("limit_wells", "")),
        )

        logging.info(f"limits: {limits}")

        try:
            payload = search_compounds(q, limits)
            self.set_header("Content-Type", "application/json")
            self.write(payload)
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

    @staticmethod
    def _int(raw, default, mn, mx):
        try:
            v = int(raw)
        except Exception:
            return default
        return max(mn, min(mx, v))

    @staticmethod
    def _opt_int(raw):
        s = str(raw).strip()
        if not s:
            return None
        try:
            v = int(s)
            return v if v > 0 else None
        except Exception:
            return None

class SaveSelectedImagesHandler(tornado.web.RequestHandler):  # pylint: disable=abstract-method
    def prepare(self):
        self.set_header("Content-Type", "application/json")

    def post(self):
        try:
            body = self.request.body.decode("utf-8") or "{}"
            payload = json.loads(body)
        except Exception:
            payload = {}

        logging.info("SaveSelectedImagesHandler payload: %s", payload)

        # Stub implementation: just acknowledge the request.
        self.write({"status": "ok", "message": "Save selected images stub"})
        self.finish()

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
