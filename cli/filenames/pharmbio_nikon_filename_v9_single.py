import re
import os
import logging
import datetime

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
#
# /share/mikro2/nikon/spheroid-test/pilot10-spheroid-P1-9/Well-J18-z1-CONC.ome.tiff
#
#

__pattern_path_and_file = re.compile(r'^'
                                     r'.*/nikon/'      # any until /nikon/
                                     r'(.*?)/'         # project (1)
                                     r'(.*?)/'         # plate (2)
                                     r'(.*?/)?'        # Optional subdir (3), e.g. /single_images/
                                     r'([A-Z])([0-9]+)'# well (4,5)
                                     r'_S([0-9]+)'     # site (6)
                                     r'.*Channel_([0-9]+).*.ome' # channel (7)
                                     r'.*(\..*)'       # Extension [8]
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
  col = int(match.group(5))
  well = f'{row}{col:02d}'

  site = int(match.group(6))

  channel_name = match.group(7)
  channels = ['405', '446', '477', '545', '637']
  channel_pos = channels.index(channel_name) + 1

   # file creation timestamp
  c_time = os.path.getctime(path)
  date_create = datetime.datetime.fromtimestamp(c_time)

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': date_create.year,
      'date_month': date_create.month,
      'date_day_of_month': date_create.day,
      'project': match.group(1),
      'magnification': 'x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'z': 0,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(8),
      'timepoint': 1,
      'channel_map_id': 26,
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
        "/share/mikro2/nikon/cleo-test/P013730-live-cell-run3/K16_s2__Channel_446-er.ome.tiff")
    print("retval = " + str(retval))



