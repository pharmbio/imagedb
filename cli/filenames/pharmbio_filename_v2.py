import re
import os
import logging

# Adopted from: https://github.com/HASTE-project/haste-image-analysis-container2/tree/master/haste/image_analysis_container2/filenames
# file example
# /share/mikro/IMX/MDC_pharmbio/exp-WIDE/ACHN-20X-P009060/2019-02-19/51/ACHN-20X-P009060_G11_s9_w52B1ACE5F-5E6A-4AEC-B227-016795CE2297.tif
# or
# /share/mikro/IMX/MDC_pharmbio/PolinaG-U2OS/181212-U2OS-20X-BpA-HD-DB-high/2018-12-12/1/181212-U2OS-20X-BpA-HD-DB-high_E02_s7_w3_thumbCFB5B241-4E5B-4AB4-8861-A9B6E8F9FE00.tif

__pattern_path_and_file   = re.compile('^'
                            + '.*'        # any
                            + '([0-9]{4})-([0-9]{2})-([0-9]{2})' # date (yyyy, mm, dd) (1,2,3)
                            # TODO could check for optional timepoint here
                            # Now instead the timepoint version is being tested first
                            + '.*\/'      # any until last /
                            + '([0-9]{6}-)?' # maybe date here also (4)
                            + '([^-]+)'   # project-name (5)
                            + '-([^-]+)'  # magnification (6)
                            + '-([^_]+)'  # plate (7)
                            + '_([^_]+)'  # well (8)
                            + '_s([^_]+)'  # wellsample (9)
                            + '_w([0-9]+)' # Channel (color channel?) (10)
                            + '(_thumb)?'  # Thumbnail (11)
                            + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})'  # Image GUID [12]
                            + '(\.tiff?)?'  # Extension [13]
                            + '$'
                            ,
                            re.IGNORECASE)  # Windows has case-insensitive filenames

def parse_path_and_file(path):
  match = re.search(__pattern_path_and_file, path)

  if match is None:
    return None

  metadata = {
    'path': path,
    'filename': os.path.basename(path),
    'date_year': int(match.group(1)),
    'date_month': int(match.group(2)),
    'date_day_of_month': int(match.group(3)),
    'project': match.group(5),
    'magnification': match.group(6),
    'plate': match.group(7),
    'well': match.group(8),
    'wellsample': match.group(9),
    'channel': int(match.group(10)),
    'is_thumbnail': match.group(11) is not None,
    'guid': match.group(12),
    'extension': match.group(13),
    'timepoint': 1,
  }

  return metadata


