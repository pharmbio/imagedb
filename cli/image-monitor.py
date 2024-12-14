#!/usr/bin/env python3

import logging
import argparse
import os
from pathlib import Path
import re
import time
import traceback
import glob
from typing import Dict, List
from unittest import result
import psycopg2
from psycopg2 import pool
import json
from datetime import datetime

import filenames.filename_parser
import image_tools
import settings as imgdb_settings

__connection_pool = None

IMAGE_EXTENSIONS = (".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp") # lower case in this tuple collection
EXCLUDED_EXTENSIONS = (".ome.tiff.not.used.anymore") # lower case in this tuple collection
EXCLUDED_PREFIXES = ("otf_") # lower case in this tuple collection

def get_connection():

    global __connection_pool
    if __connection_pool is None:
        __connection_pool = pool.SimpleConnectionPool(1, 2, user=imgdb_settings.DB_USER,
                                                               password=imgdb_settings.DB_PASS,
                                                               host=imgdb_settings.DB_HOSTNAME,
                                                               port=imgdb_settings.DB_PORT,
                                                               database=imgdb_settings.DB_NAME)
    return __connection_pool.getconn()


def put_connection(pooled_connection):

    global __connection_pool
    if __connection_pool:
        __connection_pool.putconn(pooled_connection)


def get_all_image_files(dir):
    # get all files
    logging.info(dir)

    image_files = []
    for file in os.listdir(dir):
        file_lower = file.lower()  # Convert to lower case once to avoid multiple conversions
        if (file_lower.endswith(IMAGE_EXTENSIONS) and
                not (file_lower.endswith(EXCLUDED_EXTENSIONS) or file_lower.startswith(EXCLUDED_PREFIXES))):

            absolute_file = os.path.join(dir, file)
            image_files.append(absolute_file)

    return image_files


def make_thumb_path(image, thumbdir):
    # need to strip / otherwise path can not be joined
    image_subpath = image.strip("/")
    thumb_path = os.path.join(thumbdir, image_subpath)
    return thumb_path

def getPlateBarcodeFromPlateAcquisitionName(acquisition_name):

    # extract barcode from acquisition_name (if there is one)
    match = re.match(r'(PB?\d+)', acquisition_name)
    if match:
        return match.group(1)

    # return default barcode
    barcode = acquisition_name
    return barcode


def insert_meta_into_table_images(img_meta, plate_acq_id):

    conn = None
    try:

        insert_query = "INSERT INTO images(plate_acquisition_id, plate_barcode, timepoint, well, site, channel, channel_name, z, path) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connection()
        insert_cursor = conn.cursor()
        insert_cursor.execute(insert_query, (plate_acq_id,
                                             getPlateBarcodeFromPlateAcquisitionName(img_meta['plate']),
                                             img_meta['timepoint'],
                                             img_meta['well'],
                                             img_meta['wellsample'],
                                             img_meta['channel'],
                                             img_meta.get('channel_name', None),
                                             img_meta.get('z', 0),
                                             img_meta['path']
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
    plate_acq_id = select_plate_acq_id(img_meta.get('folder', os.path.dirname(img_meta['path'])))

    if plate_acq_id is None:
        plate_acq_id = insert_plate_acq(img_meta)

    return plate_acq_id


def select_plate_acq_id(acquisition_folder):

    conn = None

    try:

        query = ("SELECT id "
                 "FROM plate_acquisition "
                 "WHERE folder = %s ")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (acquisition_folder,))
        plate_acq_id = cursor.fetchone()
        cursor.close()

        return plate_acq_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)

def getChannelMapIDFromMapping(project, plate_acq_name):
    conn = None

    try:

        query = (
                 "SELECT channel_map "
                 "FROM channel_map_mapping "
                 "WHERE project = %s "
                 "AND "
                 "( plate_acquisition_name = %s OR plate_acquisition_name = '*')"
                 )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (project, plate_acq_name))
        result = cursor.fetchone()
        cursor.close()

        # set default if nothing speciffic for this plate or plate_acquisition
        if result:
            channel_map_id = result[0]
        else:
            channel_map_id = None

        logging.info(f"channel_map_id = {channel_map_id}")

        return channel_map_id

    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


