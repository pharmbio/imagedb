import re
import os
import logging

# file examples
# CancerTherapyData/Bartek/1_ATXN2/2_CETSA pilot screen/20190904 part2/Bartek 384w BD 10x/
#             Bartek 384w BD 10x_CETSApilot2_11_2019.09.06.05.07.57/B - 02(fld 1 wv Cy3 - Cy3).tif
# or
#  ........./D - 05(wv TL-Brightfield - Cy3).tif
#
# Katie/Data and Results/PR97 inducible cells line/HTS batch 2 08_04_19/
#                      U2OS 384 BD Falcon 4x_Hoechst_HTS/U2OS 384 BD Falcon 4x_Hoechst_HTS_72hrs_1/A - 03(wv DAPI - DAPI).tif
#
# /A - 01(fld 1 wv Cy5 - Cy5).tif


def parse_path_and_file(path):

  # If something errors (file not parsable with this parser, then exception and return None)
  try:

    # project
    match = re.search('/share/mikro/(.+?)/', path)
    project = match.group(1)

    # path
    match = re.search('/share/mikro/.+?/(.*)/', path)
    if match is None:
      return None
    plate = match.group(1)

    # well
    match = re.search('.*/(.+?) - ([0-9][0-9])', path)
    well = match.group(1) + match.group(2)
    # workaround TODO remove
    if "_" in well:
      logging.warn("well=" + well)
      well = well.split('_')[1]

    # site
    match = re.search('.*\(fld ([0-9]) ', path)
    if match is None:
      site = 1
    else:
      site = match.group(1)
   
    # channel
    match = re.search('.*wv (.+) - ', path)
    channel_name = match.group(1)
    channel_names = ['FITC',
                     'Cy3',
                     'Cy5',
                     'DAPI',
                     'TL-Brightfield']
    channel = channel_names.index(channel_name)

    # logging
    logging.debug("project" + project)
    logging.debug("plate" + plate)
    logging.debug("well" + well)
    logging.debug("field" + str(site))
    logging.debug("channel" + str(channel))

    metadata = {
      'path': path,
      'filename': os.path.basename(path),
      'date_year': 0,
      'date_month': 0,
      'date_day_of_month': 0,
      'project': project,
      'magnification': '?x',
      'plate': plate,
      'well': well,
      'wellsample': site,
      'channel': channel,
      'is_thumbnail': False,
      'guid': 'no-guid',
      'extension': ".tif",
      'timepoint': 1,
    }

    return metadata

  except:
    logging.exception("could not parse")
    return None


if __name__ == '__main__':
    # Testparse
    retval = parse_path_and_file("/share/mikro/Jordi/IN Cell test/384 wellplate BD Falcon black 4x DAPI/384 wellplate BD Falcon black 4x DAPI_1/B - 02(wv DAPI - DAPI).tif")
    print(str(retval))