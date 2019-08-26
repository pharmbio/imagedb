#!/usr/bin/env python3
import pymongo as pymongo
import logging
import json
import psycopg2
import settings as imgdb_settings

def get_default_collection():
    dbclient = pymongo.MongoClient(username=imgdb_settings.DB_USER,
                                   password=imgdb_settings.DB_PASS,
                                   # connectTimeoutMS=500,
                                   serverSelectionTimeoutMS=1000,
                                   host=imgdb_settings.DB_HOSTNAME,
                                   port=imgdb_settings.DB_PORT
                                   )

    img_db = dbclient["pharmbio_db"]
    img_collection = img_db["pharmbio_microimages"]

    return img_collection

def get_connection():
    return psycopg2.connect(host=imgdb_settings.DB_HOSTNAME,
                                 database=imgdb_settings.DB_NAME,
                                 user=imgdb_settings.DB_USER, password=imgdb_settings.DB_PASS)



def list_plate(find_plate):
    logging.debug("list_plates")

    logging.debug("find_plate" + find_plate)

    conn = None
    try:

        conn = get_connection()

        query = ("SELECT plate, timepoint, path, well, site, channel "
                 "FROM images "
                 "WHERE plate = %s "
                 "ORDER BY well, site, channel")

        logging.info("query" + query)

        cursor = conn.cursor()
        cursor.execute(query, (find_plate, ))

        resultlist = []

        for row in cursor:
            resultlist.append({'plate': row[0],
                          'timepoint': row[1],
                          'path': row[2],
                          'well': row[3],
                          'site': row[4],
                          'channel': row[5]
                          })

        # resultlist = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()

        # Before returning (to web) delete the for user hidden "root part" IMAGES_ROOT_FOLDER part, e.g. /share/mikro/IMX.....
        for image in resultlist:
            for key, value in image.items():
                if key == "path":
                    new_value = str(value).replace( imgdb_settings.IMAGES_ROOT_FOLDER , "")
                    image.update( {'path': new_value})

        plates_dict = {}
        for image in resultlist:
            plates_dict.setdefault(image['plate'], {}) \
                .setdefault(image['timepoint'], {}) \
                .setdefault(image['well'], {}) \
                .setdefault(image['site'], {}) \
                .setdefault(image['channel'], image['path'])


        #plateObj = {'plate_name:', plate,
        #            'timepoints:', platesdict['plate']
        #            }

        return {'plates': plates_dict}

    except (Exception, psycopg2.DatabaseError) as error:
        logging.exception("Message")
    finally:
        if conn is not None:
            conn.close()

def list_plates(DB_HOSTNAME="image-mongo"):

    logging.debug("list_plates")

    conn = None
    try:

        conn = get_connection()

        query = ("SELECT DISTINCT plate, project "
                 "FROM images "
                 "ORDER BY project, plate")

        logging.info("query" + str(query))

        cursor = conn.cursor()
        cursor.execute(query)

        resultlist = []

        for row in cursor:
            resultlist.append({'plate': row[0],
                               'project': row[1]
                               })

        # resultlist = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()

        logging.debug(json.dumps(resultlist, indent=2))

        return resultlist


    except (Exception, psycopg2.DatabaseError) as error:
        logging.exception("Message")
    finally:
        if conn is not None:
            conn.close()