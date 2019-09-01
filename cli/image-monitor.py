#!/usr/bin/env python3

import logging
import argparse
import os
import re
import time
import traceback
import glob
import pymongo
import psycopg2
from psycopg2 import pool
import json
from datetime import datetime, timedelta

from filenames.filenames import parse_path_and_file
from image_tools import makeThumb
from image_tools import read_tiff_info
import settings as imgdb_settings

#
# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
# path example
# 'ACHN-20X-P009060/2019-02-19/and-more/not/needed/'
# or
# '181212-U2OS-20X-BpA-HD-DB-high_E02_s7_w3_thumbCFB5B241-4E5B-4AB4-8861-A9B6E8F9FE00.tif
#
__pattern_path_plate_date = re.compile('^'
                                       + '.*'         # any
                                       + '/([0-9]{6}-)?' # maybe date here also (1)
                                       + '([^-/]+)'  # project-name (2)
                                       + '-([^-/]+)'  # magnification (3)
                                       + '-([^/]+)'   # plate (4)
                                       + '/([0-9]{4})-([0-9]{2})-([0-9]{2})' # date (yyyy, mm, dd) (5,6,7)
                                       ,
                                       re.IGNORECASE)  # Windows has case-insensitive filenames

__connection_pool = None


def parse_path_plate_date(path):
    match = re.search(__pattern_path_plate_date, path)

    if match is None:
        return None

    group_ = {
        'project': match.group(2),
        'magnification': match.group(3),
        'plate': match.group(4),
        'date_year': int(match.group(5)),
        'date_month': int(match.group(6)),
        'date_day_of_month': int(match.group(7)),
    }
    metadata = group_

    return metadata


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


#
# Returns list of (level 1) subdirs to specified dir
#
def get_subdirs(root_path, filter=""):
    subdirs = []
    for name in os.listdir(root_path):
        if filter in name:
            if os.path.isdir(os.path.join(root_path, name)):
                subdirs.append(os.path.join(root_path, name))
    return subdirs

#
# Recursively gets all files in subdirs
#
def get_all_image_files(path):
    # get all files
    logging.debug(path)

    # For now return all tiff-files
    all_files = glob.glob(os.path.join(path, '**/*.tif'), recursive=True)
    # all_files.extend( glob.glob(os.path.join(path, '**/*.png'), recursive=True))

    logging.debug(all_files)

    return all_files

def image_name_sort_fn(filename):
    metadata = parse_path_and_file(filename)
    return metadata['path']


def make_thumb_path(image, thumbdir, image_root_dir):
    subpath = str(image).replace(image_root_dir, "")
    # Need to strip / otherwise can not join as subpath
    subpath = subpath.strip("/")
    thumb_path = os.path.join(thumbdir, subpath)
    return thumb_path


def insert_meta_into_db(img_meta):

    insert_query = "INSERT INTO images(project, plate, timepoint, well, site, channel, path, metadata) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    insert_conn = get_connection()
    insert_cursor = insert_conn.cursor()
    insert_cursor.execute(insert_query, (img_meta['project'],
                                         img_meta['plate'],
                                         img_meta['timepoint'],
                                         img_meta['well'],
                                         img_meta['wellsample'],
                                         img_meta['channel'],
                                         img_meta['path'],
                                         json.dumps(img_meta)
                                         ))
    insert_cursor.close()
    insert_conn.commit()
    put_connection(insert_conn)

def image_exists_in_db(image_path):

    select_conn = get_connection()
    select_cursor = select_conn.cursor()

    select_path_query = "SELECT * FROM images WHERE path = %s"
    select_cursor.execute(select_path_query, (image_path,))

    rowcount = select_cursor.rowcount
    select_cursor.close()
    put_connection(select_conn)

    return rowcount > 0

def add_plate_to_db(images, latest_filedate_to_test):
    logging.info("start add_plate_metadata to db")

    current_latest_imagefile = 0

    # sort images (just to get thumb after image)
    images.sort(key=image_name_sort_fn)

    # Loop all Images
    for idx, image in enumerate(images):

        img_meta = parse_path_and_file(image)

        logging.debug(img_meta)

        # get last modified date of this image-file
        image_modtime = os.path.getmtime(image)

        # Keep track of latest processed file
        current_latest_imagefile = max(current_latest_imagefile, image_modtime)

        # Only check newer files if image is in db already
        if image_modtime > latest_filedate_to_test:

            # Skip thumbnails
            if not img_meta['is_thumbnail']:

                # Check if image already exists in db
                image_exists = image_exists_in_db(img_meta['path'])

                # Insert image if not in db (no result)
                if image_exists == False:

                    # read tiff-meta-tags
                    tiff_meta = read_tiff_info(img_meta['path'])
                    img_meta['tiff_meta'] = tiff_meta

                    # insert into db
                    insert_meta_into_db(img_meta)

                    # create thumb image
                    thumb_path = make_thumb_path(image,
                                                 imgdb_settings.IMAGES_THUMB_FOLDER,
                                                 imgdb_settings.IMAGES_ROOT_FOLDER)
                    logging.debug(thumb_path)

                    # Only create thumb if not exists already
                    if not os.path.exists(thumb_path):
                      makeThumb(image, thumb_path, False)

                else:
                    logging.debug("doc exists already")

            if idx % 100 == 0:
                logging.info("images processed:" + str(idx))
        else:
            logging.debug("file is to old for being inserted into database, image_modtime < latest_filedate_to_test")

    return current_latest_imagefile


