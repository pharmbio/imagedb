#!/usr/bin/env python3
"""
This file has the ImageHandler, it gets request for images and returns images.
"""

import logging
import json

import tornado.web
from imageutils import (merge_channels, tif2png)
import settings as imgdb_settings


class ImageMergeHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The image handler returns actual images, not just links
    """
    async def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """

        logging.info("Inside async")

        logging.debug("ch1:" + ch1)
        logging.debug("ch2:" + ch2)
        logging.debug("ch3:" + ch3)

        channels= {'1':ch1}

        if not ch2 == 'undefined':
            channels.update({'2': ch2})

        if not ch3 == 'undefined':
            channels.update({'3': ch3})


        # rewrite paths to full images
        IMAGES_ROOT_FOLDER = imgdb_settings.IMAGES_ROOT_FOLDER
        for (key, value) in channels.items():
            new_value = IMAGES_ROOT_FOLDER + str(value)
            channels.update({key: new_value})

        logging.debug(channels)

        img_path = None
        if len(channels) == 1:
            img_path = tif2png(channels, imgdb_settings.IMAGES_CACHE_FOLDER)
        else:
            img_path = await merge_channels(channels, imgdb_settings.IMAGES_CACHE_FOLDER)

        logging.debug(img_path)

        self.set_header("Content-type", "image/png")
        self.write(open(img_path, 'rb').read())


class ThumbImageMergeHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The image handler returns actual images, not just links
    """
    async def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """

        channels = {'1': ch1}

        if not ch2 == 'undefined':
            channels.update({'2': ch2})

        if not ch3 == 'undefined':
            channels.update({'3': ch3})

        # rewrite paths to thumbs
        for (key, value) in channels.items():
 
            # To be replaced with "removesuffix in python 3.9"
            if value.endswith('.tif'):
                value = value[:-(len('.tif'))]
                value = value + ".png"

            new_value = imgdb_settings.IMAGES_THUMB_FOLDER + "/" + value
            channels.update({key: new_value})

        logging.debug(channels)

        img_path = None
        if len(channels) == 1:
            img_path = channels['1']
        else:
            img_path = await merge_channels(channels, imgdb_settings.IMAGES_CACHE_FOLDER)

        logging.debug(img_path)

        self.set_header("Content-type", "image/png")
        self.write(open(img_path, 'rb').read())


class ImageMergeHandlerGetURL(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The query handler handles form posts and returns a list of hits.
    """
    def post(self):
        """Handles POST requests.
        """
        logging.info("Hej")
        logging.info(self.request)
        logging.info(tornado.escape.json_decode(self.request.body))
        try:
            form_data = self.request.body_arguments

        except Exception as e:
            logging.error("Exception: %s", e)
            form_data = []

        logging.info("Hej")
        logging.info("form_data:" + str(form_data))

        self.finish({'results':'nothing here says anderd'})



