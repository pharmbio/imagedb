import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_2_2_Fluorescence_638_nm_Ex.tiff
#


# Compile a regex pattern to match the structured file path and name, with case-insensitivity for Windows compatibility
__pattern_path_and_file = re.compile(r'''
    ^.*/squid/                                  # Match start and any characters until "/squid/"
    (.*?)/                                      # Capture project name
    (.*?)_                                      # Capture plate
    ([0-9]{4})-([0-9]{2})-([0-9]{2})_           # Capture date (yyyy-mm-dd)
    (.*?)/                                      # Capture time or additional info until the next slash
    (t[0-9]+/)?                                 # Optionally capture timepoint (e.g., "t1/")
    ([A-Z])([0-9]+)_                            # Capture well position (letter and numbers)
    s([0-9]+)_                                  # Capture site index
    x([0-9]+)_                                  # Capture site x coordinate
    y([0-9]+)_                                  # Capture site y coordinate
    (z[0-9]+_)?                                 # Optionally capture site z coordinate
    (.*?)_                                      # Capture imaging type (e.g., Fluorescence, BF)
    (.*?)                                       # Capture wavelength or light source
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

  tp = match.group(7)
  if tp:
    timepoint = tp[1:-1] # remove t and /
  else:
    timepoint = 0

  time_of_day = match.group(6).replace('.',':')
  date_iso = f"{match.group(3)}-{match.group(4)}-{match.group(5)}T{time_of_day}"

  row = match.group(8)
  col = match.group(9)
  well = f'{row}{col}'

  imaging_type = match.group(14)
  logging.debug(imaging_type)
  if imaging_type == 'Fluorescence':
    channel_name = match.group(15).split('_nm')[0]

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
    channel_pos = 6
    channel_map_id = 22
  else:
     channel_pos = 1
     channel_map_id = 10

  site = int(match.group(10))
  site_x = int(match.group(11))
  site_y = int(match.group(12))

  z_val = match.group(13)
  if z_val:
    z = int(z_val[1:-1]) # remove z and
    channel_pos = z + 1
  else:
    z = 0

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_iso': date_iso,
      'project': match.group(1),
      'magnification': '20x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'x': site_x,
      'y': site_y,
      'z': z,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(16),
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
        "/share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_1_2_2_Fluorescence_638_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/test/Agilent/test_2022-09-26_13-12-22.804556/0/D16_1_2_2_Fluorescence_638_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/ColoPaint/pilot3-colopaint-P1-L2_2022-12-14_16.19.09/E02_s2_x1_y0_Fluorescence_730_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/FluoCells/test_2022-12-16_12.06.09/C06_s1_x0_y0_Fluorescence_638_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/Gentle/Gentle_2022-12-21_15.04.42/B05_s3_x0_y1_Fluorescence_730_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/Colo/pilot5-DLD1_2023-03-08_16.19.17/I07_s6_x2_y1_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/squid/BlueWash-auto/labauto-plate3-FA_2023-04-04_16.12.04/t1/B04_s5_x1_y1_z0_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/squid/BlueWash-auto/labauto-plate3-FA_2023-04-04_16.12.04/t1/G17_s6_x2_y1_z1_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))





