#!/usr/bin/env python3

import datetime
import fnmatch
import logging
import os
import re
import sys
import time
import traceback
import glob
import pymongo

from filenames.filenames import parse_path_and_file
from image_tools import makeThumb

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
# Returns list of files
#
def recursive_glob(rootdir='.', pattern='*'):
  matches = []
  for root, dirnames, filenames in os.walk(rootdir):
    for filename in fnmatch.filter(filenames, pattern):
      matches.append(os.path.join(root, filename))
  return matches

#
# Recurses dir and returns time of file with last modification dat
def get_last_modification_in_dir(path, pattern):
  files = recursive_glob(path, pattern)
  logging.debug(files)
  latest_file = max(files, key=os.path.getctime)
  logging.debug("latest_file: " + str(latest_file))
  modTimeInEpoc = os.path.getmtime(latest_file)
  modificationTime = datetime.datetime.utcfromtimestamp(modTimeInEpoc)
  return modificationTime

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
#  all_files.extend( glob.glob(os.path.join(path, '**/*.png'), recursive=True))

  logging.debug(all_files)

  # filter the ones we want
  # for now returning all
  #pattern_file_filter = re.compile('^(?!.*thumb)(?=.*tif|.*jpg)') # not "thumb" but contains tif or jpg
  #filtered_files = list(filter(pattern_file_filter.match, all_files))

  return all_files

#
# Returns true if any of files in list is in database already
#
def is_image_in_db(images):
  return False

def image_name_sort_fn(filename):
  metadata = parse_path_and_file(filename)
  return metadata['path']


def make_thumb_path(image, THUMBDIR, IMAGE_ROOT_DIR):
    subpath = str(image).replace(IMAGE_ROOT_DIR, "")
    # Need to strip / otherwise can not join as subpath
    subpath = subpath.strip("/")
    thumb_path = os.path.join(THUMBDIR, subpath)
    return thumb_path

def add_plate_to_db(images):
  logging.info("start add_plate_metadata to db")

  dbclient = pymongo.MongoClient( username=DB_USER,
                                  password=DB_PASS,
                                  # connectTimeoutMS=500,
                                  serverSelectionTimeoutMS=1000,
                                  host=DB_HOST
                                 )
  img_db = dbclient["pharmbio_db"]
  img_collection = img_db["pharmbio_microimages"]

  # sort images (just to get thumb after image)
  images.sort(key=image_name_sort_fn)

  # Loop all Images
  for idx, image in enumerate(images):

    img_meta = parse_path_and_file(image)

    logging.info(img_meta)

    # makeThumb(image, THUMBDIR)

    if not img_meta['is_thumbnail']:

        # check if doc already exists in db
        result = img_collection.find({'path': img_meta['path']})
        if result.count() == 0:
            next_img = images[(idx + 1) % len(images)]
            img_meta_thumb = parse_path_and_file(next_img)
            img_meta['thumbnail_path'] = img_meta_thumb['path']

            document = { 'project': img_meta['project'],
                         'plate': img_meta['plate'],
                         'timepoint': img_meta['timepoint'],
                         'path': img_meta['path'],
                         'metadata': img_meta }

            thumb_path = make_thumb_path(image, THUMBDIR, IMAGE_ROOT_DIR)
            logging.debug(thumb_path)
            makeThumb(image, thumb_path)
            x = img_collection.insert_one(document)
        else:
            print("doc exists already")


def plateExists(name):
  return False


#
# Main import function
#
def import_plate_images_and_meta(plate_date_dir):
  logging.debug("start import_plate_images_and_meta:" + str(plate_date_dir))
  all_images = get_all_image_files(plate_date_dir)

  # Check that no image is in database already
  images_uploaded = is_image_in_db(all_images)
  if images_uploaded == True:
    # Exit
    sys.exit("# Exit here")

  logging.debug(all_images)

  # Add metadata
  add_plate_to_db(all_images)

#
#  Main entry for script
#
try:

  start_time = time.time()
  #
  # Configure logging
  #
  #logging.basicConfig(level=logging.INFO)
  #logging.getLogger("omero").setLevel(logging.WARNING)

  logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.DEBUG)

  #fileHandler = logging.FileHandler("/scripts/import-omero.log", 'w')
  #mylogformatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
  #fileHandler.setFormatter(mylogformatter)
  rootLogger = logging.getLogger()
  #rootLogger.addHandler(fileHandler)

  logging.info("Start script")

  # read password from environment
  #OMERO_ROOTPASS = os.environ['ROOTPASS']
  DB_USER = "root"
  DB_PASS = "example"

  is_docker_version = False
  if "IS_DOCKER_VERSION" in os.environ and os.environ['IS_DOCKER_VERSION'].lower() == 'true':
    is_docker_version = True

  if is_docker_version:
    DB_HOST = "image-mongo"
    THUMBDIR = "/share/imagedb/thumbs/"
    IMAGE_ROOT_DIR = "/share/mikro/IMX/MDC Polina Georgiev"
    proj_root_dirs = [ "exp-TimeLapse/",
                       "exp-WIDE/"
                     ]
  else:
    DB_HOST = "localhost"
    THUMBDIR = "../share/imagedb/thumbs/"
    IMAGE_ROOT_DIR = "../share/mikro/IMX/MDC Polina Georgiev"
    proj_root_dirs = ["exp-TimeLapse/",
                      "exp-WIDE/"
                        ]

  plate_filter = ""

  for proj_root_dir in proj_root_dirs:
    # Get all subdirs (these are the top plate dir)
    image_dir = os.path.join(IMAGE_ROOT_DIR, proj_root_dir )
    plate_dirs = get_subdirs(image_dir)
    logging.debug("plate_dirs" + str(plate_dirs))
    for plate_dir in plate_dirs:
      # filter plate for names
      if plate_filter in plate_dir:
        plate_subdirs = get_subdirs(plate_dir)
        for plate_date_dir in plate_subdirs:
          logging.debug("plate_subdir: " + str(plate_date_dir))

          # Parse filename for metadata (e.g. platename well, site, channet etc.)
          metadata = parse_path_plate_date(plate_date_dir)
          logging.debug("metadata" + str(metadata))

          # Check if plate exists in database (if no - then import folder)
          #
          # TODO create project? Add to correct group, permissions?
          #
          plate_exists = plateExists(metadata['plate'])
          if not plate_exists:
            # import images and create database entries for plate, well, site etc.
            import_plate_images_and_meta(plate_date_dir)

          else:
            logging.info("Plate already in DB: " + metadata['plate']);
            #sys.exit("# Exit here")

  elapsed_time = time.time() - start_time
  logging.info("time spent: " + str(elapsed_time))

except Exception as e:
  print(traceback.format_exc())

  logging.info("Done script")

