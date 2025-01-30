#!/usr/bin/env python3

import logging
import argparse
import os
import time
import traceback
from typing import Dict, List

import json
from datetime import datetime

import filenames.filename_parser
import image_tools
import settings as imgdb_settings
import file_utils

from database import Database
from image import Image


def addImageToImagedb(img: Image):

    # check if image exists if so exit, exiting before creating plate_acq means that you can delete plate_acq from db and just keep files
    if img.exists_in_db():
        logging.debug('image exists in db already, return')
        return

    # First select plate acquisition id, or insert it if not there
    plate_acq_id = Database.get_instance().select_or_insert_plate_acq(img)

    # Insert into images table
    img_id = Database.get_instance().insert_meta_into_table_images(img, plate_acq_id)

    # Insert into upload_to_s3 table
    Database.get_instance().insert_into_upload_table(img, plate_acq_id, img_id)

    # create thumb image
    thumb_path = img.make_thumb_path(imgdb_settings.IMAGES_THUMB_FOLDER)
    logging.debug(thumb_path)

    # Only create thumb if not exists already and not skip_thumb is specified and set to True
    # make inside try-catch so a corrupted image doesn't stop it all
    # also try 3 times with some sleep in between to allow for images that are not
    # completely uploaded
    if img.is_make_thumb() and not os.path.exists(thumb_path):

        #logging.debug(f'makethumb: {thumb_path}')
        attempts = 0
        while attempts < 3:
            try:
                image_tools.makeThumb(img.get_path(), thumb_path, False)
                break
            except Exception as e:
                logging.error("Exception making thumb image: %s", e)
                logging.error("image: " + str(img.get_path()))
                logging.error("thumb_path: " + str(thumb_path))
                logging.error(f'will retry x times in x seconds, attempt {attempts}')
                logging.error("After that Continuing since we don't want to break on a single bad image")
                attempts += 1
                time.sleep(10)

def add_plate_to_db(images):
    global processed

    logging.info(f"start add_plate_metadata to db, len(images)(including thumbs): {len(images)}")

    # Loop all Images
    for idx, img_path in enumerate(images):

        img_meta = filenames.filename_parser.parse_path_and_file(img_path)

        # img meta should never be None
        if img_meta is None:
            raise Exception('img_meta is None')

        logging.debug(img_meta)

        img = Image.from_meta(img_meta)

        # Skip thumbnails
        if not img.is_thumbnail():
            addImageToImagedb(img)

        if idx % 100 == 1:
                logging.info("images processed (including thubs):" + str(idx))
                logging.info("images total to process(including thumbs):" + str(len(images)))

        # Add image to processed images (path as key and timestamp as value)
        processed[ img.get_path() ] = time.time()

    logging.info("done add_plate_metadata to db")

def update_finished_plate_acquisitions(cutoff_time):
    update_finished_plate_acquisitions_from_cutoff_time(cutoff_time)


def update_finished_plate_acquisitions_from_file():
    global processed

    # first get unfinished acq from database
    unfinished = Database.get_instance().select_unfinished_plate_acq_folder()

    for plate_acq_folder in unfinished:

        # if coordinates.csv file in plate_acq folder, then set finished
        finished_flag_file = os.path.join(plate_acq_folder, "coordinates.csv")
        if os.path.exists(finished_flag_file):
            Database.get_instance().update_acquisition_finished(plate_acq_folder, time.time())


def update_finished_plate_acquisitions_from_cutoff_time(cutoff_time):
    global processed

    # first get unfinished acq from database
    unfinished = Database.get_instance().select_unfinished_plate_acq_folder()

    for plate_acq_folder in unfinished:

        # loop processed images in reverse to see when last file was processed for this unfinished folder
        for img_path in reversed(processed):
            if plate_acq_folder in img_path:
                proc_time = processed[img_path]
                logging.info("proc_time=" + str(proc_time))
                logging.info("cutoff_time=" + str(cutoff_time))
                if proc_time < cutoff_time:
                    folder = os.path.dirname(img_path)
                    Database.get_instance().update_acquisition_finished(folder, cutoff_time)

                # latest proc_time for this acquisition is found, time to break
                break

#
# Main import function
#
def import_plate_images_and_meta(plate_dir: str):
    """
    Main import function
    """

    global processed

    logging.info("start import_plate_images_and_meta: " + str(plate_dir))

    all_images = sorted(file_utils.get_all_image_files(plate_dir))

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

    Database.get_instance().initialize_connection_pool(
                user=imgdb_settings.DB_USER,
                password=imgdb_settings.DB_PASS,
                host=imgdb_settings.DB_HOSTNAME,
                port=imgdb_settings.DB_PORT,
                database=imgdb_settings.DB_NAME
    )

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
        finished_acq_folders = Database.get_instance().select_finished_plate_acq_folder()

        # get all image dirs within root dirs (yields dirs sorted by date, most recent first)
        for img_dir in file_utils.find_dirs_containing_img_files_recursive_from_list_of_paths(proj_root_dirs):

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
                    logging.debug(f"removed because blacklisted: {img_dir}")
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