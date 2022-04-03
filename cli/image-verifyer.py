#!/usr/bin/env python3

import logging
import argparse
import os
from pathlib import Path
import re
import time
import traceback
import glob
from unittest import result
import psycopg2
import psycopg2.extras
from psycopg2 import pool
import json
from datetime import datetime, timedelta

from filenames.filenames import parse_path_and_file
from image_tools import makeThumb
from image_tools import read_tiff_info
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

def get_modtime(file):
    # get last modified date of this file
    modtime = os.path.getmtime(file)
    return modtime

def delete_image_from_db(path, dry_run=False):
    logging.debug("Inside delete_image_from_db, path: " + str(path))

    conn = None
    
    try:
        
        # Build query
        query = ("DELETE FROM images WHERE path = %s")
        logging.debug("query" + str(query))

        if dry_run:
            logging.info("dry_run=True, return here")
            return

        conn = get_connection()
        cursor = conn.cursor()
        retval = cursor.execute(query, (path,))
        conn.commit()
        cursor.close()

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        if conn is not None:
            put_connection(conn)

def select_image_path(plate_acquisition_id, well, site, channel):

    #logging.debug("Inside select_image_path(plate_acquisition_id, well, site, channel)" + str(channel))

    conn = None
    
    try:
        
        query = ("SELECT path, well "
                        "FROM images "
                        "WHERE plate_acquisition_id = %s "
                        "AND well = %s "
                        "AND site = %s "
                        "AND channel = %s")

        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, (plate_acquisition_id,
                               well,
                               site,
                               channel)
                        )
        paths = cursor.fetchall()
        cursor.close()

        return paths

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def get_duplicate_channel_images():

    logging.info("Inside get_duplicate_channel_images()")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        dupe_query = ("SELECT plate_acquisition_id, plate_barcode, well, site, channel, count(*) as dupecount"
                      " FROM images"
                      " GROUP BY plate_acquisition_id, plate_barcode, well, site, channel HAVING count(*)> 1")
        cursor.execute(dupe_query)
        dupes = cursor.fetchall()
        cursor.close()

        return dupes

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def deal_with_orfans():
    orfans = find_orfan_images()

    # Save orfan images as textfile
    with open('orfans.txt', 'w+') as orfan_file:   
        for line in orfans:
            orfan_file.write('%s\n' %line)

    # delete orfan image-entries from database:
    for orfan_path in orfans:
        delete_image_from_db(orfan_path, dry_run=False)

def deal_with_dupes():
    dupes = get_duplicate_channel_images()
    for dupe in dupes:
        #logging.debug(dupe)

        paths = select_image_path(
                                     dupe['plate_acquisition_id'],
                                     dupe['well'],
                                     dupe['site'],
                                     dupe['channel'])

        # only deal with first two, if there are more, just run everything again
        path_0 = paths[0]['path']
        modtime_path_0 = get_modtime(path_0)

        path_1 = paths[1]['path']
        modtime_path_1 = get_modtime(path_1)

        # Leave file with longest time (since 1970-01-01)
        if modtime_path_0 > modtime_path_1:
            logging.info("Leavin image path_0, modtime: " + str(modtime_path_0) + ", path: " + str(path_0))
            logging.info("Delete image path_1, modtime: " + str(modtime_path_1) + ", path: " + str(path_1))
        else:           
            logging.info("Leavin image path_1, modtime: " + str(modtime_path_1) + ", path: " + str(path_1))
            logging.info("Delete image path_0, modtime: " + str(modtime_path_0) + ", path: " + str(path_0))
            
            


def find_orfan_images():

    logging.info("Inside find_orfan_images()")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = ("SELECT path"
                      " FROM images"
                      " ORDER BY plate_acquisition_id")
        cursor.execute(query)

        orfans = list()
        counter = 0
        for row in cursor:
            path = row['path']
            
            if counter % 10000 == 0:
                logging.debug("files verified counter: " + str(counter))

            if not os.path.exists(path):
                logging.debug(path)
                orfans.append(path)

            counter += 1

        return orfans


    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def add_more_plate_acq():

    logging.info("Inside add_more_plate_acq()")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = ("SELECT plate_barcode, timepoint, imaged, folder"
                      " FROM images")
        cursor.execute(query)

        counter = 0
        for row in cursor:
            
            plate_barcode = row['plate_barcode']
            timepoint = row['timepoint']
            imaged_timepoint = row['imaged']
            folder = row['folder']

            if counter % 10000 == 0:
                logging.debug("files verified counter: " + str(counter))

            select_or_insert_plate_acq(plate_barcode, 'ImageXpress', timepoint, imaged_timepoint, folder)

            counter += 1


    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def select_or_insert_plate_acq(plate_barcode, microscope, timepoint, imaged_timepoint, folder):

    # First select to see if plate_acq already exists
    plate_acq_id = select_plate_acq_id(plate_barcode, timepoint, folder)

    if plate_acq_id is None:
        plate_acq_id = insert_plate_acq(plate_barcode, microscope, timepoint, imaged_timepoint, folder)
    
    return plate_acq_id