def create_imaged_timepoint(img_meta):

    date_iso = img_meta.get('date_iso')
    if date_iso:
        timepoint = datetime.fromisoformat(date_iso)
    else:
        year = int(img_meta['date_year'])
        month = int(img_meta['date_month'])
        day = int(img_meta['date_day_of_month'])
        timepoint = datetime(year, month, day)

    return timepoint

def insert_plate_acq(img_meta):

    conn = None
    try:

        imaged_timepoint = create_imaged_timepoint(img_meta=img_meta)

        # get channel map for speciffic projects/plates
        specific_ch_map = getChannelMapIDFromMapping(img_meta['project'], img_meta['plate'])
        if specific_ch_map:
            img_meta['channel_map_id'] = specific_ch_map

        query = "INSERT INTO plate_acquisition(plate_barcode, name, project, imaged, microscope, channel_map_id, timepoint, folder) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (getPlateBarcodeFromPlateAcquisitionName(img_meta['plate']),
                               img_meta['plate'],
                               img_meta['project'],
                               imaged_timepoint,
                               img_meta['microscope'],
                               img_meta['channel_map_id'],
                               img_meta['timepoint'],
                               img_meta.get('folder', os.path.dirname(img_meta['path']))
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


def image_exists_in_db(image_path):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        exists_path_query = "SELECT EXISTS (SELECT 1 FROM images WHERE path = %s)"
        cursor.execute(exists_path_query, (image_path,))

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

def addImageToImagedb(img_meta):

    # check if image exists if so exit, exiting before creating plate_acq means that you can delete plate_acq from db and just keep files
    if image_exists_in_db(img_meta['path']):
        logging.debug('image exists in db already, return')
        return

    # First select plate acquisition id, or insert it if not there
    plate_acq_id = select_or_insert_plate_acq(img_meta)

    # Insert into images table
    insert_meta_into_table_images(img_meta, plate_acq_id)

    # create thumb image
    thumb_path = make_thumb_path(img_meta['path'],
                                 imgdb_settings.IMAGES_THUMB_FOLDER)
    logging.debug(thumb_path)

    # Only create thumb if not exists already and not skip_thumb is specified and set to True
    # make inside try-catch so a corrupted image doesn't stop it all
    # also try 3 times with some sleep in between to allow for images that are not
    # completely uploaded
    make_thumb = img_meta.get('make_thumb', True)
    if make_thumb and not os.path.exists(thumb_path):

        #logging.debug(f'makethumb: {thumb_path}')
        attempts = 0
        while attempts < 3:
            try:
                image_tools.makeThumb(img_meta['path'], thumb_path, False)
                break
            except Exception as e:
                logging.error("Exception making thumb image: %s", e)
                logging.error("image: " + str(img_meta['path']))
                logging.error("thumb_path: " + str(thumb_path))
                logging.error(f'will retry x times in x seconds, attempt {attempts}')
                logging.error("After that Continuing since we don't want to break on a single bad image")
                attempts += 1
                time.sleep(10)

def add_plate_to_db(images):
    global processed

    logging.info(f"start add_plate_metadata to db, len(images)(including thumbs): {len(images)}")

    # Loop all Images
    for idx, image in enumerate(images):

        img_meta = filenames.filename_parser.parse_path_and_file(image)

        # img meta should never be None
        if img_meta is None:
            raise Exception('img_meta is None')

        logging.debug(img_meta)

        # Skip thumbnails
        if not img_meta['is_thumbnail']:

            addImageToImagedb(img_meta)

        if idx % 100 == 1:
                logging.info("images processed (including thubs):" + str(idx))
                logging.info("images total to process(including thumbs):" + str(len(images)))

        # Add image to processed images (path as key and timestamp as value)
        processed[ img_meta['path'] ] = time.time()

    logging.info("done add_plate_metadata to db")


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

def select_unfinished_plate_acq_folder():

    conn = None
    try:
        query = ("SELECT folder "
                 "FROM plate_acquisition "
                 "WHERE finished IS NULL")

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


