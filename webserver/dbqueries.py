#!/usr/bin/env python3
import logging
import json
import psycopg2
import psycopg2.pool
import psycopg2.extras
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

        # create a dict with well_id as key to metadata
        layout_dict = {}
        for row in rows:
            well_id = row['well_id']
            layout_dict[well_id] = row

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


def list_all_plates():

    logging.info("inside list_all_plates")

    conn = None
    try:

        conn = get_connection()

        query = ("SELECT DISTINCT name, plate_barcode, project, id, hidden "
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