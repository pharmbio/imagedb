#!/usr/bin/env python3
import hashlib
import logging
import cv2 as cv2
from PIL import Image
import numpy as np
import os
import settings as imgdb_settings

from fileutils import create_merged_filepath, create_pngconverted_filepath

def tif2png(channels, outdir, overwrite_existing=False):
    return tif2png_opencv(channels, outdir, overwrite_existing )

def tif2png_opencv(channels, outdir, overwrite_existing=False):

    #logging.debug(channels)

    tiff_path = channels.get('1')

    png_path = create_pngconverted_filepath(outdir, tiff_path)

    #logging.debug('merged_file=' + str(png_path))


    # Check if file exists already
    if not os.path.isfile(png_path) or overwrite_existing:

        img = cv2.imread(tiff_path)

        # Save the merged image
        if not os.path.exists(os.path.dirname(png_path)):
            os.makedirs(os.path.dirname(png_path))
        cv2.imwrite(png_path, img)

    return png_path

def tif2png_pillow(channels, outdir, overwrite_existing=False):

    #logging.debug(channels)

    tiff_path = channels.get('1')

    png_path = create_pngconverted_filepath(outdir, tiff_path)

    #logging.debug('merged_file=' + str(png_path))


    # Check if file exists already
    if not os.path.isfile(png_path) or overwrite_existing:

        img = Image.open(tiff_path)

        # Save the merged image
        if not os.path.exists(os.path.dirname(png_path)):
            os.makedirs(os.path.dirname(png_path))
        img.save(png_path)

    return png_path

def count_unique_colors(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    img = Image.open(image_path)
    return len(np.unique(image))

def auto_white_balance(im, p=.6):
    '''https://stackoverflow.com/questions/48268068/how-do-i-do-the-equivalent-of-gimps-colors-auto-white-balance-in-python-fu'''
    '''Stretch each channel histogram to same percentile as mean.'''

    # get mean values
    p0, p1 = np.percentile(im, p), np.percentile(im, 100-p)

    for i in range(3):
        ch = im[:,:,i]
        # get channel values
        pc0, pc1 = np.percentile(ch, p), np.percentile(ch, 100-p)
        # stretch channel to same range as mean
        ch = (p1 - p0) * (ch - pc0) / (pc1 - pc0) + p0
        im[:,:,i] = ch

    return im

async def merge_channels(channels, outdir, overwrite_existing=False):
    ''' For now in image veiewer read image as 8 bit grayscale cv2.IMREAD_GRAYSCALE
        instead of 16 bit cv2.IMREAD_UNCHANGED (can't see difference in img viewer and saves 90% of size)
        and also dont create np array with np.uint16'''

    #logging.info("Inside async merge")

 #   for k, v in channels.items():
 #     logging.debug("key" + str(k))
 #     logging.debug("value" + str(v))

    # TODO change this to more generalized merge than three channels
    paths = [channels.get('1')]
    if len(channels) > 1:
        paths.append(channels.get('2'))
    if len(channels) > 2:
        paths.append(channels.get('3'))

    merged_file = create_merged_filepath(outdir, paths)

    #logging.debug('merged_file=' + str(merged_file))

    # Check if file exists already
    if overwrite_existing or not os.path.isfile(merged_file):

        logging.debug("list len =" + str(len(paths)))

        # Read images, raise exceptions manually since opencv is silent if file doesn't exist
        b = cv2.imread(paths[0],  cv2.IMREAD_GRAYSCALE)
        if b is None:
            raise Exception('image read returned NONE, path: ' + str(paths[0]))

        # Create a blank image that has three channels
        # and the same number of pixels as your original input
        merged_img = np.zeros((b.shape[0], b.shape[1], 3)) #, np.uint16)

        # Add the channels to the needed image one by one
        # opencv uses bgr format instead of rgb
        merged_img[:, :, 0] = b

        if len(paths) > 1:
            r = cv2.imread(paths[1], cv2.IMREAD_GRAYSCALE)
            if r is None:
                raise Exception('image read returned NONE, path: ' + str(paths[1]))

            merged_img[:, :, 2] = r

        if len(channels) > 2:
            g = cv2.imread(paths[2], cv2.IMREAD_GRAYSCALE)
            if g is None:
                raise Exception('image read returned NONE, path: ' + str(paths[2]))

            merged_img[:, :, 1] = g

        # normalize colors
        merged_img = auto_white_balance(merged_img)

        # Save the merged image
        if not os.path.exists(os.path.dirname(merged_file)):
            os.makedirs(os.path.dirname(merged_file))
        cv2.imwrite(merged_file, merged_img)

        #logging.info("img unique:" + str(len(np.unique(merged_img))))

    #logging.info("Unique colors:" + str(count_unique_colors(merged_file)))


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
