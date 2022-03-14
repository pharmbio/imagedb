#!/usr/bin/env python3

import logging
import argparse
import os
import re
import time
import traceback
import glob
import psycopg2
from psycopg2 import pool
import json
from datetime import datetime, timedelta

from filenames.filenames import parse_path_and_file
import image_tools
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
# Recursively gets all subdirs in dir
#


def get_subdirs_recursively_no_thumb_dir(path):
    logging.debug(path)
    subdirs = []
    for root, dir, files in os.walk(path):
        for subdir in dir:
            if "thumb" not in subdir:
                subdir = os.path.join(root, subdir)
                subdirs.append(subdir)
    return subdirs


def get_all_image_files(path):
    # get all files
    logging.info(path)

    all_files = []
    for file in os.listdir(path):
        if file.lower().endswith(".tif") or file.lower().endswith(".png") or file.lower().endswith(".tiff"):
            absolute_file = os.path.join(path, file)
            all_files.append(absolute_file)

    # logging.info("found files" + str(all_files))

    return all_files


def get_last_modified(path):
    return


def make_thumb_path(image, thumbdir):
    # need to strip / otherwise path can not be joined
    image_subpath = image.strip("/")
    thumb_path = os.path.join(thumbdir, image_subpath)
    return thumb_path


def insert_meta_into_db(img_meta):

    # First select plate acquisition id, or insert it if not there
    plate_acq_id = select_or_insert_plate_acq(img_meta)
    # Insert into images table
    insert_meta_into_table_images(img_meta, plate_acq_id)


def getPlateBarcodeFromPlateAcquisitionName(acquisition_name):
    # extract barcode from plate_name
    pattern = '.*-(P015\\d{3})(-|$).*'
    match = re.search(pattern, acquisition_name)
    if match:
        barcode = match.group(1)
    else:
        barcode = acquisition_name

    return barcode


def insert_meta_into_table_images(img_meta, plate_acq_id):

    conn = None
    try:

        insert_query = "INSERT INTO images(project, plate_acquisition_id, plate_barcode, plate_acquisition_name, timepoint, well, site, channel, path, file_meta, metadata) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connection()
        insert_cursor = conn.cursor()
        insert_cursor.execute(insert_query, (img_meta['project'],
                                             plate_acq_id,
                                             getPlateBarcodeFromPlateAcquisitionName(
                                                 img_meta['plate']),
                                             img_meta['plate'],
                                             img_meta['timepoint'],
                                             img_meta['well'],
                                             img_meta['wellsample'],
                                             img_meta['channel'],
                                             img_meta['path'],
                                             json.dumps(img_meta['file_meta']),
                                             json.dumps(img_meta)
                                             ))
        insert_cursor.close()
        conn.commit()
    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def select_or_insert_plate_acq(img_meta):

    # First select to see if plate_acq already exists
    plate_acq_id = select_plate_acq_id(img_meta['path'])

    if plate_acq_id is None:
        plate_acq_id = insert_plate_acq(img_meta)

    return plate_acq_id


