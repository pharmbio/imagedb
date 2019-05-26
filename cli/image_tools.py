#!/usr/bin/env python3

import logging
import os
from PIL import Image
import cv2 as cv2


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
