import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
# file example
# /share/mikro/IMX/MDC_pharmbio/exp-TimeLapse/A549-20X-DB-HD-BpA-pilot1/2019-03-27/84/TimePoint_1/A549-20X-DB-HD-BpA-pilot1_B02_s1_thumb1E64F2F4-E1E8-410C-9891-A491D91FC73C.tif

__pattern_path_and_file   = re.compile('^'
                            + '.*'        # any
                            + 'MDC_pharmbio/(.*?)/' # project (1)
                            + '(.*?)/' # plate (2)
                            + '([0-9]{4})-([0-9]{2})-([0-9]{2})' # date (yyyy, mm, dd) (3,4,5)
                            + '.*'        # Any
                            + 'TimePoint_([^\/]+)' # Timepoint (6)
                            + '\/([^-]+)' # cell-line-name (7)
                            + '-([^-]+)'  # magnification (8)
                            + '-([^_]+)'  # plate-short (9)
                            + '_([^_]+)'  # well (10)
                            + '_s([0-9])'  # wellsample (11) # OBS! Only 9 wellsamples
                            + '(_w[0-9])?' # optional channel (12)
                            + '(_thumb)?'  # Thumbnail (11)
                            + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})'  # Image GUID [12]
                            + '(\.tiff?)?'  # Extension [13]
                            + '$'
                            ,
                            re.IGNORECASE)  # Windows has case-insensitive filenames

def parse_path_and_file(path):
  match = re.search(__pattern_path_and_file, path)

  #logging.debug(match)

  if match is None:
    return None

  # parse channel
  # first set default
  channel = 1
  if match.group(12):
    # remove _w from match
    channel = match.group(12)[1]


  metadata = {
    'path': path,
    'filename': os.path.basename(path),
    'date_year': int(match.group(3)),
    'date_month': int(match.group(4)),
    'date_day_of_month': int(match.group(5)),
    'timepoint': int(match.group(6)),
    'project': match.group(1),
    'magnification': match.group(8),
    'plate': match.group(2),
    'well': match.group(10),
    'wellsample': match.group(11),
    'channel': channel,
    'is_thumbnail': match.group(13) is not None,
    'guid': match.group(14),
    'extension': match.group(15),
  }

  return metadata

if __name__ == '__main__':
    # Testparse
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/exp-TimeLapse/A549-20X-DB-HD-BpA-pilot1/2019-03-27/84/TimePoint_1/A549-20X-DB-HD-BpA-pilot1_B02_s1_w1_thumb1E64F2F4-E1E8-410C-9891-A491D91FC73C.tif")
    print("retval = " + str(retval))


