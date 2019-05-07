#!/usr/bin/env python3

import datetime
import fnmatch
import logging
import os
import re
import sys
import traceback
import glob
import pymongo

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
# file example
# /share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/ACHN-20X-P009060/2019-02-19/51/ACHN-20X-P009060_G11_s9_w52B1ACE5F-5E6A-4AEC-B227-016795CE2297.tif
# or
# /share/mikro/IMX/MDC Polina Georgiev/PolinaG-U2OS/181212-U2OS-20X-BpA-HD-DB-high/2018-12-12/1/181212-U2OS-20X-BpA-HD-DB-high_E02_s7_w3_thumbCFB5B241-4E5B-4AB4-8861-A9B6E8F9FE00.tif
__pattern_path_and_file   = re.compile('^'
                            + '.*'        # any
                            + '([0-9]{4})-([0-9]{2})-([0-9]{2})' # date (yyyy, mm, dd) (1,2,3)
                            + '.*/'      # any until last /
                            + '([0-9]{6}-)?' # maybe date here also (4)
                            + '([^-]+)'   # screen-name (5)
                            + '-([^-]+)'  # magnification (6)
                            + '-([^_]+)'  # plate (7)
                            + '_([^_]+)'  # well (8)
                            + '_s([^_]+)'  # wellsample (9)
                            + '_w([0-9]+)' # Channel (color channel?) (10)
                            + '(_thumb)?'  # Thumbnail (11)
                            + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})'  # Image GUID [12]
                            + '(\.tiff?)?'  # Extension [13]
                            + '$'
                            ,
                            re.IGNORECASE)  # Windows has case-insensitive filenames

def parse_path_and_file(path):
  match = re.search(__pattern_path_and_file, path)

  logging.debug("path" + str(path))

  if match is None:
    return None

  # logging.debug("match" + str(match.group(1)))
  # logging.debug("match" + str(match.group(2)))
  # logging.debug("match" + str(match.group(3)))
  # logging.debug("match" + str(match.group(4)))
  # logging.debug("match" + str(match.group(5)))
  # logging.debug("match" + str(match.group(6)))

  optional_second_date = match.group(4)
  if optional_second_date is None:
    optional_second_date = ""

  metadata = {
    'path': path,
    'filename': os.path.basename(path),
    'date_year': int(match.group(1)),
    'date_month': int(match.group(2)),
    'date_day_of_month': int(match.group(3)),
    'screen': match.group(5),
    'magnification': match.group(6),
    'plate': match.group(7),
    'well': match.group(8),
    'wellsample': match.group(9),
    'color_channel': int(match.group(10)),
    'is_thumbnail': match.group(11) is not None,
    'guid': match.group(12),
    'extension': match.group(13),
    'image_name': (optional_second_date +
                   match.group(5) + '-' +
                   match.group(6) + '-' +
                   match.group(7) + '_' +
                   match.group(8) + '_s' +
                   match.group(9)),
    'sort_string':(optional_second_date +
                   match.group(5) + '-' +
                   match.group(6) + '-' +
                   match.group(7) + '_' +
                   match.group(8) + '_s' +
                   match.group(9).zfill(2) + '_w' +
                   match.group(10).zfill(2)),

  }

  return metadata

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
                            + '([^-/]+)'  # screen-name (2)
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
    'screen': match.group(2),
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
# Recurses dir and returns time of file with last modification date
#
def getLastModificationInDir(path, pattern):
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
# Recursively gets all (valid) imagefiles in subdirs
# e.g. *.tif, jpg and not *thumb"
#
def get_all_valid_images(path):
  # get all files
  all_files = glob.glob(os.path.join(path, '**/*'))

  logging.debug(all_files)

  # filter the ones we want
  pattern_file_filter = re.compile('^(?!.*thumb)(?=.*tif|.*jpg)') # not "thumb" but contains tif or jpg
  filtered_files = list(filter(pattern_file_filter.match, all_files))

  return filtered_files

#
# Sorting iamge names needs to be done on metadata 'sort_string'
# because of site and channel that need to
# have values with leading 0 to be sorted correct
#
def image_name_sort_fn(filename):
  metadata = parse_path_and_file(filename)
  return metadata['sort_string']

#
# Returns true if any of files in list is in database already
#
def is_image_in_db(images):
  return False

def add_plate_metadata(images):
  logging.info("start add_plate_metadata")
  # sort images with image_name_sort_fn
  # makes sure well, wellsample and channels come sorted
  # after each other when looping the list
  images.sort(key=image_name_sort_fn)

  myclient = pymongo.MongoClient("mongodb://%s:%s@localhost:27017/" % (DB_USER, DB_PASS))
  mydb = myclient["pharmbio_db"]
  mycol = mydb["pharmbio_microimages"]

  # Loop all Images
  for image in images:
    img_meta = parse_path_and_file(image)

    document = { 'metadata': img_meta }

    x = mycol.insert_one(document)


def plateExists(name):
  return False


#
# Main import function
#
def import_plate_images_and_meta(plate_date_dir):
  logging.debug("start import_plate_images_and_meta:" + str(plate_date_dir))
  all_images = get_all_valid_images(plate_date_dir)

  # Check that no image is in database already
  images_uploaded = is_image_in_db(all_images)
  if images_uploaded == True:
    # Exit
    sys.exit("# Exit here")

  logging.debug(all_images)

  # Add metadata
  add_plate_metadata(all_images)

#
#  Main entry for script
#
try:

  #
  # Configure logging
  #
  #logging.basicConfig(level=logging.INFO)
  #logging.getLogger("omero").setLevel(logging.WARNING)

  logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.DEBUG)

  #fileHandler = logging.FileHandler("/scripts/import-omero.log", 'w')
  mylogformatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
  #fileHandler.setFormatter(mylogformatter)
  rootLogger = logging.getLogger()
  #rootLogger.addHandler(fileHandler)

  logging.info("Start script")

  # read password from environment
  #OMERO_ROOTPASS = os.environ['ROOTPASS']
  DB_USER = "root"
  DB_PASS = "example"

  proj_root_dir = "share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/"

  #proj_root_dir = "/share/mikro/IMX/MDC Polina Georgiev/PolinaG-U2OS/"

  plate_filter = ""

  # last_mod_date = getLastModificationInDir(proj_root_dir, '*')

  # Get all subdirs (these are the top plate dir)
  plate_dirs = get_subdirs(proj_root_dir)
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
        # TODO create screen? Add to correct group, permissions?
        #
        plate_exists = plateExists(metadata['plate'])
        if not plate_exists:
          # import images and create database entries for plate, well, site etc.
          import_plate_images_and_meta(plate_date_dir)

        else:
          logging.info("Plate already in DB: " + metadata['plate']);
          #sys.exit("# Exit here")

except Exception as e:
  print(traceback.format_exc())

  logging.info("Done script")

