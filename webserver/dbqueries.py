#!/usr/bin/env python3
import logging
import json
import psycopg2
from psycopg2 import pool
import settings as imgdb_settings
import platemodel

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


def get_plate(plate_name):
    logging.info("inside get_plate, plate_name:" + plate_name)

    conn = None
    try:

        conn = get_connection()

        return_cols = ['plate_barcode',
                       'project',
                       'plate_acquisition_id',
                       'timepoint',
                       'path',
                       'well',
                       'site',
                       'channel',
                       'cell_line'
                       ]

        query = ("SELECT " + ",".join(return_cols) +
                 " FROM images_minimal_view"
                 " WHERE plate_barcode = %s"
                 " ORDER BY well, site, channel")

        logging.debug("query" + query)

        cursor = conn.cursor()
        cursor.execute(query, (plate_name, ))

        # create a list with all results as key-values
        resultlist = [dict(zip([key[0] for key in cursor.description], row)) for row in cursor]

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        logging.debug(str(resultlist))

        # create a nested json object of all images.
        # A plate object containing all plate_acquisitions. The plate_acquisitions containing all wells and then
        # all sites, and then channels with the image path
        plates_dict = {}
        for image in resultlist:
            plate_id = image['plate_barcode']
            # get or create a new object with this key
            plate = plates_dict.setdefault(plate_id, platemodel.Plate(plate_id))
            plate.add_data(image)

        result_dict = {"plates": plates_dict}

        return result_dict

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            conn.close()
            put_connection(conn)


def list_all_plates():

    logging.info("inside list_all_plates")

    conn = None
    try:

        conn = get_connection()

        query = ("SELECT DISTINCT plate_barcode, project "
                 " FROM images "
                 " ORDER BY project, plate_barcode")

        logging.debug("query" + str(query))

        cursor = conn.cursor()
        cursor.execute(query)

        resultlist = []

        for row in cursor:
            resultlist.append({'plate': row[0],
                               'project': row[1]
                               })

        # Close/Release connection
        cursor.close()
        put_connection(conn)
        conn = None

        logging.debug(json.dumps(resultlist, indent=2))

        return resultlist

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            conn.close()
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
            conn.close()
            put_connection(conn)