def find_dirs_containing_img_files_recursive_from_list_of_paths(path_list: List[str]):
    for path in path_list:
        if not os.path.exists(path):
            logging.exception(f"Path does not exist: {path}")
        else:
            yield from find_dirs_containing_img_files_recursive(path, True)

def find_dirs_containing_img_files_recursive(path: str, sort_dir_entries: bool = False):
    """
    Yield lowest level directories containing image files as Path (not starting with '.')
    the method is called recursively to find all subdirs
    It breaks the recursion when it finds an image file to avoid looking through all files (long operation)
    """

    if sort_dir_entries:
        iterable_entries = list(os.scandir(path))
        # Sort entries by modification time, most recent first
        iterable_entries.sort(key=lambda e: e.stat().st_mtime, reverse=True)
    else:
        iterable_entries = os.scandir(path)

    for entry in iterable_entries:
        # recurse directories
        if not entry.name.startswith('.') and entry.is_dir():
            yield from find_dirs_containing_img_files_recursive(entry.path)
        if entry.is_file():
            # return parent path if file is imagefile, then break scandir-loop
            if entry.path.lower().endswith( IMAGE_EXTENSIONS ) and not entry.path.lower().endswith( EXCLUDED_EXTENSIONS ):

                parent = Path(entry.path).parent
                yield(parent)
                # A little hack to get subdir "single_images" if it exist, before break looking through this directory
                # check if single_images subdir also exists, if so add that one to
                single_images_dir = parent / "single_images"
                if os.path.exists(single_images_dir):
                    yield single_images_dir

                break


def update_finished_plate_acquisitions(cutoff_time):
    #update_finished_plate_acquisitions_from_file()
    update_finished_plate_acquisitions_from_cutoff_time(cutoff_time)


def update_finished_plate_acquisitions_from_file():
    global processed

    # first get unfinished acq from database
    unfinished = select_unfinished_plate_acq_folder()

    for plate_acq_folder in unfinished:

        # if coordinates.csv file in plate_acq folder, then set finished
        finished_flag_file = os.path.join(plate_acq_folder, "coordinates.csv")
        if os.path.exists(finished_flag_file):
            update_acquisition_finished(plate_acq_folder, time.time())


def update_finished_plate_acquisitions_from_cutoff_time(cutoff_time):
    global processed

    # first get unfinished acq from database
    unfinished = select_unfinished_plate_acq_folder()

    for plate_acq_folder in unfinished:

        # loop processed images in reverse to see when last file was processed for this unfinished folder
        for img_path in reversed(processed):
            if plate_acq_folder in img_path:
                proc_time = processed[img_path]
                logging.info("proc_time=" + str(proc_time))
                logging.info("cutoff_time=" + str(cutoff_time))
                if proc_time < cutoff_time:
                    folder = os.path.dirname(img_path)
                    update_acquisition_finished(folder, cutoff_time)

                # latest proc_time for this acquisition is found, time to break
                break

def update_acquisition_finished(folder: str, timestamp: float):

    logging.info("inside update_acquisition_finished, folder: " + folder)

    conn = None
    try:

        query = (" UPDATE plate_acquisition "
                 " SET finished = %s "
                 " WHERE folder = %s")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (datetime.utcfromtimestamp(timestamp), folder) )
        assert cursor.rowcount == 1, "rowcount should always be 1 for this update query"
        cursor.close()
        conn.commit()
    except Exception as err:
        logging.exception("Message")
        raise err
    finally:
        put_connection(conn)


#
# Main import function
#
def import_plate_images_and_meta(plate_dir: str):
    """
    Main import function
    """

    global processed

    logging.info("start import_plate_images_and_meta: " + str(plate_dir))

    all_images = sorted(get_all_image_files(plate_dir))

    # create a new list with only images not in processed dict
    new_images = [img for img in all_images if img not in processed]

    # import images (if later than latest_import_filedate)
    if len(new_images) > 0:
        add_plate_to_db(new_images)

    logging.info("done import_plate_images_and_meta: " + str(plate_dir))


