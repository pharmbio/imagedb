import re
import os
import logging
import datetime

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
#
# nikon/spheroid-test/pilot10-spheroid-P1-8/20230609_143142_722__PointB02_0000_ZStack0015_ChannelSYTO_Spheroid.ome.tiff
#
#

__pattern_path_and_file = re.compile('^'
                                     + '.*/nikon/'      # any until /nikon/
                                       + '(.*?)/'       # project (1)
                                       + '(.*?)/'       # plate (2)
                                       + '(.*?/)?'                        # Optional subdir (3), e.g. /single_images/
                                       + '([0-9]{4})([0-9]{2})([0-9]{2})' # date (yyyy, mm, dd) (4,5,6)
                                       + '_.*Point([A-Z])([0-9]+)' #  well (7,8)
                                       + '_.*ZStack([0-9]+)' #  z (9)
                                       + '_Channel(.*)_Spheroid.ome' #  channel (10)
                                       + '.*(\..*)'                 # Extension [11]
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

  row = match.group(7)
  col = int(match.group(8))
  well = f'{row}{col:02d}'

  z = int(match.group(9))
  site = z

  channel_name = match.group(10)
  channels = ['MITO', 'PHAandWGA', 'SYTO', 'HOECHST']
  channel_pos = channels.index(channel_name) + 1


  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': int(match.group(4)),
      'date_month': int(match.group(5)),
      'date_day_of_month': int(match.group(6)),
      'project': match.group(1),
      'magnification': 'x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'z': z,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(11),
      'timepoint': 1,
      'channel_map_id': 24,
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
        "/share/mikro2/nikon/spheroid-test/pilot10-spheroid-P1-8/20230609_143142_722__PointB02_0000_ZStack0015_ChannelSYTO_Spheroid.ome.tiff")
    print("retval = " + str(retval))



