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
                            + 'MDC_pharmbio/(.*?)/' # project (1)
                            + '(.*?)/' # plate (2)
                            + '([0-9]{4})-([0-9]{2})-([0-9]{2})' # date (yyyy, mm, dd) (3,4,5)
                            # TODO could check for optional timepoint here
                            # Now instead the timepoint version is being tested first
                            + '.*\/'      # any until last /
                            + '([0-9]{6}-)?' # maybe date here also (6)
                            + '([^-]+)'   # project-name (7)
                            + '-([^-]+)'  # magnification (8)
                            + '-([^_]+)'  # plate-short (9)
                            + '_([^_]+)'  # well (10)
                            + '_s([^_]+)'  # wellsample (11)
                            + '_w([0-9]+)' # Channel (color channel?) (12)
                            + '(_thumb)?'  # Thumbnail (13)
                            + '([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})'  # Image GUID [14]
                            + '(\.tiff?)?'  # Extension [15]
                            + '$'
                            ,
                            re.IGNORECASE)  # Windows has case-insensitive filenames

def parse_path_and_file(path):
 # If something errors (file not parsable with this parser, then exception and return None)
 try:
  match = re.search(__pattern_path_and_file, path)

  if match is None:
    return None

  metadata = {
    'path': path,
    'filename': os.path.basename(path),
    'date_year': int(match.group(3)),
    'date_month': int(match.group(4)),
    'date_day_of_month': int(match.group(5)),
    'project': match.group(1),
    'magnification': match.group(8),
    'plate': match.group(2),
    'plate_acq_name': path,
    'well': match.group(10),
    'wellsample': match.group(11),
    'channel': int(match.group(12)),
    'is_thumbnail': match.group(13) is not None,
    'guid': match.group(14),
    'extension': match.group(15),
    'timepoint': 1,
    'channel_map_id': 1,
    'microscope': "ImageXpress",
    'parser': os.path.basename(__file__)
  }

  return metadata
 except:
    logging.debug("could not parse filename with this parser")
    return None

if __name__ == '__main__':
        #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
  
    # Testparse
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/PolinaG-U2OS/181212-U2OS-20X-BpA-HD-DB-high/2018-12-12/1/181212-U2OS-20X-BpA-HD-DB-high_E02_s7_w3_thumbCFB5B241-4E5B-4AB4-8861-A9B6E8F9FE00.tif")
    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015232-A549-48h-P1-L3-r1/2022-01-31/906/kinase378-v1-FA-P015232-A549-48h-P1-L3-r1_B02_s3_w5F56592B1-3477-465C-B118-87465E0163A1.tif")
    print("retval = " + str(retval))

    retval = parse_path_and_file("/share/mikro/IMX/MDC_pharmbio/kinase378-v1/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1/2022-03-11/965/kinase378-v1-FA-P015240-HOG-48h-P2-L5-r1_B02_s8_w3_thumb3DF2C4AE-602A-46F6-84B2-9B31D1981B60.tif")
    print("retval = " + str(retval))


