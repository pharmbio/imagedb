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
    match = re.search('.*/external-datasets/(.*?)\/(.*?)\/.*', path)
    if match is None:
      return None
    project = match.group(1)
    plate = match.group(2)


    logging.debug("project: " + project)
    logging.debug("plate: " + plate)


    # well, site, channel, thumb, guid, extension
    match = re.search('.*\/'           # any until last /
      + '(.*_)?' # optional text delimited by _ (1)
      + '([A-Z0-9]*)_'  # well (2([0-9]*)'  
      + 'z([0-9]*)_'  # z (2([0-9]*)'  
      + 'w([0-9]*)'  # z (2([0-9]*)' 
      + '\.(.*)', path)   # Extension [6]

    if match is None:
      return None

    well = match.group(2)
    z = match.group(3)
    channel = match.group(4)

    # Return if wrong extension
    extension = match.group(5)
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if not extension.lower().endswith( valid_extensions ):
      logging.debug("no extension")
      return None

    # logging
    logging.debug("well" + well)
    logging.debug("z" + str(z))
    logging.debug("channel" + str(channel))
    logging.debug("extensionid" + str(extension))


    metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': 2022,
      'date_month': 1,
      'date_day_of_month': 1,
      'project': project,
      'magnification': '?x',
      'plate': plate,
      'well': well,
      'wellsample': 1,
      'channel': channel,
      'is_thumbnail': False,
      'guid': 'no-guid',
      'extension': extension,
      'timepoint': z,
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
    retval = parse_path_and_file("/share/data/external-datasets/bbbc/BBBC021/Week4_27861/D07_s1_w192A46E20-C4C2-4748-B19D-541F77829FFA.tif")
    retval = parse_path_and_file("/share/data/external-datasets/bbbc/BBBC021/Week5_28961/Week5_130707_E04_s2_w2C65C4A21-EF2A-4E99-BF05-C07F5B1C529E.tif")
    print("retval: " + str(retval))
    retval = parse_path_and_file("/share/data/external-datasets/bbbc/BBBC021_selection/Week5_28921/Week5_130707_B05_s2_w1F5518E16-4A9B-4630-B7D3-DF9E55CD423C.tif")
    print("retval: " + str(retval))

    retval = parse_path_and_file("/share/data/external-datasets/spheroids/221020-cr-spheroid-pilot7/221020-cr-spheroid-pilot7_A03_z013_w4.tif")
    print("\nretval = " + str(retval))

    # .*\/(.*)\/(.*)\/.*
    # .*\/(.*)_s(.*)_w([0-9]+)([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})(.*)\.(.*)

