import re
import os
import logging

def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # https://regex101.com/

    # project, plate
    match = re.search('.*/external-datasets/(.*?)/(.*?)/([0-9]{4})-([0-9]{2})-([0-9]{2})/(.*?)/', path)
    if match is None:
      logging.debug("None match")
      return None

    project = match.group(1)
    subdir = match.group(2)

    date_year = match.group(3)
    date_month = match.group(4)
    date_day_of_month = match.group(5)
    plate = match.group(6)

    logging.debug("project: " + project)
    logging.debug("plate: " + plate)


    # well, site, channel, thumb, guid, extension
    match = re.search('.*/'           # any until last /
      + '(.*_)?' # optional text delimited by _ (1)
      + '([A-Z0-9]*)'  # well (2)
      + '_s([0-9]*)'   # wellsample (3)
      + '_w([0-9]*)'  # Channel (color channel?) (4)
      + '(_thumb)?'   # thumb
      + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})?'  # Image GUID (optional) [5]
      + r'\.(.*)', path)   # Extension [6]

    if match is None:
      return None

    well = match.group(2)
    site = match.group(3)
    channel = match.group(4)
    is_thumbnail = match.group(5) is not None
    guid = match.group(6)
    

    # Return if wrong extension
    extension = match.group(7)
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if not extension.lower().endswith( valid_extensions ):
      logging.debug("no extension")
      return None

    # logging
    logging.debug("well" + well)
    logging.debug("site" + str(site))
    logging.debug("channel" + str(channel))
    logging.debug("guid" + str(guid))
    logging.debug("extensionid" + str(extension))


    metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': date_year,
      'date_month': date_month,
      'date_day_of_month': date_day_of_month,
      'project': project,
      'magnification': '?x',
      'plate': plate,
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'channel': channel,
      'is_thumbnail': is_thumbnail,
      'guid': guid,
      'extension': extension,
      'timepoint': 1,
      'channel_map_id': 27,
      'microscope': "Unknown",
      'parser': os.path.basename(__file__)
    }

    return metadata

  except:
    logging.exception("exception")
    logging.debug("could not parse")
    return None



if __name__ == '__main__':
    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)


    retval = parse_path_and_file("/share/data/external-datasets/Morphomac/torkild/2023-08-11/23764/2023-U35_THP-1_I02_s1_w3_thumbA99DF1CF-9039-4190-8FB9-0594BBE3A896.tif")
    print("\nretval = " + str(retval))

    