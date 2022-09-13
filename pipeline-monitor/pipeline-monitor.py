#!/usr/bin/env python3

import logging
import os
from pathlib import Path
import time
import traceback
from typing import Dict, List
import psycopg2
from psycopg2 import pool, extras, extensions
import json
from datetime import datetime

import settings as imgdb_settings

__connection_pool = None


def get_connection():

    global __connection_pool
    if __connection_pool is None:
        __connection_pool = psycopg2.pool.SimpleConnectionPool(1, 2, user=imgdb_settings.DB_USER,
                                                               password=imgdb_settings.DB_PASS,
                                                               host=imgdb_settings.DB_HOSTNAME,
                                                               port=imgdb_settings.DB_PORT,
                                                               database=imgdb_settings.DB_NAME)
    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)





def get_celline_from_text(text):

    cell_lines = ["U2OS", "A549", "MCF7", "HOG", "VERO E6", "VERO", "RD", "RD18", "RH30"]
    for cell_line in cell_lines:
        if "-" + cell_line + "-" in text:
            return cell_line

    return ""

def select_image_analyses_automation_unsubmitted():

    try:

        conn = get_connection()

        query = """
                SELECT *
                FROM plate_acquisition
                WHERE finished IS NOT NULL
                AND id NOT IN (
                                SELECT plate_acq_id
                                FROM image_analyses_automation_submitted
                            )
                """

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        put_connection(conn)
        conn = None

        return results

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def select_image_analyses_automation_from_params(project, cell_line, channel_map):

    try:

        conn = get_connection()

        query = """
                SELECT *
                FROM image_analyses_automation
                WHERE (cell_line = %s OR cell_line = '*')
                AND (channel_map = %s OR channel_map = -1)
                AND (project = %s)
                """

        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute(query, (cell_line, channel_map, project))
        results = cursor.fetchall()
        cursor.close()

        put_connection(conn)
        conn = None

        return results

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def add_plate_acq_id_to_image_analyses_automation_submitted(plate_acq_id):

    logging.debug("inside add_plate_acq_id_to_image_analyses_automation_submitted")

    conn = None
    try:

        conn = get_connection()
        timestamp = time.time()

        # Build query
        query = ("INSERT INTO image_analyses_automation_submitted(plate_acq_id, time)"
                 "VALUES (%s, %s)")

        logging.info("query" + str(query))

        cursor = conn.cursor()

        cursor.execute(query, [plate_acq_id, datetime.utcfromtimestamp(timestamp)])

        cursor.close()

        conn.commit()

        put_connection(conn)
        conn = None

        return "OK"

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def submit_analysis(plate_acquisition, analysis_pipeline_name):
    '''This method is copied from pipelinegui/webserver/dbqueries.py and in future code should be common and shared'''

    logging.debug("submit_analysis")

    conn = None
    try:

        conn = get_connection()

        select_query = ("SELECT name, meta FROM analysis_pipelines WHERE name=%s")
        logging.info("select_query" + str(select_query))
        cursor = conn.cursor()
        cursor.execute(select_query, (analysis_pipeline_name,))
        first_row = cursor.fetchone()
        pipeline_name = first_row[0]
        meta = first_row[1]
        cursor.close()

        # get the sub-analysis and analysis_meta part of pipeline-meta
        sub_analyses = meta["sub_analyses"]
        analysis_meta = meta["analysis_meta"]
        analysis_meta['submitted_by'] = 'pipeline_automation'

        # Build query
        query = ("INSERT INTO image_analyses(plate_acquisition_id, pipeline_name, meta) "
                 "VALUES (%s, %s, %s) RETURNING id")

        logging.info("query" + str(query))

        cursor = conn.cursor()

        logging.debug(cursor.mogrify(query, [plate_acquisition, pipeline_name, json.dumps(analysis_meta)]))

        cursor.execute(query, [plate_acquisition, pipeline_name, json.dumps(analysis_meta)])
        analysis_id = cursor.fetchone()[0]
        cursor.close()

        depends_on_id = []
        for sub_analysis in sub_analyses:
            insert_sub_cursor = conn.cursor() # piro says https://stackoverflow.com/users/10138/piro
            insert_sub_query = ("INSERT INTO image_sub_analyses(analysis_id, plate_acquisition_id, meta, depends_on_sub_id) "
                                "VALUES (%s,%s,%s,%s) RETURNING sub_id")
            insert_sub_cursor.execute(insert_sub_query, (analysis_id, plate_acquisition, json.dumps(sub_analysis),json.dumps(depends_on_id),))
            returned_sub_id = insert_sub_cursor.fetchone()[0]

        conn.commit()

        put_connection(conn)
        conn = None

        return "OK"

    except (Exception, psycopg2.DatabaseError) as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)


def polling_loop():

    logging.info("starting polling_loop: ")

    sleep_time = 10

    while True:

        logging.info("***")
        logging.info("")
        logging.info("Staring new imagedb poll for finished plates: " + str(datetime.today()))
        logging.info("")
        logging.info("***")
        logging.info("")

        start_loop = time.time()

        results = select_image_analyses_automation_unsubmitted()

        logging.debug(f"len(results) {len(results)}")
        logging.debug(f"results {results}")

        # Loop through all new plate-acquisitions
        for row in results:

            plate_acq_id = row['id']
            project = row['project']
            name = row['name']
            cell_line = get_celline_from_text(name)
            channel_map_id = row['channel_map_id']

            logging.debug(f"cell_line: {cell_line}")
            logging.debug(f"project: {project}")

            analyses = select_image_analyses_automation_from_params(project, cell_line, channel_map_id)
            # Loop through all analyses to be submitted for current plate-acq-id
            for analysis in analyses:

                logging.debug(f"going to submit this analysis: {analysis}")

                pipeline_name = analysis['pipeline_name']

                submit_analysis(plate_acq_id, pipeline_name)

            # mark this plate_acq_id done
            add_plate_acq_id_to_image_analyses_automation_submitted(plate_acq_id)


        logging.info(f"elapsed: {time.time() - start_loop}")

        # Sleep until next polling action
        is_initial_poll = False
        logging.info(f"Going to sleep for: {sleep_time} sek")
        logging.info("")
        time.sleep(sleep_time)

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

    polling_loop()

except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")
