#!/usr/bin/env python3

import logging
import os
from PIL import Image
import cv2 as cv2
import subprocess

def colon_delimited_to_dict(inputString):
  # for each line in result, split into key-val on delimiter(colon)
  splitted = inputString.splitlines()
  result = {}
  for line in splitted:
    key_val = line.split(':')
    # only process lines with delimiter
    if len(key_val) == 2:
      result[key_val[0].strip()] = key_val[1].strip()

  return result

def read_tiff_info(path):
  result =  subprocess.run(['tiffinfo', path, "-i"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = str(result.stdout.decode())
  return colon_delimited_to_dict(output)

def makeThumb(path, thumbpath, overwrite):
  return makeThumb_opencv(path, thumbpath, overwrite)


def makeThumb_pillow(path, thumbdir):

  logging.debug("make thumb pillow")

  # create thumbfile name by joining thumbdir and orig name
  thumbfile = os.path.join(thumbdir, path.strip('/'))

  # replace old ext with png
  thumbfile_with_ext = os.path.splitext(thumbfile)[0]+'.png'

  # create thumb
  size = (120,120)
  im = Image.open(path)
  im.thumbnail(size)

  # create dir if needed
  directory = os.path.dirname(thumbfile_with_ext)
  if not os.path.exists(directory):
    os.makedirs(directory)

  # save thumb
  im.save(thumbfile_with_ext)


def makeThumb_opencv(path, thumbpath, overwrite):

  # replace old ext with png
  thumbpath_with_ext = os.path.splitext(thumbpath)[0]+'.png'

  if overwrite or (not os.path.isfile(thumbpath_with_ext)):

    # create thumb
    maxsize = (120,120)

    origimg = cv2.imread(path)
    imRes = cv2.resize(origimg, maxsize, interpolation = cv2.INTER_AREA)

    # create dir if needed
    directory = os.path.dirname(thumbpath_with_ext)
    if not os.path.exists(directory):
      os.makedirs(directory)

    # save thumb
    cv2.imwrite(thumbpath_with_ext, imRes)


if __name__ == '__main__':
  # test tiff-function
  result = read_tiff_info("/mnt/messi/tmp/WT-day7-40X-H2O2-Glu_B02_s3_w58595D8FD-A862-48FD-BE61-DDE35F0EDAC3.tif")
  print(result)

