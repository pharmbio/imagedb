import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
# /share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_2_2_Fluorescence_638_nm_Ex.tiff
#


__pattern_path_and_file = re.compile('^'
                                     + '.*/squid/'  # any until /squid/
                                       + '(.*?)/'   # project (1)
                                       + '(.*?)_'    # plate (2)
                                       + '([0-9]{4})-([0-9]{2})-([0-9]{2})_(.*?)/' # date (yyyy, mm, dd) (3,4,5) and (time 6)
                                       + '([0-9]+)/'   # timepoint (7)
                                       + '([A-Z])([0-9]+)_'  # well (8,9)
                                       + '([0-9]+)_'   # site x (10)
                                       + '([0-9]+)_'   # site y (11)                                       
                                       + '(.*?)_' # imaging-type, e,g, Florecense (12)                                    
                                       + '([0-9]+)_nm_Ex' # Channel (wavelength) (13)
                                       + '(\..*)'      # Extension [14]
                                     ,
                                     re.IGNORECASE)  # Windows has case-insensitive filenames


def parse_path_and_file(path):
 # If something errors (file not parsable with this parser, then exception and return None)
 try:
  match = re.search(__pattern_path_and_file, path)

  logging.debug(f'match: {match}')
  
  if match is None:
    return None

  logging.debug(f'match: {match.groups()}')
  
  row = match.group(8)
  col = int(match.group(9))
  well = f'{row}{col:02}'

  channel_name = match.group(13)
  channels = ['405', '488', '561', '638', '730']
  channel_pos = channels.index(channel_name) + 1

  site_x = int(match.group(10))
  site_y = int(match.group(11))
  site = (site_x + 1) * (site_y + 1)

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': int(match.group(3)),
      'date_month': int(match.group(4)),
      'date_day_of_month': int(match.group(5)),
      'project': match.group(1),
      'magnification': '20x',
      'plate': match.group(2),
      'well': well,
      'wellsample': site,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(14),
      'timepoint': match.group(7),
      'channel_map_id': 2,
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
        "/share/mikro/squid/test/cell-density-martin-2022-09-23_2022-10-03_12-58-54.710491/0/D16_2_2_Fluorescence_638_nm_Ex.tiff")
    print("retval = " + str(retval))
