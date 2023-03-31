import re
import os
import logging
import datetime

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
#
# /share/mikro/nikon/U20S-test/u2os-test/20230303_200618_678__WellP24_ChannelMITO,PHAandWGA,SYTO,CONC,HOECHST_Seq0360xy9c5.tif
#
#

__pattern_path_and_file = re.compile('^'
                                     + '.*/nikon/'      # any until /nikon/
                                       + '(.*?)/'       # project (1)
                                       + '(.*?)/'       # plate (2)
                                       + '(.*?/)?'   # Optional subdir (3), e.g. /single_images/ 
                                       + '.*?_Wells([A-Z])([0-9]+)_'         # well (4,5)
                                       + 'Points([0-9]+)'       #  site (6)
                                       + 'c([0-9]+)' #  channel (7)
                                       + '.*(\..*)'                 # Extension [8]
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

  row = match.group(4)
  col = match.group(5)
  well = f'{row}{col}'

  site = int(match.group(6))

  channel_pos = int(match.group(7))
  
  # file creation timestamp in float
  c_time = os.path.getctime(path)

  date_create = datetime.datetime.fromtimestamp(c_time)
  print('Created on:', date_create)

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': 0,
      'date_month': 0,
      'date_day_of_month': 0,
      'project': match.group(1),
      'magnification': '20x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(8),
      'timepoint': 1,
      'channel_map_id': 19,
      'microscope': "nikon",
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
        "/share/mikro2/nikon/RMS-test/batch4-RH30-test2/single_images/RMS-P01_WellsI10_Points00c5.tif")
    print("retval = " + str(retval))