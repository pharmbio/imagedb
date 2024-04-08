import re
import os
import logging

# file examples
# /share/data/external-datasets/2020_11_04_CPJUMP1/images/BR00116992__2020-11-05T21_31_31-Measurement1/Images/r16c24f09p01-ch3sk1fk1fl1.tiff


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # /share/data/external-datasets/2020_11_04_CPJUMP1/images/BR00116992__2020-11-05T21_31_31-Measurement1/Images/r16c24f09p01-ch3sk1fk1fl1.tiff

    # project, plate, date

    logging.debug("inside parse_path_and_file")

    #match = re.search('.*/external-datasets/(.+?)/(.+?)/(.+?)__([0-9]{4})-([0-9]{2})-([0-9]{2})T.*/Images/', path) # /project/plate/date (yyyy-mm-dd)
    match = re.search('.*/external-datasets/(.+?)/(.+?)/(.+?)/Images/', path) # /project/plate/date (yyyy-mm-dd)
    logging.debug(f'match {match}')
    if match is None:
      return None
    subdir_not_used = match.group(1)
    project = match.group(2)
    plate = match.group(3)

    logging.debug("project" + project)
    logging.debug("plate" + plate)

    # well, site, channel, thumb, guid, extension
    match = re.search('.*\/'           # any until last /
      + 'r(.+?)' # row (1)
      + 'c(.+?)'  # col (2)
      + 'f(.+?)'  # wellsample (field) (3)
      + 'p(.+?)'   # plane (z) (4)
      + '-'
      + 'ch([0-9]+)'  # Channel (color channel?) (5)
      + 'sk([0-9]+)'  # dont know (6)
      + 'fk([0-9]+)'  # dont know (7)
      + 'fl([0-9]+)'  # dont know (8)
      + '(\.tiff?)?', path)   # Extension (9)

    if match is None:
      return None


    row = match.group(1)
    col = match.group(2)
    row_as_chr = chr(64 + int(row))

    well = row_as_chr + col

    site = match.group(3)
    z = match.group(4)

    channel = match.group(5)

    extension = match.group(9)
    # Return if wrong extension
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if not extension.lower().endswith(valid_extensions):
      return None

    # logging
    logging.debug("well" + well)
    logging.debug("site" + str(site))
    logging.debug("channel" + str(channel))
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
      'z': z,
      'channel': channel,
      'is_thumbnail': False,
      'guid': 'no-guid',
      'extension': extension,
      'timepoint': 1,
      'channel_map_id': 6,
      'microscope': "Opera",
      'parser': os.path.basename(__file__)
    }

    return metadata

  except:
    logging.exception("could not parse")
    logging.info("could not parse")
    return None


if __name__ == '__main__':
    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    # Testparse
    retval = parse_path_and_file("share/data/external-datasets/compoundcenter/specs1K-v2/YML2_1_3__2022-11-02T10_35_46-Measurement 1/Images/r02c02f04p01-ch4sk1fk1fl1.tiff")
    print(str(retval))

    retval = parse_path_and_file("/share/data/external-datasets/compoundcenter/CBCS-compound-collection/P101056-U2OS-CBCS-JUMP-v1-MoA90-L1-KI-Opera-20X/Images/r13c06f05p01-ch1sk1fk1fl1.tiff")
    print(str(retval))

