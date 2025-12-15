#!/usr/bin/env python3
import logging
import json
import psycopg2
import psycopg2.pool
import psycopg2.extras
from datetime import datetime
import settings as imgdb_settings
import platemodel
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


__connection_pool = None


def get_connection():


    global __connection_pool
    if __connection_pool is None:
        __connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, user = imgdb_settings.DB_USER,
                                              password = imgdb_settings.DB_PASS,
                                              host = imgdb_settings.DB_HOSTNAME,
                                              port = imgdb_settings.DB_PORT,
                                              database = imgdb_settings.DB_NAME)

    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)


def get_plate_old(plate_name):
    logging.info("inside get_plate, plate_name:" + plate_name)

    conn = None
    try:

        conn = get_connection()

        return_cols = ['plate_barcode',
                       'project',
                       'plate_acquisition_id',
                       'plate_acquisition_name',
                       'folder',
                       'timepoint',
                       'path',
                       'well',
                       'site',
                       'z',
                       'channel',
                       'dye',
                       'cell_line'
                       ]

        query = ("SELECT " + ",".join(return_cols) +
                 " FROM images_minimal_view"
                 " WHERE plate_barcode = %s"
                 " ORDER BY timepoint, plate_acquisition_id, well, site, z, channel")

        logging.debug("query" + query)

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        logging.info(cursor.mogrify(query, (plate_name, )))

        cursor.execute(query, (plate_name, ))

        logging.info("after exec")

        # create a list with all results as key-values
        #resultlist = [dict(zip([key[0] for key in cursor.description], row)) for row in cursor]

        resultlist = cursor.fetchall()

        logging.info("after dict")

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        logging.info("len(resultlist):" + str(len(resultlist)))

        # create a nested json object of all images.
        # A plate object containing all plate_acquisitions. The plate_acquisitions containing all wells and then
        # all sites, and then channels with the image path
        plates_dict = {}
        for image in resultlist:
            plate_id = image['plate_barcode']
            # get or create a new object with this key
            plate = plates_dict.setdefault(plate_id, platemodel.Plate(plate_id))
            plate.add_data(image)

        #
        # Add plate layout meta to result
        #

        conn = get_connection()

        query = ("SELECT * " +
                 " FROM plate_v1"
                 " WHERE barcode = %s"
                 " ORDER BY well_id")

        logging.debug("query" + query)

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        logging.info(cursor.mogrify(query, (plate_name, )))

        cursor.execute(query, (plate_name, ))

        #rows = [dict(zip([key[0] for key in cursor.description], row)) for row in cursor]

        rows = cursor.fetchall()

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        # create a dict with well_id as key to metadata (metadata is a list of rows since there can be multiple compound combinations per well)
        layout_dict = defaultdict(list)
        for row in rows:
            well_id = row['well_id']
            layout_dict[well_id].append(row)

        # add layout to plate (if we have a plate entry)
        if plate_name in plates_dict:
            plate = plates_dict[plate_name]
            plate.add_layout(layout_dict)
        else:
            # No image rows for this plate_barcode; optionally attach layout only,
            # or return an empty dict so callers can handle "no such plate".
            logging.info("No image rows found for plate %s; returning empty plates dict", plate_name)
            return {"plates": {}}

        result_dict = {"plates": plates_dict}
        logging.info("done with get_plate, plate_name:" + plate_name)
        return result_dict

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


