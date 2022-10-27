import re
import os
import logging

# file examples
# /share/mikro/IMX/MDC_pharmbio/jonne/384-pilot-4x/2020-08-21/233/384-pilot-4x_D06_w13BB03CA4-CE8C-4DE8-AFE2-1321765D3AAE.tif


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # project, plate, date
    match = re.search('/MDC_pharmbio/(.+?)/(.+?)/([0-9]{4})-([0-9]{2})-([0-9]{2})', path) # /project/plate/date (yyyy-mm-dd)
    if match is None:
      return None

    project = match.group(1)
    plate = match.group(2)
    date_year = match.group(3)
    date_month = match.group(4)
    date_day_of_month = match.group(5)

    logging.debug("project" + project)
    logging.debug("plate" + plate)
    logging.debug("date_year" + date_year)
    logging.debug("date_month" + date_month)
    logging.debug("date_day_of_month" + date_day_of_month)

    # well, site, channel, thumb, guid, extension
    match = re.search('.*\/'           # any until last /
      + '.+?_([^_]+)'  # well (1)
      + '(_s[^_]+)?'   # wellsample (2)
      + '(_w[0-9]+)?'  # Channel (color channel?) (3)
      + '(_thumb)?'     # Thumbnail (4)
      + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})'  # Image GUID [5]
      + '(\.tiff?)?', path)   # Extension [6]

    if match is None:
      return None

    well = match.group(1)

    # parse optional site
    # first set default
    site = 1
    if match.group(2):
      # remove _s from match
      site = match.group(2)[2]

    # parse optional channel
    # first set default
    channel = 1
    if match.group(3):
      # remove _w from match
      channel = match.group(3)[2]

    # make boolean is thumb
    is_thumbnal = match.group(4) is not None

    guid = match.group(5)
    extension = match.group(6)

    # logging
    logging.debug("well" + well)
    logging.debug("site" + str(site))
    logging.debug("channel" + str(channel))
    logging.debug("thumb" + str(is_thumbnal))
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
      'is_thumbnail': is_thumbnal,
      'guid': 'no-guid',
      'extension': ".tif",
      'timepoint': 1,
      'channel_map_id': 1,
      'microscope': "ImageXpress",
      'parser': os.path.basename(__file__)
    }

    return metadata

  except:
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
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/Covid19-Profiling/MRC5-CellDensity-384/2020-06-25/224/MRC5-CellDensity-384_I04_thumbE7E3B2C3-9420-452B-ACB6-89128BDC69BB.tif")
    print(str(retval))

    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1/2022-03-11/965/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1_B02_s8_w3_thumb3DF2C4AE-602A-46F6-84B2-9B31D1981B60.tif")
    print("retval = " + str(retval))
