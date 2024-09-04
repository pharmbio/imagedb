import re
import os
import logging
import datetime

# file examples
# /share/data/external-datasets/christa/KI-NIKON/Spheroid-1_z001_CONC.tif
# /share/data/external-datasets/christa/KI-NIKON/spheroid-1_z002_SYTO.tif


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # https://regex101.com/

    # project, plate
    match = re.search(r'.*/external-datasets/christa/(.*?)/.*', path)
    if match is None:
      return None
    project = "KI-NIKON"
    plate = "KI_NIKON_PLATE_A"

    logging.debug("project: " + project)
    logging.debug("plate: " + plate)

    match = re.search(
        r'.*/[Ss]pheroid-'     # match any path and 'Spheroid-' or 'spheroid-'
        + r'(\d+)'             # well (one or more digits)
        + r'_z(\d+)'           # z (one or more digits)
        + r'_([A-Z_]+)'         # channel (one or more uppercase letters or Underscore)
        + r'\.(.*)',           # Extension
        path
    )

    if match is None:
        return None

    well_col = match.group(1)
    well = f'A0{well_col}'

    site = 1

    z = match.group(2)

    channel_name = match.group(3)
    channels = ['HOECHST','SYTO','PHA_WGA','MITO','CONC']
    channel_pos = channels.index(channel_name) + 1

    # Return if wrong extension
    extension = match.group(4)
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg")
    if not extension.lower().endswith(valid_extensions):
        logging.debug("no extension")
        return None

    # file creation timestamp
    c_time = os.path.getctime(path)
    date_create = datetime.datetime.fromtimestamp(c_time)

    # logging
    logging.debug("well" + well)
    logging.debug("z" + str(z))
    logging.debug("channelpos" + str(channel_pos))
    logging.debug("extensionid" + str(extension))

    metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': date_create.year,
      'date_month': date_create.month,
      'date_day_of_month': date_create.day,
      'project': project,
      'magnification': '?x',
      'plate': plate,
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'z': z,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': 'no-guid',
      'extension': extension,
      'timepoint': 1,
      'channel_map_id': 10,
      'microscope': "Nikon-KI",
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
    retval = parse_path_and_file("/share/data/external-datasets/christa/KI-NIKON/Spheroid-1_z001_CONC.tif")
    print("retval: " + str(retval))
    retval = parse_path_and_file("/share/data/external-datasets/christa/KI-NIKON/spheroid-2_z002_SYTO.tif")
    print("retval: " + str(retval))
    retval = parse_path_and_file("/share/data/external-datasets/christa/KI-NIKON/Spheroid-1_z001_PHA_WGA.tif")
    print("retval: " + str(retval))
