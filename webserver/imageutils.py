#!/usr/bin/env python3
import hashlib
import logging
import cv2 as cv2
import numpy as np
import os

from fileutils import create_merged_filepath

def get_thumb_path(channels):

    IMGAGES_ROOT_FOLDER = "share/mikro/IMX/MDC Polina Georgiev/"
    thumb_path = os.path.join(IMGAGES_ROOT_FOLDER, channels.get('1'))

    # TODO check if file exists already

    return thumb_path

def merge_channels(channels, outdir):

    logging.debug(channels)

    for k, v in channels.items():
      logging.info("key" + str(k))
      logging.info("value" + str(v))

    logging.info("1 = " + channels.get('1'))
    IMGAGES_ROOT_FOLDER = "/share/mikro/IMX/MDC Polina Georgiev/"
    ch_1_path = os.path.join(IMGAGES_ROOT_FOLDER, channels.get('1'))
    ch_2_path = os.path.join(IMGAGES_ROOT_FOLDER, channels.get('2'))
    ch_3_path = os.path.join(IMGAGES_ROOT_FOLDER, channels.get('3'))

    merged_file = create_merged_filepath(outdir, ch_1_path, ch_2_path, ch_3_path)

    # TODO check if file exists already

    r = cv2.imread(ch_1_path, 0)
    g = cv2.imread(ch_2_path, 0)
    b = cv2.imread(ch_3_path, 0)
    if r is None or g is None or b is None:
        raise Exception('image read returned NONE')

    # Create a blank image that has three channels
    # and the same number of pixels as your original input
    merged_img = np.zeros((r.shape[0], r.shape[1], 3))

    # Add the channels to the needed image one by one
    # opencv uses bgr format instead of rgb
    merged_img[:, :, 0] = b
    merged_img[:, :, 1] = g
    merged_img[:, :, 2] = r

    # Save the merged image
    if not os.path.exists(os.path.dirname(merged_file)):
        os.makedirs(os.path.dirname(merged_file))
    cv2.imwrite(merged_file, merged_img)

    return merged_file


## main entry for testing
#logging.getLogger().setLevel(logging.DEBUG)
#
#channels = {
#            '1': '/home/anders/projekt/pharmbio/imageDB/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/MCF7-20X-P009086/2019-03-06/56/MCF7-20X-P009086_D05_s2_w1868FF30C-4AD3-4582-86C8-6CA2FF34C056.png',
#            '2': '/home/anders/projekt/pharmbio/imageDB/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/MCF7-20X-P009086/2019-03-06/56/MCF7-20X-P009086_D05_s2_w2B64CD11B-6B9A-431E-B330-0C9E402FC658.png',
#            '3': '/home/anders/projekt/pharmbio/imageDB/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/MCF7-20X-P009086/2019-03-06/56/MCF7-20X-P009086_D05_s2_w30ECE7E78-A619-41C4-8883-B6DCC14A72D2.png',
#            '4': '/home/anders/projekt/pharmbio/imageDB/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/MCF7-20X-P009086/2019-03-06/56/MCF7-20X-P009086_D05_s2_w4007FAC31-741D-4903-BDBC-45B9EE337568.png',
#            '5': '/home/anders/projekt/pharmbio/imageDB/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/exp-WIDE/MCF7-20X-P009086/2019-03-06/56/MCF7-20X-P009086_D05_s2_w5DB657BF2-7497-430C-9A3E-5764F7EC913A.png'
#            }
#
#outdir = '/home/anders/projekt/pharmbio/imageDB/share/imagedb/image-cache/'
#
#merged_filen = merge_channels(channels, outdir)
