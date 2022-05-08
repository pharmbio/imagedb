#!/usr/bin/env python3

from distutils.log import debug
import logging
import os
import re
import time
import traceback
import glob
import csv
import psycopg2
from psycopg2 import pool, extras, extensions

import settings as imgdb_settings
import json

__connection_pool = None

def get_connection() -> extensions.connection:

    global __connection_pool
    if __connection_pool is None:
        __connection_pool = pool.SimpleConnectionPool(1, 2, user = imgdb_settings.DB_USER,
                                              password = imgdb_settings.DB_PASS,
                                              host = imgdb_settings.DB_HOSTNAME,
                                              port = imgdb_settings.DB_PORT,
                                              database = imgdb_settings.DB_NAME)

    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)



def insert_csv(tablename, filename):

    conn = get_connection()
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t')

        # first line has to be columns
        columns = next(reader)
        logging.debug(columns)

        cols = ','.join(columns)

        query = 'INSERT INTO ' + tablename + ' (' + cols + ') VALUES %s'

        logging.debug(query)
        cursor = conn.cursor()
        psycopg2.extras.execute_values(cursor, query, reader)
        cursor.close()
        conn.commit()

    put_connection(conn)

def filter_list_remove_imagefiles(list):
     suffix = ('.png','.jpg','.tiff','.tif')
     return filter_list_remove_files_suffix(list, suffix)

def filter_list_remove_files_suffix(input_list, suffix):


    filtered_list = []
    was_filtered = False
    for file in input_list:
        if file.lower().endswith(suffix):
            # remove filename and add path only to filtered list
            filtered_list.append(os.path.dirname(file) + '/')
            was_filtered = True
        else:
            filtered_list.append(file)

    unique_filtered_list = list(set(filtered_list))

    if was_filtered:
        logging.debug("unique_filtered_list" + str(unique_filtered_list))

    return unique_filtered_list

def update_analysis_filelist(dry_run=True):

    try:
        conn = get_connection()

        query = 'SELECT id, result FROM image_analyses'

        logging.debug(query)
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        cursor.execute(query)

        analyses = cursor.fetchall()
        cursor.close()

        for row in analyses:
            logging.debug('id' + str(row['id']))
            result = row['result']
            if result is not None:
                #logging.debug(str(result))
                file_list = result['file_list']
                filtered_list = filter_list_remove_imagefiles(file_list)
                result['file_list'] = filtered_list

        query = f"""UPDATE image_analyses
                    SET result=%s
                    WHERE id=%s
                """

        for row in analyses:
            id = row['id']
            result = row['result']

            cursor = conn.cursor()
            cursor.execute(query, [json.dumps(result), id])
            cursor.close()


        if not dry_run:
            logging.debug("Before commit")
            conn.commit()
            logging.debug("Commited")
        else:
            logging.debug("Dry_run - no commit")

        put_connection(conn)
        conn = None

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


def update_sub_analysis_filelist(dry_run=True):

    try:
        conn = get_connection()

        query = 'SELECT sub_id, result FROM image_sub_analyses'

        logging.debug(query)
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        cursor.execute(query)

        analyses = cursor.fetchall()
        cursor.close()

        for row in analyses:
            logging.debug('id' + str(row['sub_id']))
            result = row['result']
            if result is not None:
                #logging.debug(str(result))
                file_list = result['file_list']
                filtered_list = filter_list_remove_imagefiles(file_list)
                result['file_list'] = filtered_list


        query = f"""UPDATE image_sub_analyses
                    SET result=%s
                    WHERE sub_id=%s
                """

        for row in analyses:
            id = row['sub_id']
            result = row['result']

            cursor = conn.cursor()
            cursor.execute(query, [json.dumps(result), id])
            cursor.close()


        if not dry_run:
            logging.debug("Before commit")
            conn.commit()
            logging.debug("Commited")
        else:
            logging.debug("Dry_run - no commit")

        put_connection(conn)
        conn = None

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


def update_analysis_pipelines_meta(dry_run=True):

    try:
        conn = get_connection()

        query = 'SELECT name, meta FROM analysis_pipelines'

        logging.debug(query)
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        cursor.execute(query)

        results = cursor.fetchall()
        cursor.close()

        for row in results:
            logging.debug('name' + str(row['name']))
            name = row['name']
            meta = row['meta']
            if meta is not None:

                if meta['analysis_meta']['type'] == "cp_features":
                    meta['analysis_meta']['type'] = "cp-features"
                if meta['analysis_meta']['type'] == "cp_qc":
                    meta['analysis_meta']['type'] = "cp-qc"

                logging.debug(json.dumps(meta, indent=4, sort_keys=True))

                query = f"""UPDATE analysis_pipelines
                            SET meta=%s
                            WHERE name=%s
                        """

                cursor = conn.cursor()
                cursor.execute(query, [json.dumps(meta), name])
                cursor.close()


                if not dry_run:
                    logging.debug("Before commit")
                    conn.commit()
                    logging.debug("Commited")
                else:
                    logging.debug("Dry_run - no commit")

        put_connection(conn)
        conn = None

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)





