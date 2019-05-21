import logging
import os
from PIL import Image
import cv2


def makeThumb(path):
  return makeThumb_opencv(path)

def makeThumb_pillow(path):
  thumbdir = "thumbs/"

  logging.debug("make thumb pillow")

  # create thumbfile name by joining thumbdir and orig name
  thumbfile = os.path.join(thumbdir, path)

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

def makeThumb_opencv(path):
  thumbdir = "thumbs/"

  # create thumbfile name by joining thumbdir and orig name
  thumbfile = os.path.join(thumbdir, path)

  # replace old ext with png
  thumbfile_with_ext = os.path.splitext(thumbfile)[0]+'.png'

  # create thumb
  maxsize = (120,120)
  imRes = cv2.resize(im, maxsize, interpolation=cv2.CV_INTER_AREA)

  # create dir if needed
  directory = os.path.dirname(thumbfile_with_ext)
  if not os.path.exists(directory):
    os.makedirs(directory)

  # save thumb
  cv2.imwrite(os.path.join(thumbfile_with_ext, file_name), cropped)