def get_plate_json_via_python(plate_name, well_filter=None):
    """
    Original Python-based get_plate, renamed with optional well_filter.
    """
    logging.info(f"inside get_plate_json_via_python: {plate_name}, wells={well_filter}")
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Query images_minimal_view
        cols = [
            'plate_barcode','project','plate_acquisition_id','plate_acquisition_name',
            'folder','timepoint','path','well','site','z','channel','dye','cell_line'
        ]
        query = f"SELECT {','.join(cols)} FROM images_minimal_view WHERE plate_barcode = %s"
        params = [plate_name]
        if well_filter:
            query += " AND well = ANY(%s)"
            params.append(well_filter)
        query += " ORDER BY timepoint, plate_acquisition_id, well, site, z, channel"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        plates_dict = {}
        for img in rows:
            pid = img['plate_barcode']
            plate = plates_dict.setdefault(pid, platemodel.Plate(pid))
            plate.add_data(img)
        # Query layout
        layout_query = "SELECT * FROM plate_v1 WHERE barcode = %s"
        layout_params = [plate_name]
        if well_filter:
            layout_query += " AND well_id = ANY(%s)"
            layout_params.append(well_filter)
        layout_query += " ORDER BY well_id"
        cursor.execute(layout_query, layout_params)
        layout_rows = cursor.fetchall()
        layout_dict = defaultdict(list)
        for lr in layout_rows:
            layout_dict[lr['well_id']].append(lr)
        # Attach layout
        if plate_name in plates_dict:
            plates_dict[plate_name].add_layout(layout_dict)
        else:
            p = platemodel.Plate(plate_name)
            p.add_layout(layout_dict)
            plates_dict[plate_name] = p
        return {'plates': plates_dict}
    finally:
        if conn:
            cursor.close()
            put_connection(conn)


def get_plate(plate_name, acqID=None, well_filter=None):

    return get_plate_old(plate_name)


def list_all_plates():

    logging.info("inside list_all_plates")

    conn = None
    try:

        conn = get_connection()

        query = ("SELECT DISTINCT name, plate_barcode, project, id, hidden, microscope "
                 " FROM plate_acquisition "
                 " ORDER BY project, name, plate_barcode, id")

        logging.info("query" + str(query))

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute(query)

        resultlist = cursor.fetchall()

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        #logging.debug(json.dumps(resultlist, indent=2))

        return resultlist

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


###
### From pipelinegui
###

def list_plate_acquisitions():

    query = ("SELECT * "
             "FROM plate_acquisition "
             "ORDER BY id DESC "
             "LIMIT 1000")

    return select_from_db(query)

def list_image_analyses(plate_barcode="", plate_acq_id=""):

    logging.info("plate_barcode=" + plate_barcode)

    barcode_filter = ""
    if plate_barcode != "":
      barcode_filter = " WHERE plate_barcode = '" + plate_barcode + "' "

    plate_acq_id_filter = ""
    if plate_acq_id != "":
      plate_acq_id_filter = " WHERE plate_acquisition_id = " + plate_acq_id + " "


    query = ("SELECT * "
             "FROM image_analyses_v1 " +
             barcode_filter +
             plate_acq_id_filter +
             "ORDER BY id DESC "
             "LIMIT 1000")

    return select_from_db(query)


def list_image_sub_analyses():

    query = ("SELECT * "
             "FROM image_sub_analyses_v1 "
             "ORDER BY sub_id DESC "
             "LIMIT 1000")

    return select_from_db(query)


def select_from_db(query):

    logging.debug("Inside select from query")
    logging.info("query=" + str(query))

    conn = None
    try:

        conn = get_connection()

        cursor = conn.cursor()
        cursor.execute(query)

        colnames = [desc[0] for desc in cursor.description]

        rows = cursor.fetchall()

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        resultlist = []

        # Add column headers
        resultlist = [colnames] + rows

        # First dump to string (This is because datetime cant be converted to string without the default=str function)
        result_jsonstring = json.dumps(resultlist, indent=2, default=str)

        # Then reload into json
        result = json.loads(result_jsonstring)

        # logging.debug(json.dumps(result, indent=2, default=str))

        return result

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


