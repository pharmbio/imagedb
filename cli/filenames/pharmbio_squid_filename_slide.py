import re
import os
import logging
import datetime

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/martin-tissue-slide/slide-acquisition2/A1_s710_x7_y23_z1_fluo730.tiff
#


# Compile a regex pattern to match the structured file path and name, with case-insensitivity for Windows compatibility
__pattern_path_and_file = re.compile(r'''
    ^.*/squid/                                  # Match start and any characters until "/squid/"
    (.*?)/                                      # Capture project name
    (.*?)/                                      # Capture plate/slide name
    (t[0-9]+/)?                                 # Optionally capture timepoint (e.g., "t1/")
    ([A-Z])([0-9]+)_                            # Capture well position (always A1)
    s([0-9]+)_                                  # Capture site index
    x([0-9]+)_                                  # Capture site x coordinate
    y([0-9]+)_                                  # Capture site y coordinate
    (z[0-9]+_)?                                 # Optionally capture site z coordinate
    (.*?)                                       # Capture imaging type and wavelength (e.g., fluo730)
    (\..*)                                      # Capture file extension
''', re.IGNORECASE | re.VERBOSE)


def parse_path_and_file(path):
 # If something errors (file not parsable with this parser, then exception and return None)
 try:
  match = re.search(__pattern_path_and_file, path)

  logging.debug(f'match: {match}')

  if match is None:
    return None

  logging.debug(f'match: {match.groups() }')

  tp = match.group(3)
  if tp:
    timepoint = tp[1:-1] # remove t and /
  else:
    timepoint = 0

  logging.debug(f'timepoint: {timepoint}')

  imaging_type = match.group(10)
  logging.debug(imaging_type)
  if imaging_type.startswith('fluo'):
    channel_name = imaging_type[4:]

    logging.debug(f"channel_name: {channel_name}")

    channels_v1 = ['405', '488', '561', '638', '730']
    channels_v2 = ['385', '470', '510', '560', '640']

    if channel_name in channels_v1:
      channels = channels_v1
      channel_map_id = 10
    elif channel_name in channels_v2:
      channels = channels_v2
      channel_map_id = 28

    channel_pos = channels.index(channel_name) + 1


  elif imaging_type == 'BF':
    channel_name = 'BF'
    channel_pos = 6
    channel_map_id = 22 # Brightfield and other channels
  else:
     channel_name = 'Unknown'
     channel_pos = 1
     channel_map_id = 10

  logging.debug(f"channel_map_id: {channel_map_id}")

  site = int(match.group(6))
  site_x = int(match.group(7))
  site_y = int(match.group(8))

  letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef"
  well = f"{letters[site_x]}{site_y:02d}"

  z_val = match.group(9)
  if z_val:
    z = int(z_val[1:-1]) # remove leading z and trailing _
  else:
    z = 0

  # Get file creation timestamp
  c_time = os.path.getctime(path)
  date_create = datetime.datetime.fromtimestamp(c_time)

  # Format as ISO 8601 (YYYY-MM-DDTHH:MM:SS)
  date_iso = date_create.strftime("%Y-%m-%dT%H:%M:%S")

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_iso': date_iso,
      'project': match.group(1),
      'magnification': '?x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'x': site_x,
      'y': site_y,
      'z': z,
      'channel': channel_pos,
      'channel_name': channel_name,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(11),
      'timepoint': timepoint,
      'channel_map_id': channel_map_id,
      'microscope': "squid",
      'parser': os.path.basename(__file__)
  }

  return metadata

 except:
    logging.exception("exception")
    logging.debug("could not parse")
    return None


if __name__ == '__main__':
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    retval = parse_path_and_file(
        "/share/mikro/squid/martin-tissue-slide/slide-acquisition2/A1_s710_x7_y23_z1_fluo730.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/martin-tissue-slide/slide-acquisition2/A1_s881_x18_y28_z1_fluo405.tiff")
    print("retval = " + str(retval))

    






