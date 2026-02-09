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

__pattern_path_and_file = re.compile(
    r'^'
    r'.*/nikon/'             # any until /nikon/
    r'(.*?)/'                # project (1)
    r'(.*?)/'                # plate (2)
    r'(?:([0-9]{4})([0-9]{2})([0-9]{2})_[0-9]{6}_[0-9]{3}/)?'  # Optional date folder: YYYYMMDD_HHMMSS_mmm (3,4,5)
    r'(?:([0-9]+x)[^/]*/)?'  # Optional magnification subdir (6), e.g. 20x/, 4x/, 20x_processed/
    r'Well-([A-Z])([0-9]+)'  # well (7,8)
    # Two alternatives:
    #  1) Full pattern with z and channel, e.g. Well-E19-z7-CONC.ome.tiff
    #  2) Short pattern without z/channel but with extra text after well, e.g. Well-N23_WellN23.ome.tiff
    r'(?:-z([0-9]+)-(.*)\.ome(.*(\..*))|_.*\.ome()()(.*(\..*)))'
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

  # z is optional in some filename variants
  if match.group(9):
      z = int(match.group(9))
  else:
      z = 0
  site = 0

  # Channel name is optional; if missing, fall back to a default single channel
  channel_name = match.group(10)
  if channel_name:
      channels = ['MITO', 'PHAandWGA', 'HOECHST', 'SYTO', 'CONC']
      channel_pos = channels.index(channel_name) + 1
  else:
      channel_pos = 1

  # Optional magnification captured from the path (group 6), e.g. "20x"
  magnification = match.group(6) if match.group(6) else 'x'

  # Parse date from date folder (groups 3–5) if present, otherwise fall back to file creation time
  if match.group(3) and match.group(4) and match.group(5):
      year = int(match.group(3))
      month = int(match.group(4))
      day = int(match.group(5))
  else:
      c_time = os.path.getctime(path)
      date_create = datetime.datetime.fromtimestamp(c_time)
      year = date_create.year
      month = date_create.month
      day = date_create.day

  # Plate acquisition name: if a date folder exists, use plate + "_" + <actual date-folder> +
  # optional "_" + magnification subdir. Otherwise, fall back to the full path (legacy behaviour).
  plate = match.group(2)
  if match.group(3):
      magnification_dir = ''
      if match.group(6):
          magnification_dir = os.path.basename(os.path.dirname(path))

      # Actual date folder name between plate and magnification/filename
      if magnification_dir:
          date_folder = os.path.basename(os.path.dirname(os.path.dirname(path)))
      else:
          date_folder = os.path.basename(os.path.dirname(path))

      if magnification_dir:
          plate_acq_name = f'{plate}_{date_folder}_{magnification_dir}'
      else:
          plate_acq_name = f'{plate}_{date_folder}'
  else:
      plate_acq_name = path

  metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': year,
      'date_month': month,
      'date_day_of_month': day,
      'project': match.group(1),
      'magnification': magnification,
      'plate': plate,
      'plate_acq_name': plate_acq_name,
      'well': well,
      'wellsample': site,
      'z': z,
      'channel': channel_pos,
      'is_thumbnail': False,
      'guid': None,
      # Extension may come from different capture groups depending on which
      # filename variant matched (with or without z/channel).
      'extension': match.group(11) if match.group(11) else match.group(15),
      'timepoint': 1,
      # Use different channel maps depending on whether we have
      # an explicit channel or not.
      'channel_map_id': 25 if channel_name else 44,
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


    # retval = parse_path_and_file(
    #     "/share/mikro2/nikon/spheroid-test/pilot10-spheroid-P1-9/Well-J18-z1-CONC.ome.tiff")
    # print("retval = " + str(retval))

    # retval = parse_path_and_file(
    #     "/share/mikro2/nikon/Erica/Neuroblastoma/SiMaSpheres48hBoNT-A-C/Well-P01-z11-PHAandWGA.ome.tiff")
    # print("retval = " + str(retval))

    # retval = parse_path_and_file(
    #     "/share/mikro2/nikon/organoids/test_storage/20260115_164715_750/20x/Well-J12-z4-SYTO.ome.tiff")
    # print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/nikon/organoids/pilot3_withoutWGA_01BSA_run2/20260115_165013_732/20x/Well-E19-z7-CONC.ome.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/nikon/organoids/pilot3_withoutWGA_01BSA_run2/20260115_165013_732/4x/Well-N23_WellN23.ome.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/nikon/organoids/pilot3_withoutWGA_01BSA_run2/20260115_165013_732/20x_processed/Well-E19-z7-CONC.ome.tiff")
    print("retval = " + str(retval))

    retval = parse_path_and_file(
        "/share/mikro2/nikon/spheroids-revsion/colo8-sectant-P2-stained-six-v2/Well-P18-z15-HOECHST.ome.tiff")
    print("retval = " + str(retval))