#
# Main import function
#
def import_plate_images_and_meta(plate_date_dir, latest_import_filedate):
    logging.info("start import_plate_images_and_meta: " + str(plate_date_dir))
    all_images = get_all_image_files(plate_date_dir)

    logging.debug(all_images)

    # import images (if later than latest_import_filedate)
    current_latest_imported_file = add_plate_to_db(all_images, latest_import_filedate)

    logging.info("done import_plate_images_and_meta: " + str(plate_date_dir))

    return current_latest_imported_file

def polling_loop(poll_dirs_margin_days, latest_file_change_margin, sleep_time, proj_root_dirs, exhaustive_initial_poll, continuous_polling):

    logging.info("Inside polling loop")

    is_initial_poll = True
    latest_filedate_last_poll = 0

    logging.info("exhaustive_initial_poll=" + str(exhaustive_initial_poll))

    while True:

        start_time = time.time()
        logging.info("Staring new poll")
        logging.info("latest_filedate_last_poll=" + str(datetime.fromtimestamp(latest_filedate_last_poll)))

        plate_filter = ""

        current_poll_latest_filedate = 0
        for proj_root_dir in proj_root_dirs:
            # Get all subdirs (these are the top plate dir)
            image_dir = os.path.join(imgdb_settings.IMAGES_ROOT_FOLDER, proj_root_dir)
            plate_dirs = get_subdirs(image_dir)
            logging.debug("plate_dirs" + str(plate_dirs))

            for plate_dir in plate_dirs:
                plate_subdirs = get_subdirs(plate_dir)

                try:
                    for plate_date_dir in plate_subdirs:
                        logging.debug("plate_subdir: " + str(plate_date_dir))

                        # Parse filename for metadata (e.g. platename well, site, channet etc.)
                        metadata = parse_path_plate_date(plate_date_dir)
                        logging.debug("metadata" + str(metadata))

                        # get date from dir
                        dir_date = datetime(metadata['date_year'], metadata['date_month'],
                                            metadata['date_day_of_month'])

                        date_delta = datetime.today() - dir_date

                        logging.debug("delta" + str(date_delta))
                        logging.debug(str(is_initial_poll))
                        logging.debug(str(exhaustive_initial_poll))

                        # poll images in directories more recent than today + poll_dirs_date_margin_days
                        if date_delta <= timedelta(days=poll_dirs_margin_days) or \
                                (exhaustive_initial_poll and is_initial_poll):

                            logging.debug("Image folder is more recent")

                            # set file date to test inserting into db to last poll latest file minus margin
                            latest_filedate_last_poll_with_margin = latest_filedate_last_poll - latest_file_change_margin;

                            # try to import files more recent than latest_filedate last poll minus margin
                            # returns max of latest filedate in dir and the latest file to check
                            current_dir_latest_filedate = import_plate_images_and_meta(plate_date_dir,
                                                                                       latest_filedate_last_poll_with_margin)

                            # keep track of latest file in this current poll
                            current_poll_latest_filedate = max(current_poll_latest_filedate,
                                                               current_dir_latest_filedate)

                            # only update with latest file when everything is checked once

                except Exception as e:
                    logging.exception("Exception in plate dir")
                    exception_file = os.path.join(imgdb_settings.ERROR_LOG_DIR, "exceptions.log")
                    with open(exception_file, 'a') as exc_file:
                       exc_file.write("plate_date_dir:" + str(plate_date_dir))
                       exc_file.write(traceback.format_exc())

        # Set latest file mod for all monitored dirs
        latest_filedate_last_poll = max(latest_filedate_last_poll, current_poll_latest_filedate)

        elapsed_time = time.time() - start_time
        logging.info("Time spent polling: " + str(elapsed_time))

        is_initial_poll = False

        # Sleep until next polling action
        logging.info("Going to sleep for: " + str(sleep_time) + "sek" )
        time.sleep(sleep_time)

        # TODO could skip sleeping if images were inserted... but difficult then with 2 hour margin (all files would be tried again)

        if continuous_polling != True:
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
                        level=logging.INFO)

    rootLogger = logging.getLogger()

    parser = argparse.ArgumentParser(description='Description of your program')

    parser.add_argument('-prd', '--proj-root-dirs', help='Description for xxx argument',
                        default=imgdb_settings.PROJ_ROOT_DIRS)
    parser.add_argument('-cp', '--continuous-polling', help='Description for xxx argument',
                        default=imgdb_settings.CONTINUOUS_POLLING)
    parser.add_argument('-pi', '--poll-interval', help='Description for xxx argument',
                        default=imgdb_settings.POLL_INTERVAL)
    parser.add_argument('-pdmd', '--poll-dirs-margin-days', help='Description for xxx argument',
                        default=imgdb_settings.POLL_DIRS_MARGIN_DAYS)
    parser.add_argument('-eip', '--exhaustive-initial-poll', help='Description for xxx argument',
                        default=imgdb_settings.EXHAUSTIVE_INITIAL_POLL)
    parser.add_argument('-lfcm', '--latest-file-change-margin', help='Description for xxx argument',
                        default=imgdb_settings.LATEST_FILE_CHANGE_MARGIN)

    args = parser.parse_args()

    logging.debug(args)

    polling_loop(args.poll_dirs_margin_days,
                 args.latest_file_change_margin,
                 args.poll_interval,
                 args.proj_root_dirs,
                 args.exhaustive_initial_poll,
                 args.continuous_polling)

except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")
