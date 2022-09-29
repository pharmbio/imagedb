#!/usr/bin/env python3

from ast import Not
import logging
import os
from PIL import Image
import cv2 as cv2
import subprocess
import time
import glob
from pathlib import Path

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

def tif2png_recursive(in_path, out_path):
  exts = ['.tif', '.tiff']
  files = [p for p in Path(in_path).rglob('*') if p.suffix in exts]

  for file in files:
    filename = str(file)
    if not 'thumb' in filename:
      out_filename = filename.replace(in_path, out_path).replace(file.suffix, '.png')
      if not os.path.isfile(out_filename):
        any2png(filename, out_filename)

def any2lzw(in_path, out_path):

  #logging.debug("Inside img2png")
  #logging.debug("in_path:" + str(in_path))
  #logging.debug("out_path:" + str(out_path))

  os.makedirs(os.path.dirname(out_path),exist_ok=True)
  start = time.time()
  cv2_any2png(in_path, out_path)
  cv2_any2lzw(in_path, out_path)

  logging.debug("time:" + str(time.time() - start))
  #logging.debug("orig:" + str(os.path.getsize(in_path)))
  #logging.debug("new :" + str(os.path.getsize(out_path)))

  # start = time.time()
  # cv2.imread(out_path)
  # logging.info("open:" + str(time.time() - start))


  logging.info("Done img2png")

def any2png(in_path, out_path, compression_level=4):
  os.makedirs(os.path.dirname(out_path),exist_ok=True)
  cv2_any2png(in_path, out_path, compression_level)

def cv2_any2png(in_path, out_path, compression=4):
  orig_img = cv2.imread(in_path)
  cv2.imwrite(out_path, orig_img, [cv2.IMWRITE_PNG_COMPRESSION, compression])

def cv2_any2lzw(in_path, out_path, compression=6):
  orig_img = cv2.imread(in_path)
  cv2.imwrite(out_path, orig_img, [cv2.IMWRITE_TIFF_COMPRESSION])





if __name__ == '__main__':

  #
  # Configure logging
  #
  logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.DEBUG)
  rootLogger = logging.getLogger()

  #imgfile = "/share/mikro/IMX/MDC_pharmbio/JUMP-v1/P013841-GR-U2OS-50h-L1/2021-10-04/801/P013841-GR-U2OS-50h-L1_C03_s1_w1D25AE1A3-B911-4E54-9B3F-06B19BD45236.tif"
  #imgpath = "/share/mikro/IMX/MDC_pharmbio/dicot/"


  orig_root = '/share/mikro/'
  new_root = '/share/mikro-compressed/'

  in_path = "/share/mikro/IMX/MDC_pharmbio/dicot/"
  out_path = in_path.replace(orig_root, new_root)

  # img2png(in_path, out_path)
  tif2png_recursive(in_path, out_path)