def select_channel_map_id(plate_barcode, timepoint):

    conn = None
    
    try:
        
        query = ("SELECT channel_map_id "
                "FROM plate_acquisition "
                "WHERE plate_barcode = %s "
                "AND timepoint = %s ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (plate_barcode,
                               timepoint
                              ))
        channel_map_id = cursor.fetchone()
        cursor.close()
        
        return channel_map_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def select_plate_acq_id(plate_barcode, timepoint, folder):

    conn = None
    
    try:
        
        query = ("SELECT id "
                        "FROM plate_acquisition "
                        "WHERE plate_barcode = %s "
                        "AND timepoint = %s "
                        "AND folder = %s ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (plate_barcode,
                               timepoint,
                               folder
                              ))
        plate_acq_id = cursor.fetchone()
        cursor.close()
        
        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)
        
def select_finished_plate_acq_folder():

    conn = None
    
    try:
        
        query = ("SELECT folder "
                 "FROM plate_acquisition "
                 "WHERE finished IS NOT NULL")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # get result as list instead of tuples
        result = [r[0] for r in cursor.fetchall()]
        
        cursor.close()
        
        return result

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def insert_plate_acq(plate_barcode, microscope, timepoint, imaged_timepoint, folder):

    conn = None
    try:

        channel_map_id = select_channel_map_id(plate_barcode, timepoint)

        
        query = "INSERT INTO plate_acquisition(plate_barcode, imaged, microscope, channel_map_id, timepoint, folder) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"
        conn = get_connection()

        logging.info("query: " + query)
        logging.info("folder: " + str(folder))

        cursor = conn.cursor()
        cursor.execute(query, (plate_barcode,
                               imaged_timepoint,
                               microscope,
                               channel_map_id,
                               timepoint,
                               folder
                               ))

        plate_acq_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()

        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)
        

def find_dirs_containing_img_files_recursive(path):
    """Yield lowest level directories containing image files as Path (not starting with '.')
       the method is called recursively to find all subdirs """
    for entry in os.scandir(path):
        # recurse directories
        if not entry.name.startswith('.') and entry.is_dir():
            yield from find_dirs_containing_img_files_recursive(entry.path)
        if entry.is_file():
            # return parent path if file is imagefile, then break scandir-loop
            if entry.path.lower().endswith(('.png','.tif','tiff')):
                yield(Path(entry.path).parent)
                break
            



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

    parser = argparse.ArgumentParser(description='Description of your program')

    parser.add_argument('-targ', '--testarg', help='Description for xxx argument',
                        default='default-value')

    args = parser.parse_args()

    logging.debug("all args" + str(args))
    logging.debug("args.testarg" + str(args.testarg))

    start = time.time()

    # deal_with_orfans()
    # deal_with_dupes()

    #update_plate_acq()
    # add_more_plate_acq()
    
    # get all image dirs within root dirs 
    img_dirs = set(find_dirs_containing_img_files_recursive("/share/mikro/IMX/MDC_pharmbio/"))
    
    # remove finished acquisitions
    finished_acq_folders = select_finished_plate_acq_folder()
    for path in set(img_dirs):
        if str(path) in finished_acq_folders:
            img_dirs.remove(path)
            print("removed: " + str(path))
            
    # remove old dirs
    cutoff_time = time.time() - 3600 * 48 
    for path in set(img_dirs):
        if path.stat().st_mtime < cutoff_time:
            img_dirs.remove(path)
            print("removed: " + str(path))
    
    # remove blacklisted (Directories with unparsable images that were found since start of program)

    print(img_dirs)
    
    files = os.listdir('/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015239-A549-48h-P2-L4/2022-01-28/903')
    print(len(files))
    
    print("elapsed: " + str(time.time() - start))
    
    
    


except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")
