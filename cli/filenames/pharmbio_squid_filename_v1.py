import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/D16_2_2_Fluorescence_638_nm_Ex.tiff
# /share/mikro/squid/Colo/pilot5-DLD1_2023-03-08_16.19.17/I07_s6_x2_y1_BF_LED_matrix_full.tiff

__pattern_path_and_file = re.compile('^'
                                     + '.*/squid/'  # any until /squid/
                                       + '(.*?)/'   # project (1)
                                       + '(.*?)[/_]'    # plate (2)
                                       + '([0-9]{4})-([0-9]{2})-([0-9]{2})_(.*?)/' # date (yyyy, mm, dd) (3,4,5) and (time 6)
                                       + '([0-9]+)/'   # timepoint (7)
                                       + '([A-Z])([0-9]+)_'  # well (8,9)
                                       + '([0-9]+)_'   # site index (10)
                                       + '([0-9]+)_'   # site x (11)
                                       + '([0-9]+)_'   # site y (12)
                                       + '(.*?)_' # imaging-type, e,g, Fluorescence, BF (13)
                                       + '(.*?)' # wavelength or Light source (14)
                                       + '(\..*)'      # Extension [15]
                                     ,
                                     re.IGNORECASE)  # Windows has case-insensitive filenames


def parse_path_and_file(path):
 # If something errors (file not parsable with this parser, then exception and return None)
 try:
  match = re.search(__pattern_path_and_file, path)

  logging.debug(f'match: {match}')

  if match is None:
    return None

  logging.debug(f'match: {match.groups() }')

  row = match.group(8)
  col = match.group(9)
  well = f'{row}{col}'

  imaging_type = match.group(13)
  logging.debug(imaging_type)
  if imaging_type == 'Fluorescence':
    channel_name = match.group(14).split('_nm')[0]
    channels = ['405', '488', '561', '638', '730']
    channel_pos = channels.index(channel_name) + 1
    channel_map_id = 10
  elif imaging_type == 'BF':
    channel_pos = 1
    channel_map_id = 21
  else:
     channel_pos = 1
     channel_map_id = 21

  site = int(match.group(10))
  site_x = int(match.group(11))
  site_y = int(match.group(12))

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': int(match.group(3)),
      'date_month': int(match.group(4)),
      'date_day_of_month': int(match.group(5)),
      'project': match.group(1),
      'magnification': '20x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(15),
      'timepoint': match.group(7),
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
        "/share/mikro/squid/Gentle_2022-12-21_15.04.42/B05_s3_x0_y1_Fluorescence_730_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro/squid/Colo/pilot5-DLD1_2023-03-08_16.19.17/I07_s6_x2_y1_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))
    

#