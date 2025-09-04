#!/usr/bin/env python3
import logging
import json
import psycopg2
import psycopg2.pool
import psycopg2.extras
import settings as imgdb_settings
import platemodel
from collections import defaultdict

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

        # add layout to plate
        plate = plates_dict[plate_name]
        plate.add_layout(layout_dict)

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


def search_compounds(term: str, limit: int = 100):
    """
    Free‐text search across batchid, cbkid, libid, libtxt, smiles, inchi, inkey, name
    in the plate_v1 view, joined to plate_acquisition for context.
    Returns at most `limit` wells (rows) in total.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        like = f"%{term}%"
        query = (
            "SELECT "
            "  pa.id AS plate_acquisition_id, "
            "  pa.name AS plate_acquisition_name, "
            "  pa.plate_barcode AS barcode, "
            "  pv.well_id, "
            "  pv.batchid, pv.cbkid, pv.libid, pv.libtxt, "
            "  pv.smiles, pv.inchi, pv.inkey, pv.compound_name "
            "FROM plate_v1 pv "
            "JOIN plate_acquisition pa ON pv.barcode = pa.plate_barcode "
            "WHERE "
            "  pv.batchid::text   ILIKE %(like)s OR "
            "  pv.cbkid            ILIKE %(like)s OR "
            "  pv.libid            ILIKE %(like)s OR "
            "  pv.libtxt           ILIKE %(like)s OR "
            "  pv.smiles           ILIKE %(like)s OR "
            "  pv.inchi            ILIKE %(like)s OR "
            "  pv.inkey            ILIKE %(like)s OR "
            "  pv.compound_name    ILIKE %(like)s "
            "ORDER BY pa.id, pv.well_id "
            "LIMIT %(limit)s"
        )
        cursor.execute(query, {"like": like, "limit": limit})
        return cursor.fetchall()
    finally:
        cursor.close()
        put_connection(conn)