def select_plate_acq_id(image_path):

    conn = None

    try:

        folder = os.path.dirname(image_path)

        query = ("SELECT id "
                 "FROM plate_acquisition "
                 "WHERE folder = %s ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (folder,))
        plate_acq_id = cursor.fetchone()
        cursor.close()

        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def insert_plate_acq(img_meta):

    conn = None
    try:

        imaged_timepoint = datetime(int(img_meta['date_year']), int(
            img_meta['date_month']), int(img_meta['date_day_of_month']))
        folder = os.path.dirname(img_meta['path'])

        # Set default channel_map_id and change it to new one if after a certain date
        channel_map_id = 1
        if imaged_timepoint >= datetime(2020, 9, 1):
            channel_map_id = 2

        query = "INSERT INTO plate_acquisition(plate_barcode, name, project, imaged, microscope, channel_map_id, timepoint, folder) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (getPlateBarcodeFromPlateAcquisitionName(img_meta['plate']),
                               img_meta['plate'],
                               img_meta['project'],
                               imaged_timepoint,
                               img_meta['microscope'],
                               channel_map_id,
                               img_meta['timepoint'],
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


def image_exists_in_db(image_path, compressed_copy_path):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        exists_path_query = "SELECT EXISTS (SELECT 1 FROM images WHERE path = %s OR path = %s)"
        cursor.execute(exists_path_query, (image_path, compressed_copy_path))

        path_exists = cursor.fetchone()[0]
        cursor.close()
        return path_exists

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def make_compressed_copy_filename(img_meta, ORIG_ROOT_PATH, COMPRESSED_ROOT_PATH):
    filename, suffix = os.path.splitext(img_meta['path'])
    out_filename = img_meta['path'].replace(ORIG_ROOT_PATH, COMPRESSED_ROOT_PATH).replace(suffix, '.png')
    return out_filename

def make_compressed_copy(img_meta):
    COMPRESSION_LEVEL = 4
    if not os.path.isfile(img_meta['path_compressed_copy']):
        image_tools.any2png(img_meta['path'], img_meta['path_compressed_copy'], COMPRESSION_LEVEL)

def addImageToImagedb(img_meta, make_compressed_copy=False):
    # read tiff-meta-tags
    # make inside try-catch so a corrupted image doesn't stop it all
    tiff_meta = ""
    try:
        tiff_meta = image_tools.read_tiff_info(img_meta['path'])
    except Exception as e:
        logging.error("Exception reading tiff meta: %s", e)
        logging.error("image: " + str(img_meta['path']))
        logging.error( "Continuing since we don't want to break on a single bad image")

    img_meta['file_meta'] = tiff_meta

    if make_compressed_copy:
        make_compressed_copy(img_meta)
        img_meta['path'] = img_meta['path_compressed_copy']

    # insert into db
    insert_meta_into_db(img_meta)

    # create thumb image
    thumb_path = make_thumb_path(img_meta['path'],
                                 imgdb_settings.IMAGES_THUMB_FOLDER)
    logging.debug(thumb_path)

    # Only create thumb if not exists already
    # make inside try-catch so a corrupted image doesn't stop it all
    if not os.path.exists(thumb_path):
        try:
            image_tools.makeThumb(img_meta['path'], thumb_path, False)
        except Exception as e:
            logging.error("Exception making thumb image: %s", e)
            logging.error("image: " + str(img_meta['path']))
            logging.error("thumb_path: " + str(thumb_path))
            logging.error(
                "Continuing since we don't want to break on a single bad image")


def add_plate_to_db(images, latest_filedate_to_test):
    logging.info("start add_plate_metadata to db")
    logging.info("hello")

    current_latest_imagefile = 0

    # sort images (just to get thumb after image)
    # images.sort(key=image_name_sort_fn)

    # Loop all Images
    for idx, image in enumerate(images):

        img_meta = parse_path_and_file(image)

        logging.debug(img_meta)

        # Make compressed copy only if IMX-file
        make_compressed_copy = False
        #IMX_ORIG_ROOT = '/share/mikro/IMX/MDC_pharmbio/'
        #if img_meta['path'].startswith(IMX_ORIG_ROOT):
        #    COMPRESSED_IMG_ROOT = '/share/mikro-compressed/IMX/MDC_pharmbio/'
        #    img_meta['path_compressed_copy'] = make_compressed_copy_filename(img_meta, IMX_ORIG_ROOT, COMPRESSED_IMG_ROOT)
        #    make_compressed_copy = True

        # get last modified date of this image-file
        image_modtime = os.path.getmtime(image)

        # Keep track of latest processed file
        current_latest_imagefile = max(current_latest_imagefile, image_modtime)

        # Only check newer files if image is in db already
        if image_modtime > latest_filedate_to_test:

            # Skip thumbnails
            if not img_meta['is_thumbnail']:

                # Check if image already exists in db
                image_exists = image_exists_in_db(img_meta['path'], img_meta['path_compressed_copy'])

                # Insert image if not in db (no result)
                if image_exists == False:
                    addImageToImagedb(img_meta, make_compressed_copy)
                else:
                    logging.debug("image exists already in db")

            if idx % 100 == 0:
                logging.info("images processed:" + str(idx))
                logging.info("images total to process:" + str(len(images)))
        else:
            logging.debug(
                "file is to old for being inserted into database, image_modtime < latest_filedate_to_test")

    logging.info("done add_plate_metadata to db")
    return current_latest_imagefile


#
# Main import function
#
def import_plate_images_and_meta(plate_date_dir, latest_import_filedate):
    logging.info("start import_plate_images_and_meta: " + str(plate_date_dir))
    all_images = get_all_image_files(plate_date_dir)

    logging.debug(all_images)

    # import images (if later than latest_import_filedate)
    current_latest_imported_file = add_plate_to_db(
        all_images, latest_import_filedate)

    logging.info("done import_plate_images_and_meta: " + str(plate_date_dir))

    return current_latest_imported_file


def polling_loop(poll_dirs_margin_days, latest_file_change_margin, sleep_time, proj_root_dirs, exhaustive_initial_poll, continuous_polling):

    logging.info("Inside polling loop")

    is_initial_poll = True
    latest_filedate_last_poll = 0

    logging.info("exhaustive_initial_poll=" + str(exhaustive_initial_poll))

    if(exhaustive_initial_poll):
        exception_file_name = "exceptions-exhaustive_initial_poll.log"
    else:
        exception_file_name = "exceptions-last-limited_poll.log"

    exception_file = os.path.join(
        imgdb_settings.ERROR_LOG_DIR, exception_file_name)

    while True:

        start_time = time.time()
        logging.info("Staring new poll: " + str(datetime.today()))
        logging.info("latest_filedate_last_poll=" +
                     str(datetime.fromtimestamp(latest_filedate_last_poll)))

        # TODO maybe reimplement plate_filter
        # plate_filter = ""

        current_poll_latest_filedate = 0
        for proj_root_dir in proj_root_dirs:

            # Get all subdirs (these are the top plate dir)
            logging.info("proj_root_dir" + str(proj_root_dir))
            subdirs = get_subdirs_recursively_no_thumb_dir(proj_root_dir)

            # pretend every subdir is a plate dir
            for plate_dir in subdirs:

                try:

                    logging.info("plate_dir: " + str(plate_dir))

                    # get date from dir
                    dir_last_modified = os.path.getmtime(plate_dir)
                    logging.debug("dir_last_modified" + str(
                                  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dir_last_modified))))

                    date_delta = datetime.today() - datetime.fromtimestamp(dir_last_modified)

                    #logging.info(exhaustive_initial_poll)
                    #logging.info(is_initial_poll)
                    #logging.info("(exhaustive_initial_poll and is_initial_poll)" +
                    #             str((exhaustive_initial_poll and is_initial_poll)))
                    #logging.info("timedelta(days=poll_dirs_margin_days)" +
                    #             str(timedelta(days=poll_dirs_margin_days)))
                    #logging.info("date_delta" + str(date_delta))

                    # poll images in directories more recent than today + poll_dirs_date_margin_days
                    if date_delta <= timedelta(days=poll_dirs_margin_days) or \
                            (exhaustive_initial_poll and is_initial_poll):

                        logging.info("Image folder is more recent")

                        # set file date to test inserting into db to last poll latest file minus margin
                        latest_filedate_last_poll_with_margin = latest_filedate_last_poll - \
                            latest_file_change_margin

                        current_dir_latest_filedate = import_plate_images_and_meta(plate_dir,
                                                                                   latest_filedate_last_poll_with_margin)

                        # keep track of latest file in this current poll
                        current_poll_latest_filedate = max(current_poll_latest_filedate,
                                                           current_dir_latest_filedate)

                        # only update with latest file when everything is checked once

                except Exception as e:
                    logging.exception("Exception in plate dir")
                    with open(exception_file, 'a') as exc_file:
                        exc_file.write("Exception, time:" +
                                       str(datetime.today()) + "\n")
                        exc_file.write("plate_dir:" + str(plate_dir) + "\n")
                        exc_file.write(traceback.format_exc())

        # Set latest file mod for all monitored dirs
        latest_filedate_last_poll = max(
            latest_filedate_last_poll, current_poll_latest_filedate)

        elapsed_time = time.time() - start_time
        logging.info("Time spent polling: " + str(elapsed_time))

        is_initial_poll = False

        # Sleep until next polling action
        logging.info("Going to sleep for: " + str(sleep_time) + "sek")
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
    # parser.add_argument('-ll', '--log-level', help='Description for xxx argument',
    #                    default=imgdb_settings.LOG_LEVEL)

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
