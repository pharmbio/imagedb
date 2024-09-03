import re
import os
import logging

from numpy import char

def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:


    # project, plate
    match = re.search('.*/external-datasets/(GEN153-C1)/.*/.*/(.*)/.*', path)
    if match is None:
      return None
    
    project = match.group(1)
    plate = match.group(2)


    logging.debug("project: " + project)
    logging.debug("plate: " + plate)


    # well, site, channel, thumb, guid, extension
    # 1089380472_F16_T0001F005L01A06Z01C06.tif
    match = re.search('.*\/' # any until last /
      + '([0-9]*)'      # plate (1)
      + '_([A-Z0-9]*)_' # well (2)
      + 'T([0-9]*)'     # timepoint (3)
      + 'F([0-9]*)'     # site (4)
      + 'L([0-9]*)'     # ??? (5)
      + 'A([0-9]*)'     # ??? (6)
      + 'Z([0-9]*)'     # z (7)
      + 'C([0-9]*)'     # channeö (8)
      + '\.(.*)', path)   # Extension [9]

    logging.debug("match: " + str(match))

    if match is None:
      return None


    well = match.group(2)
    timepoint = int(match.group(3))
    site = int(match.group(4))
    z = int(match.group(7))
    channel = int(match.group(8))

    # Return if wrong extension
    extension = match.group(9)
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if not extension.lower().endswith(valid_extensions):
      return None

    metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': 2023,
      'date_month': 7,
      'date_day_of_month': 8,
      'project': project,
      'magnification': '?x',
      'plate': plate,
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'channel': channel,
      'z': z,
      'is_thumbnail': False,
      'guid': None,
      'extension': extension,
      'timepoint': timepoint,
      'channel_map_id': 29,
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
 #   retval = parse_path_and_file("/share/data/external-datasets/david/exp180/tp-1/Images/r10c46f01p01-ch6sk1fk1fl1.tiff")
 #   print("retval: " + str(retval))
    retval = parse_path_and_file("/share/data/external-datasets/GEN153-C1/emea-rditimg-darwin-cv8000-2023-07/Cell_Painting_20230707_Phenaros_Epi_U2OS_20230708_202532/1089380472/1089380472_F16_T0001F005L01A06Z01C06.tif")
    print("retval: " + str(retval))


    # .*\/(.*)\/(.*)\/.*
    # .*\/(.*)_s(.*)_w([0-9]+)([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})(.*)\.(.*)

