import re
import os
import logging
import datetime

# file examples
# /share/data/external-datasets/2020_11_04_CPJUMP1/images/BR00116992__2020-11-05T21_31_31-Measurement1/Images/r16c24f09p01-ch3sk1fk1fl1.tiff


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    match = re.search(
      r'.*/external-datasets/(.+?)/(.+?)/(.+?)/hs/(.+?)/images/',
      path,
      flags=re.IGNORECASE
    )
    logging.debug(f'match {match}')
    if match is None:
      return None
    project = match.group(1)
    subdir_not_used = match.group(2)
    plate = match.group(3)
    acquisition_gid = match.group(4)
    short_gid = acquisition_gid.split('-')[0]

    plate_acq_name = f"{plate}_{short_gid}"
    logging.debug("project" + project)
    logging.debug("plate" + plate)
    logging.debug("plate_acq_name" + plate_acq_name)

    # well, site, channel, thumb, guid, extension
    match = re.search(
      r'.*/'
      r'r(?P<row>[0-9]+)'
      r'c(?P<col>[0-9]+)'
      r'f(?P<site>[0-9]+)'
      r'p(?P<z>[0-9]+)'
      r'-'
      r'ch(?P<channel>[0-9]+)'
      r'(?:sk[0-9]+fk[0-9]+fl[0-9]+|t[0-9]+)?'
      r'\.(?P<extension>[A-Za-z0-9]+)$',
      path
    )

    if match is None:
      return None

    row = match.group('row')
    col = match.group('col')
    row_as_chr = chr(64 + int(row))

    well = row_as_chr + col

    site = match.group('site')
    z = match.group('z')

    channel = match.group('channel')

    extension = match.group('extension').lower()
    # Return if wrong extension
    valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
    if extension not in valid_extensions:
      return None

    # file creation timestamp
    c_time = os.path.getctime(path)
    date_create = datetime.datetime.fromtimestamp(c_time)

    # logging
    logging.debug("well" + well)
    logging.debug("site" + str(site))
    logging.debug("channel" + str(channel))
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
      'plate_acq_name': plate_acq_name,
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
    retval = parse_path_and_file("/share/data/external-datasets/mini3D/ki/250627_PHH_exp_6_livedrop_minispheroids_drug_exposure_CP_chronic/hs/7c57ee02-ad08-4aa0-88d6-47911861643a/images/r02c06/r02c06f01p06-ch04t01.tiff")
    print(str(retval))

    retval = parse_path_and_file("/share/data/external-datasets/mini3D/ki/250627_PHH_exp_6_livedrop_minispheroids_drug_exposure_CP_chronic/hs/7c57ee02-ad08-4aa0-88d6-47911861643a/images/r04c16/r04c16f02p06-ch06t01.tiff")
    print(str(retval))

    
