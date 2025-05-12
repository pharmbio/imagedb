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

    def get(self, plate, acqID):
        """Handles GET requests.
        """
        logging.info("plate_name: " + str(plate))

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

class SearchCompoundQueryHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        q = self.get_argument("q", "").strip()
        if not q:
            return self.write(json.dumps({"plates": []}))

        try:
            # 1) Do the free-text search, get flat rows
            hits = search_compounds(q)

            # 2) Group matching well_ids by (barcode, acquisition)
            plates_map: dict[tuple, set] = {}
            for r in hits:
                key = (
                    r["barcode"],
                    r["plate_acquisition_id"],
                    r["plate_acquisition_name"],
                )
                plates_map.setdefault(key, set()).add(r["well_id"])

            # 3) For each plate/acq, pull only those wells
            result_plates = []
            for (barcode, acq_id, acq_name), wells in plates_map.items():
                # well_filter trims the plate JSON to only these wells
                full_plate = get_plate(barcode, well_filter=list(wells))

                logging.info(f"{full_plate}")

                plate_data = full_plate["plates"].get(barcode, {})

                result_plates.append({
                    "barcode": barcode,
                    "plate_acquisition_id": acq_id,
                    "plate_acquisition_name": acq_name,
                    "plate": plate_data
                })

            # 4) Return the array of filtered plates
            self.write(json.dumps({"plates": result_plates}, default=myserialize))

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

