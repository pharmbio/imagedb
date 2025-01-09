import re
import os
import logging

# file examples
# /share/data/external-datasets/bbbc/BBBC021/Week4_27861/D07_s1_w192A46E20-C4C2-4748-B19D-541F77829FFA.tif
# /share/data/external-datasets/bbbc/BBBC021/Week5_28961/Week5_130707_E04_s2_w2C65C4A21-EF2A-4E99-BF05-C07F5B1C529E.tif


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # https://regex101.com/

    # project, plate
    match = re.search('.*/external-datasets/Morphomac/widefield/(.*)/TimePoint_(.*?)/.*', path)
    if match is None:
      logging.debug("None match")
      return None
    project = "Morphomac"
    plate = match.group(1).replace('/', '-')
    timepoint = match.group(2)


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
      'date_year': 1970,
      'date_month': 1,
      'date_day_of_month': 1,
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
      'timepoint': timepoint,
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

    # Testparse
    retval = parse_path_and_file("/share/data/external-datasets/Morphomac/widefield/2024-W50-Macrophages-wide/25201/TimePoint_1/2024-W50-Macrophages_E04_s1_w17247AC16-C2A3-41F2-B56D-0ECF158B3234.tif")
    print("\nretval = " + str(retval))
