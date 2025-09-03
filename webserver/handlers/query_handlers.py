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

from dbqueries import list_all_plates, get_plate, list_image_analyses, move_plate_acq_to_trash, search_compounds

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

    def get(self):
       """Handles GET requests using query parameters:
       /api/plate?barcode=...&acqID=...&wells=A01,B03
       """
       # Accept multiple possible param names for robustness
       plate = self.get_argument('barcode', default=None)
       acqID = self.get_argument('acqID', default=None)
       wells_arg = self.get_argument('wells', default=None)

       if not plate:
           raise tornado.web.HTTPError(400, reason="Missing required parameter: barcode")

       logging.info("plate_name: " + str(plate))

       # Prepare optional well filter (comma-separated)
       well_filter = None
       if wells_arg:
           well_filter = [w.strip() for w in wells_arg.split(',') if w.strip()]

       plates_dict = get_plate(plate, well_filter)

       data = {"data": plates_dict}


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

class SearchCompoundQueryHandler(tornado.web.RequestHandler):
    """
    GET /api/search-compound?q=…[&limit=1000]
      → returns JSON: { results: [ { barcode, plate_acquisition_id, well_id }, … ] }
      up to `limit` rows (default 1000).
    """
    def get(self):
        q     = self.get_argument("q", "").strip()
        limit = self.get_argument("limit", "1000")
        try:
            limit = int(limit)
        except ValueError:
            limit = 1000

        if not q:
            return self.write(json.dumps({"results": []}))

        try:
            # search_compounds(term, limit) should cap total rows
            hits = search_compounds(q, limit=limit)

            # build minimal flat result
            results = [
                {
                  "barcode":                r["barcode"],
                  "plate_acquisition_id":   r["plate_acquisition_id"],
                  "well_id":                r["well_id"]
                }
                for r in hits
            ]

            self.write(json.dumps({"results": results}))

        except Exception as e:
            logging.exception("Error in SearchCompoundQueryHandler")
            self.set_status(500)
            self.write(json.dumps({"error": str(e)}))


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