def update_barcode(dry_run=True):

    try:
        conn = get_connection()

        query = ("SELECT DISTINCT plate_barcode "
                 " FROM images "
                 " WHERE plate_barcode LIKE '%-P0%';")

        logging.debug(query)
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        cursor.execute(query)

        platenames = cursor.fetchall()
        cursor.close()

        for row in platenames:
            #logging.debug('id' + str(row['id']))

            plate_acquisition_name = row['plate_barcode']
            #logging.debug('platename: ' + str(plate_acquisition_name))

            #reg = '.*-(P015230)(-|$).*'
            reg = '.*-(P015\\d{3})(-|$).*'
            match = re.match(reg, plate_acquisition_name)
            if match:
                barcode = match.group(1)
                logging.debug("plate_acquisition_name:" + plate_acquisition_name)
                logging.debug('match:' + barcode)

                update_query = ("UPDATE images "
                               " SET plate_barcode=%s"
                               " WHERE plate_acquisition_name=%s")

                update_cursor = conn.cursor()
                update_cursor.execute(update_query, [barcode,plate_acquisition_name])
                update_cursor.close()

                update_query2 = ("UPDATE plate_acquisition "
                               " SET plate_barcode=%s"
                               " WHERE name=%s")

                update_cursor2 = conn.cursor()
                update_cursor2.execute(update_query2, [barcode,plate_acquisition_name])
                update_cursor2.close()


        if not dry_run:
            logging.debug("Before commit")
            conn.commit()
            logging.debug("Commited")
        else:
            logging.debug("Dry_run - no commit")

        put_connection(conn)
        conn = None

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def select_images_from_plate_acq(acq_id: int):

    try:

        #start = time.time()
        conn = get_connection()

        query = """
                SELECT well, site, count(path)
                FROM images_minimal_view
                WHERE plate_acquisition_id = %s
                GROUP BY well, site
                ORDER BY well, site
                HAVING count(path) = 5
                """

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        start = time.time()
        cursor.execute(query, (acq_id, ))
        results = cursor.fetchall()
        cursor.close()

        put_connection(conn)
        conn = None

        logging.info(f"elapsed: {time.time() - start}")

        return results

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def select_latest_plate_acq():

    try:

        cutoff_time = time.time() - 3600 * 240
        conn = get_connection()

        query = """
                SELECT *
                FROM plate_acquisition
                WHERE finished > %s
                """

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        start = time.time()
        cursor.execute(query, (cutoff_time, ))
        results = cursor.fetchall()
        cursor.close()

        put_connection(conn)
        conn = None

        logging.info(f"elapsed: {time.time() - start}")

        return results

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)



def select_channels(map_id: int):

    try:

        #start = time.time()
        conn = get_connection()

        query = """
                SELECT *
                FROM channel_map
                WHERE map_id = %s
                """

        cursor = conn.cursor()
        start = time.time()
        cursor.execute(query, (map_id, ))
        results = cursor.fetchall()
        cursor.close()

        put_connection(conn)
        conn = None

        logging.info(f"elapsed: {time.time() - start}")

        return results

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def get_complete_imgset_from_plate_acq(acq_id: int):
    all_img = select_images_from_plate_acq(acq_id)
    #print(all_img)
    channel_count = len(select_channels(2))
    print(channel_count)
    last_well = None
    last_site = None
    counter = 0
    # for img in all_img:
    #     well = img['well']
    #     site = img['site']
    #     if well != last_well:
    #         last_well = well
    #         last_site = site
    #         counter = 0
    #     if site != last_site:
    #         last_site = site
    #         counter = 0

    #     counter += 1
    #     print(counter)



#
#  Main entry for script
#
try:

    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    rootLogger = logging.getLogger()

    print("Hello")

    #update_barcode(dry_run=False)
    #update_sub_analysis_filelist(dry_run=True)
    #update_analysis_filelist(dry_run=True)
    #update_analysis_pipelines_meta(dry_run=True)

    #update_analysis_pipelines_meta(dry_run=False)


    #get_complete_imgset_from_plate_acq(1042)

    print(select_latest_plate_acq())

    #print (select_channels(2))

    #insert_csv("channel_map", "channel_map.tsv")

except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")
    print("This is error message: " + str(e))