def move_plate_acq_to_trash(acqid):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE plate_acquisition
            SET project = 'trash'
            WHERE id = %s
        """

        cursor.execute(update_query, (acqid,))
        conn.commit()

        cursor.close()
        put_connection(conn)
        conn = None

        logging.info(f"Successfully moved plate acquisition ID {acqid} to trash.")
        return {"status": "success", "message": f"Plate acquisition ID {acqid} moved to trash"}

    except (Exception, psycopg2.DatabaseError) as err:
        if conn is not None:
            conn.rollback()
        logging.exception("Failed to move plate acquisition to trash.")
        return {"status": "error", "message": str(err)}

    finally:
        if conn is not None:
            put_connection(conn)


@dataclass
class SearchLimits:
    raw_limit: int = 10000                  # hard cap on flat DB scan
    plates: Optional[int] = None           # max plates per project
    acqs_per_plate: Optional[int] = None   # max acquisitions per plate
    wells_per_acq: Optional[int] = None    # max wells per acquisition

def _take(it: Iterable[Any], n: Optional[int]) -> List[Any]:
    if n is None:
        return list(it)
    out = []
    for i, x in enumerate(it):
        if i >= n: break
        out.append(x)
    return out

def search_compounds(term: str, limits: Optional[SearchLimits] = None, field: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a project -> plate -> acquisition -> wells hie    except (Exception, psycopg2.DatabaseError) as err:
        if conn is not None:
            conn.rollback()
        logging.exception("Failed to search compounds.")
        return {"status": "error", "message": str(err)}rarchy from plate_layout_view_more,
    including acquisition dates (from 'imaged') and a project-level latest date.

    Returns:
      {
        "data": {
          "projects": {
            "<project>": {
              "id": "<project>",
              "date_iso": "YYYY-MM-DDTHH:MM:SS" | null,
              "plates": {
                "<barcode>": {
                  "id": "<barcode>",
                  "acquisitions": {
                    "<acq_id>": {
                      "id": <acq_id>,
                      "date_iso": "YYYY-MM-DDTHH:MM:SS" | null,
                      "wells": ["A01","B03", ...]
                    }
                  }
                }
              }
            }
          }
        },
        "meta": { "query": term, "limits": {...}, "counts": {...} }
      }
    """
    def iso(dt):
        return dt.isoformat() if isinstance(dt, datetime) else (dt.isoformat() if dt else None)

    if limits is None:
        limits = SearchLimits()

    conn = get_connection()
    cursor = None

    like = f"%{term}%"

    # IMPORTANT:
    # - We keep WHERE predicates ONLY on the compound-side columns so "preserve plate_layout rows"
    #   semantics are honored by how you materialized the view. The view itself should be built with
    #   LEFT JOINs so non-matching compounds still appear (compound columns NULL).
    # - We OR both v.compound_name and v.name to be resilient to column naming in the view.
    # Map allowed field keys to column expressions in the view
    field_map = {
        "batchid": "v.batchid::text",
        "cbkid": "v.cbkid",
        "libid": "v.libid",
        "libtxt": "v.libtxt",
        "smiles": "v.smiles",
        "inchi": "v.inchi",
        "inkey": "v.inkey",
        "name": "v.name",
        "plate_acquisition_name": "v.plate_acquisition_name",
        "barcode": "v.barcode",
        "project": "v.project",
    }

    where_clauses = []
    params: Dict[str, Any] = {"like": like, "limit": limits.raw_limit}

    if field and field in field_map:
        # Restrict search to the selected field
        where_clauses.append(f"{field_map[field]} ILIKE %(like)s")
    else:
        # Any field: search across all known columns
        where_clauses.append(
            "      v.batchid::text           ILIKE %(like)s "
            "   OR v.cbkid                   ILIKE %(like)s "
            "   OR v.libid                   ILIKE %(like)s "
            "   OR v.libtxt                  ILIKE %(like)s "
            "   OR v.smiles                  ILIKE %(like)s "
            "   OR v.inchi                   ILIKE %(like)s "
            "   OR v.inkey                   ILIKE %(like)s "
            "   OR v.name                    ILIKE %(like)s "
            "   OR v.plate_acquisition_name  ILIKE %(like)s "
            "   OR v.barcode                 ILIKE %(like)s "
            "   OR v.project::text           ILIKE %(like)s "
        )

    query = (
        "SELECT "
        "  v.project                         AS project, "
        "  v.barcode                         AS barcode, "
        "  v.plate_acquisition_id            AS plate_acquisition_id, "
        "  v.plate_acquisition_name          AS plate_acquisition_name, "
        "  GREATEST("
        "     COALESCE(v.imaged,  '-infinity'::timestamp),"
        "     COALESCE(v.painted, '-infinity'::timestamp)"
        "        )                           AS acq_date, "
        "  v.well_id                         AS well_id "
        "FROM plate_layout_view_more v "
        "WHERE ("
        + " ".join(where_clauses) +
        ") "
        "  AND v.plate_acquisition_id IS NOT NULL "
        "ORDER BY v.project, v.barcode, v.plate_acquisition_id, v.well_id "
        "LIMIT %(limit)s"
    )

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Build in-memory index:
        # project -> plate barcode -> acq_id -> {"date": datetime|None, "wells": [well_ids]}
        projects_idx: Dict[str, Dict[str, Dict[int, Dict[str, Any]]]] = {}
        project_latest: Dict[str, Optional[datetime]] = {}

        uniq_projects = set()
        uniq_plates: set[Tuple[str, str]] = set()
        uniq_acqs: set[Tuple[str, str, int]] = set()
        uniq_wells: set[Tuple[str, str, int, str]] = set()

        for r in rows:
            # Skip rows that don't have a concrete plate or acquisition;
            # they cannot be visualized and would cause /api/plate/None/... lookups.
            if r["barcode"] is None or r["plate_acquisition_id"] is None or r["well_id"] is None:
                continue

            project = str(r["project"]) if r["project"] is not None else "Unknown project"
            barcode = str(r["barcode"])
            acq_id  = int(r["plate_acquisition_id"])
            well_id = str(r["well_id"])
            acq_dt  = r.get("acq_date")  # datetime or None

            uniq_projects.add(project)
            uniq_plates.add((project, barcode))
            uniq_acqs.add((project, barcode, acq_id))
            uniq_wells.add((project, barcode, acq_id, well_id))

            by_plate = projects_idx.setdefault(project, {})
            by_acq_map = by_plate.setdefault(barcode, {})
            acq_entry = by_acq_map.setdefault(acq_id, {"date": acq_dt, "wells": []})
            # if later rows for same acq have date, prefer non-null / latest
            if acq_dt and (acq_entry.get("date") is None or acq_dt > acq_entry["date"]):
                acq_entry["date"] = acq_dt
            if well_id not in acq_entry["wells"]:
                acq_entry["wells"].append(well_id)

            # track latest date at the project level
            if acq_dt:
                prev = project_latest.get(project)
                if prev is None or acq_dt > prev:
                    project_latest[project] = acq_dt

        # Serialize with limits
        def _take(it: Iterable[Any], n: Optional[int]) -> List[Any]:
            if n is None:
                return list(it)
            out = []
            for i, x in enumerate(it):
                if i >= n: break
                out.append(x)
            return out

        projects_json: Dict[str, Any] = {}
        for project, plate_map in projects_idx.items():
            plates_json: Dict[str, Any] = {}
            for barcode in _take(sorted(plate_map.keys()), limits.plates):
                acq_map = plate_map[barcode]
                acqs_json: Dict[str, Any] = {}
                for acq_id in _take(sorted(acq_map.keys()), limits.acqs_per_plate):
                    wells_sorted = sorted(acq_map[acq_id]["wells"])
                    acqs_json[str(acq_id)] = {
                        "id": acq_id,
                        "date_iso": iso(acq_map[acq_id].get("date")),
                        "wells": _take(wells_sorted, limits.wells_per_acq),
                    }
                plates_json[barcode] = {"id": barcode, "acquisitions": acqs_json}
            projects_json[project] = {
                "id": project,
                "date_iso": iso(project_latest.get(project)),
                "plates": plates_json,
            }

        retval = {
            "data": {"projects": projects_json},
            "meta": {
                "query": term,
                "limits": {
                    "raw_limit": limits.raw_limit,
                    "plates": limits.plates,
                    "acqs_per_plate": limits.acqs_per_plate,
                    "wells_per_acq": limits.wells_per_acq,
                },
                "counts": {
                    "rows_scanned": len(rows),
                    "projects": len(uniq_projects),
                    "plates": len(uniq_plates),
                    "acquisitions": len(uniq_acqs),
                    "wells": len(uniq_wells),
                },
            },
        }
        return retval
    
    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Failed to search compounds.")
        return {"status": "error", "message": str(err)}

    finally:
        if cursor: cursor.close()
        put_connection(conn)
