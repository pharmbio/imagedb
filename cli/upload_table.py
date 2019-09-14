#!/usr/bin/env python3

import logging
import os
import re
import time
import traceback
import glob
import csv
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
import settings as imgdb_settings

__connection_pool = None

def get_connection():

    global __connection_pool
    if __connection_pool is None:
        __connection_pool = psycopg2.pool.SimpleConnectionPool(1, 2, user = imgdb_settings.DB_USER,
                                              password = imgdb_settings.DB_PASS,
                                              host = imgdb_settings.DB_HOSTNAME,
                                              port = imgdb_settings.DB_PORT,
                                              database = imgdb_settings.DB_NAME)

    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)

def insert_csv_old(tablename, filename):
    sql = """
        INSERT INTO test (a, b, c, d)
        VALUES %s
        """


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
    insert_csv("channel_map", "channel_map.tsv")

except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")
    print("This is error message: " + str(e))