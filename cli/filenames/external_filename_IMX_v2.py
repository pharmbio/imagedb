import re
import os
import logging

def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # https://regex101.com/

    # project, plate
    match = re.search('.*/external-datasets/(.*)/(.*)/', path)
    if match is None:
      logging.debug("None match")
      return None

    project = match.group(1)
    plate = match.group(2)

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
      'date_year': 2024,
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


        # Test with the provided examples
    paths = [
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s4_w150ACA59D-CE24-4C6D-9A69-55773E3F4DD6.tif",
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s2_w2_thumb497B52A2-6A42-4806-ADBE-C3194ED71882.tif",
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s1_w20886E4D6-AACE-4092-B1E4-7B951AE4581F.tif"
      "/share/data/external-datasets/Morphomac/Musemakrofager-U44-2024/Musemakrofager-U44-2024_B02_s1_w12FBAB2FF-6003-4BAA-9D58-85488028A363.tif"
    ]

    for p in paths:
        retval = parse_path_and_file(p)
        print("\nInput:", p)
        print("Parsed metadata:", retval)
