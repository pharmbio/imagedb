#!/usr/bin/env python3

import logging
import os
import re
import time
import traceback
import glob
import pymongo
from datetime import datetime, timedelta

from filenames.filenames import parse_path_and_file
from image_tools import makeThumb
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

def add_plate_to_db(images, latest_filedate_to_test):
    logging.info("start add_plate_metadata to db")

    current_latest_imagefile = 0

    # Connect db
    dbclient = pymongo.MongoClient( username=imgdb_settings.DB_USER,
                                    password=imgdb_settings.DB_PASS,
                                    # connectTimeoutMS=500,
                                    serverSelectionTimeoutMS=1000,
                                    host=imgdb_settings.DB_HOSTNAME
                                    )
    img_db = dbclient["pharmbio_db"]
    img_collection = img_db["pharmbio_microimages"]

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

                # Check if doc already exists in db
                result = img_collection.find({'path': img_meta['path']})
                # Insert image if not in db (no result)
                if result.count() == 0:

                    # create document to be inserted
                    document = { 'project': img_meta['project'],
                                 'plate': img_meta['plate'],
                                 'timepoint': img_meta['timepoint'],
                                 'path': img_meta['path'],
                                 'metadata': img_meta }

                    insert_result = img_collection.insert_one(document)

                    # create thumb image
                    thumb_path = make_thumb_path(image,
                                                 imgdb_settings.IMAGES_THUMB_FOLDER,
                                                 imgdb_settings.IMAGES_ROOT_FOLDER)
                    logging.debug(thumb_path)
                    makeThumb(image, thumb_path, False)

                else:
                    logging.debug("doc exists already")

            if idx % 100 == 0:
                logging.info("images processed:" + str(idx))
        else:
            logging.debug("file is to old for being inserted into database, image_modtime < latest_filedate_to_test")

    return current_latest_imagefile

def plateExists(name):
    return False


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

def polling_loop(poll_dirs_margin_days, latest_file_poll_margin_db_insert_sek, sleep_time, proj_root_dirs, exhaustive_initial_poll):

    logging.info("Inside polling loop")

    is_initial_poll = True
    latest_filedate_last_poll = 0

    logging.info("exhaustive_initial_poll=" + str(exhaustive_initial_poll))

    while(True):

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

                    # poll images in directories more recent than today + poll_dirs_date_margin_days
                    if date_delta <= timedelta(days=poll_dirs_margin_days) or \
                            (exhaustive_initial_poll and is_initial_poll):

                        # set file date to test inserting into db to last poll latest file minus margin
                        latest_filedate_last_poll_with_margin = latest_filedate_last_poll - latest_file_poll_margin_db_insert_sek;

                        # try to import files more recent than latest_filedate last poll minus margin
                        # returns max of latest filedate in dir and the latest file to check
                        current_dir_latest_filedate = import_plate_images_and_meta(plate_date_dir,
                                                                                   latest_filedate_last_poll_with_margin)

                        # keep track of latest file in this current poll
                        current_poll_latest_filedate = max(current_poll_latest_filedate,
                                                           current_dir_latest_filedate)

                        # only update with latest file when everything is checked once

        # Set latest file mod for all monitored dirs
        latest_filedate_last_poll = max(latest_filedate_last_poll, current_poll_latest_filedate)

        elapsed_time = time.time() - start_time
        logging.info("Time spent polling: " + str(elapsed_time))

        is_initial_poll = False

        # Sleep until next polling action
        logging.info("Going to sleep for: " + str(sleep_time) + "sek" )
        time.sleep(sleep_time)

        # TODO could skip sleeping if images were inserted... but difficult then with 2 hour margin (all files would be tried again)


#
#  Main entry for script
#
try:
    exhaustive_initial_poll = imgdb_settings.EXHAUSTIVE_INITIAL_POLL
    poll_dirs_margin_days = 3
    poll_sleep_time = 300 # 5 min
    latest_file_poll_margin_db_insert_sek = 7200 # 2 hour (always try insert images within this time from latest_filedate_last_poll)

    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    rootLogger = logging.getLogger()

    #
    # Set some constants, should be moved to a "config.py" or "settings.py"
    #

    # read password from environment
    # DB_USER = os.environ['DB_USER']
    proj_root_dirs = [ "Aish/",
                           "exp-CombTox/",
                           "PolinaG-ACHN",
                           "PolinaG-KO",
                           "PolinaG-MCF7",
                           "PolinaG-U2OS",
                           "exp-TimeLapse/",
                           "exp-WIDE/"
                           ]

    polling_loop(poll_dirs_margin_days,
                 latest_file_poll_margin_db_insert_sek,
                 poll_sleep_time,
                 proj_root_dirs,
                 exhaustive_initial_poll)



except Exception as e:
    print(traceback.format_exc())
    logging.info("Exception out of script")