# directories that don't have images or are throwing errors when processed
blacklist: List[str] = [
    '/share/mikro/IMX/MDC_pharmbio/trash/',
    '/share/mikro2/nikon/trash/',
    '/share/mikro2/squid/trash/'
]

# processed filenames and timestamp when processed
processed: Dict[str, float] = {}


def polling_loop(poll_dirs_margin_days, latest_file_change_margin, sleep_time, proj_root_dirs, exhaustive_initial_poll, continuous_polling):

    global processed, blacklist

    is_initial_poll = True

    logging.info("proj_root_dirs: " + str(proj_root_dirs))

    while True:

        logging.info("***")
        logging.info("")
        logging.info("Staring new poll: " + str(datetime.today()))
        logging.info("")
        logging.info("***")
        logging.info("")

        start_loop = time.time()

        # create new cutoff time
        cutoff_time = time.time() - latest_file_change_margin

        # get finished ones from db
        finished_acq_folders = select_finished_plate_acq_folder()

        # get all image dirs within root dirs (yields dirs sorted by date, most recent first)
        for img_dir in find_dirs_containing_img_files_recursive_from_list_of_paths(proj_root_dirs):

            logging.debug(f"img_dir: {img_dir}")

            # remove finished acquisitions
            if str(img_dir) in finished_acq_folders:
                logging.debug(f"removed because finished: {img_dir}")
                continue

            # remove old dirs
            if is_initial_poll:
                old_dir_cuttoff = 0 # 1970-01-01
            else:
                old_dir_cuttoff = (3600 * 24 * poll_dirs_margin_days)

            if img_dir.stat().st_mtime < old_dir_cuttoff:
                logging.debug(f"removed because old: {img_dir} ")
                continue

            # Initialize the flag for blacklisted items
            is_blacklisted = False
            for blacklisted_item in blacklist:
                if blacklisted_item in str(img_dir):
                    logging.info(f"removed because blacklisted: {img_dir}")
                    is_blacklisted = True
                    break  # Exit the inner loop as we found a match
            # If the directory is blacklisted, continue with the next img_dir
            if is_blacklisted:
                continue

            try:
                import_plate_images_and_meta(str(img_dir))

            except Exception as e:
                logging.exception("Exception in img_dir")
                # add dir to blacklist if there are more than X wrong files in dir
                logging.info(f"Add to blacklist img_dir: {img_dir} ")
                blacklist.append(str(img_dir))
                exception_file = os.path.join(imgdb_settings.ERROR_LOG_DIR, "exceptions-last-poll.log")
                with open(exception_file, 'a') as exc_file:
                    exc_file.write(f"Exception, time: {datetime.today()}\n")
                    exc_file.write(f"img_dir: {img_dir}\n")
                    exc_file.write(traceback.format_exc())


        # If time > 10 min (default cutpoff_time) since last uploaded from unfinished plate_acquisitions
        # If so update plate_acq to finished
        update_finished_plate_acquisitions(cutoff_time)

        # If latest processed file was longer ago than cutofftime,
        # clear processed dict (mainly to release memory)
        clear_processed = False
        for img_path in reversed(processed):
            proc_time = processed[img_path]
            if proc_time < cutoff_time:
                logging.info("clear processed dict")
                clear_processed = True
            # Only check the last
            break
        if clear_processed:
            processed.clear()

        logging.info("elapsed: " + str(time.time() - start_loop) + " sek")

        # dump blacklist in log dir
        if blacklist:
            logfile = os.path.join(imgdb_settings.ERROR_LOG_DIR, "blacklist.json")
            with open(logfile, 'w') as filehandle:
                json.dump(blacklist, filehandle)

        # Sleep until next polling action
        is_initial_poll = False
        logging.info(f"Going to sleep for: {sleep_time} sek")
        logging.info("")
        time.sleep(sleep_time)

        # TODO could skip sleeping if images were inserted... but difficult then with 2 hour margin (all files would be tried again)

        if continuous_polling != True:
            break

def main():

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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Exception out of script")
        print(traceback.format_exc())