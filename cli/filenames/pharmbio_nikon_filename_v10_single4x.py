import re
import os
import logging
import datetime

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
#
# file example
#
# /share/mikro2/nikon/organoids/pilot3_withoutWGA_01BSA_4x/20251219_120847_437__WellO04.ome.tiff
#

__pattern_path_and_file = re.compile(
    r'^'
    r'.*/nikon/'                          # any until /nikon/
    r'(.*?)/'                             # project (1)
    r'(.*?)/'                             # plate (2)
    r'(.*?/)?'                            # Optional subdir (3), e.g. /single_images/
    r'([0-9]{4})([0-9]{2})([0-9]{2})'     # date (yyyy, mm, dd) (4,5,6)
    r'_[0-9]{6}'                          # time, e.g. 120847 (ignored)
    r'_[0-9]{3}'                          # milliseconds, e.g. 437 (ignored)
    r'__Well([A-Z])([0-9]{2})'            # well, e.g. WellO04 (7,8)
    r'\.ome'                              # fixed .ome part
    r'(.*(\..*))'                         # extension (e.g. .tiff) (9,10)
    ,
    re.IGNORECASE
)


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

  # No explicit z or channel in this format:
  # treat as single-plane, single-channel acquisition.
  z = 0
  site = 0
  channel_pos = 1


  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': int(match.group(4)),
      'date_month': int(match.group(5)),
      'date_day_of_month': int(match.group(6)),
      'project': match.group(1),
      'magnification': '4x',
      'plate': match.group(2),
      'plate_acq_name': path,
      'well': well,
      'wellsample': site,
      'z': z,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      'extension': match.group(9),
      'timepoint': 1,
      'channel_map_id': 44,
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
        "/share/mikro2/nikon/organoids/pilot3_withoutWGA_01BSA_4x/20251219_120847_437__WellO04.ome.tiff")
    print("retval = " + str(retval))

