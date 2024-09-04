import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_2_2_Fluorescence_638_nm_Ex.tiff
#


__pattern_path_and_file = re.compile(r'^'
                                     r'.*/squid/'         # any until /squid/
                                     r'(.*?)/'            # project (1)
                                     r'(.*?)_'            # plate (2)
                                     r'([0-9]{4})-([0-9]{2})-([0-9]{2})_(.*?)/' # date (yyyy, mm, dd) (3,4,5) and (time 6)
                                     r'(t[0-9]+/)?'       # optional timepoint (7)
                                     r'([A-Z])([0-9]+)_'  # well (8,9)
                                     r's([0-9]+)_'        # site index (10)
                                     r'x([0-9]+)_'        # site x (11)
                                     r'y([0-9]+)_'        # site y (12)
                                     r'(z[0-9]+_)?'       # optional site z (13)
                                     r'(.*?)_'            # imaging-type, e.g., Fluorescence, BF (14)
                                     r'(.*?)'             # wavelength or Light source (15)
                                     r'(\..*)'            # Extension (16)
                                     ,
                                     re.IGNORECASE)       # Windows has case-insensitive filenames



def parse_path_and_file(path):
 # If something errors (file not parsable with this parser, then exception and return None)
 try:
  match = re.search(__pattern_path_and_file, path)

  logging.debug(f'match: {match}')

  if match is None:
    return None

  project =  match.group(1)
  valid_projects = ['pelago300-bf']
  if project not in (valid_projects):
    return None

  logging.debug(f'match: {match.groups() }')

  tp = match.group(7)
  if tp:
    timepoint = tp[1:-1] # remove t and /
  else:
    timepoint = 0

  row = match.group(8)
  col = match.group(9)
  well = f'{row}{col}'

  image_type = match.group(14)
  logging.debug(image_type)
  if image_type == 'Fluorescence':
    channel_name = match.group(15).split('_nm')[0]

    channels_v1 = ['405', '488', '561', '638', '730']
    channels_v2 = ['385', '470', '510', '560', '640']

    if channel_name in channels_v1:
      channels = channels_v1
    elif channel_name in channels_v2:
      channels = channels_v2
    channel_ix = channels.index(channel_name)
    channel_pos = (channel_ix + 1) * 3 + 1

  elif image_type == 'BF':
    channel_pos = 1

  channel_map_id = 30

  site = int(match.group(10))
  site_x = int(match.group(11))
  site_y = int(match.group(12))

  z_val = match.group(13)
  if z_val:
    z = int(z_val[1:-1]) # remove leading z and trailing _
  else:
    z = 0

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': match.group(3),
      'date_month': match.group(4),
      'date_day_of_month': match.group(5),
      'project': project,
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
        "/share/mikro2/squid/pelago300-bf/P104636_pelago300-bf_HepG2_48h_B1_P01_L1_2024-03-14_10.45.33/K09_s4_x0_y1_z2_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/squid/pelago300-bf/P104636_pelago300-bf_HepG2_48h_B1_P01_L1_2024-03-14_10.45.33/K09_s4_x0_y1_z0_BF_LED_matrix_full.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/squid/pelago300-bf/P104636_pelago300-bf_HepG2_48h_B1_P01_L1_2024-03-14_10.45.33/K09_s4_x0_y1_z0_Fluorescence_405_nm_Ex.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/squid/pelago300-bf/P104636_pelago300-bf_HepG2_48h_B1_P01_L1_2024-03-14_10.45.33/K09_s4_x0_y1_z0_Fluorescence_488_nm_Ex.tiff")
    print("retval = " + str(retval))







