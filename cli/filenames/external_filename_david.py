import re
import os
import logging

from numpy import char

def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # https://regex101.com/

    # project, plate
    match = re.search('.*/external-datasets/david/(exp.*)/Images/tp.*/.*', path)
    if match is None:
      return None
    project = 'david'
    plate = match.group(1)


    logging.debug("project: " + project)
    logging.debug("plate: " + plate)


    # well, site, channel, thumb, guid, extension
    # r10c03f01p01-ch2sk15fk1fl1.tiff
    match = re.search('.*\/'           # any until last /
      + 'r([0-9]*)'   # row (1)
      + 'c([0-9]*)'   # col (2)
      + 'f([0-9]*)'   # field? (3)
      + 'p([0-9]*)'   # ??? (4)
      + '\-ch([0-9]*)' # channel (5)
      + 'sk([0-9]*)'  # timepoint (6)
      + 'fk([0-9]*)'  # ???? (7)
      + 'fl([0-9]*)'  # ???? (8)
      + '\.(.*)', path)   # Extension [9]

    logging.debug("match: " + str(match))

    if match is None:
      return None


    row = int(match.group(1))
    col = match.group(2)

    # TODO this should be AA AB AC etc after A-Z in future versions
    row_as_char = chr(row + 64)

    well = row_as_char + col
    site = match.group(3)
    channel = match.group(5)
    timepoint = match.group(6)

    # Return if wrong extension
    extension = match.group(9)
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if not extension.lower().endswith(valid_extensions):
      return None

    # logging
    logging.debug("well" + well)
    logging.debug("site" + str(site))
    logging.debug("channel" + str(channel))


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
      'is_thumbnail': False,
      'guid': None,
      'extension': extension,
      'timepoint': timepoint,
      'channel_map_id': 1,
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
  #  retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/jonne/384-pilot-4x/2020-08-21/233/384-pilot-4x_D06_w13BB03CA4-CE8C-4DE8-AFE2-1321765D3AAE.tif")
  #  retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/jonne/384-pilot-4x-4/2020-09-02/262/384-pilot-4x-4_G16_w156A3DA15-CEF2-49C6-B647-3A4321D9B8DC.tif")
    retval = parse_path_and_file("/share/data/external-datasets/david/exp180/tp-1/Images/r10c46f01p01-ch6sk1fk1fl1.tiff")
    print("retval: " + str(retval))
    retval = parse_path_and_file("/share/data/external-datasets/david/exp180/Images/tp-12/r04c03f01p01-ch2sk12fk1fl1.tiff")
    print("retval: " + str(retval))


    # .*\/(.*)\/(.*)\/.*
    # .*\/(.*)_s(.*)_w([0-9]+)([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})(.*)\.(.*)

