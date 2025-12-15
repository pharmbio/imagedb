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
import io
import os
import zipfile
from tornado.web import RequestHandler

from dbqueries import list_all_plates, get_plate, list_image_analyses, move_plate_acq_to_trash, search_compounds, SearchLimits
from imageutils import merge_channels
import settings as imgdb_settings

def myserialize(obj):
    """JSON serializer for objects not serializable by default json code."""

    # Dates and times → ISO 8601 strings
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()

    # Decimals → string to avoid float rounding issues
    if isinstance(obj, decimal.Decimal):
        return str(obj)

    # Fallback for simple dataclass/objects
    if hasattr(obj, "__dict__"):
        return obj.__dict__

    # Last resort: let json deal with it (or fail clearly)
    return obj

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

        field = self.get_argument("field", "").strip() or None

        limits = SearchLimits(
            raw_limit      = self._int(self.get_argument("limit", ""), 100000, 1, 1000000),
            plates         = self._opt_int(self.get_argument("limit_plates", "")),
            acqs_per_plate = self._opt_int(self.get_argument("limit_acqs", "")),
            wells_per_acq  = self._opt_int(self.get_argument("limit_wells", "")),
        )

        logging.info(f"limits: {limits}")

        try:
            payload = search_compounds(q, limits, field)
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

    async def post(self):
        try:
            body = self.request.body.decode("utf-8") or "{}"
            payload = json.loads(body)
        except Exception:
            payload = {}

        logging.info("SaveSelectedImagesHandler payload: %s", payload)

        images = payload.get("images") or []
        merged_rgb = bool(payload.get("merged_rgb"))
        original_channels = bool(payload.get("original_channels"))
        normalize = bool(payload.get("normalize"))
        equalize = bool(payload.get("equalize"))

        if not images or not (merged_rgb or original_channels):
            self.set_status(400)
            self.write({"error": "no images to save or no output type selected"})
            return

        def _safe_part(value, fallback="NA"):
            s = str(value).strip() if value is not None else ""
            if not s:
                s = fallback
            # basic filename sanitization
            s = s.replace("/", "_").replace("\\", "_")
            return s

        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_STORED) as zf:
            for img in images:
                # Core identifiers
                acq_id = _safe_part(img.get("plate_acq_id"), "acq")
                well = _safe_part(img.get("well"), "")
                site = _safe_part(img.get("site"), "")
                zpos = _safe_part(img.get("z"), "")

                # Descriptive metadata (compound_name should not fall back to 'NA')
                batch_id = _safe_part(img.get("batch_id"), "")
                compound_name = _safe_part(img.get("compound_name"), "")
                project = _safe_part(img.get("project"), "")
                barcode = _safe_part(img.get("barcode"), "")

                # Build filename root: include only non-empty pieces
                name_parts = []
                if batch_id:
                    name_parts.append(batch_id)
                if compound_name:
                    name_parts.append(compound_name)
                if project:
                    name_parts.append(project)
                if barcode:
                    name_parts.append(barcode)
                base_name = "_".join(name_parts) if name_parts else "image"

                # Append acquisition / well / site / z info
                suffix_parts = [f"acq{acq_id}"]
                if well:
                    suffix_parts.append(well)
                if site:
                    suffix_parts.append(f"s{site}")
                if zpos:
                    suffix_parts.append(f"z{zpos}")
                suffix = "_".join(suffix_parts)

                base_prefix = f"{base_name}_{suffix}" if base_name else suffix

                # merged RGB image
                if merged_rgb:
                    ch1 = img.get("ch1") or None
                    ch2 = img.get("ch2") or None
                    ch3 = img.get("ch3") or None
                    channels = {}
                    if ch1:
                        channels["1"] = ch1
                    if ch2:
                        channels["2"] = ch2
                    if ch3:
                        channels["3"] = ch3

                    if channels:
                        try:
                            merged_path = await merge_channels(
                                channels,
                                imgdb_settings.IMAGES_CACHE_FOLDER,
                                overwrite_existing=False,
                                normalization=normalize,
                                equalize=equalize,
                            )
                            if merged_path and os.path.isfile(merged_path):
                                _, ext = os.path.splitext(merged_path)
                                if not ext:
                                    ext = ".png"
                                arcname = f"{base_prefix}_merged{ext}"
                                zf.write(merged_path, arcname)
                        except Exception as e:
                            logging.exception("Failed to merge channels for %s", base_prefix)
                            # continue with other images

                # original channel images
                if original_channels:
                    for label in ("ch1", "ch2", "ch3"):
                        ch_path = img.get(label) or None
                        if not ch_path:
                            continue
                        if not os.path.isfile(ch_path):
                            continue
                        _, ext = os.path.splitext(ch_path)
                        arcname = f"{base_prefix}_{label}{ext}"
                        try:
                            zf.write(ch_path, arcname)
                        except Exception:
                            logging.exception("Failed to add channel %s for %s", label, base_prefix)

        mem_zip.seek(0)
        # Return zip file to client
        self.set_header("Content-Type", "application/zip")
        self.set_header("Content-Disposition", "attachment; filename=selected-images.zip")
        self.finish(mem_zip.getvalue())

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
