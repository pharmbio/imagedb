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
    The image handler returns actual images
    """
    def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """

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
            img_path = tif2png(channels, "/share/imagedb/image-cache")
        else:
            img_path = merge_channels(channels, "/share/imagedb/image-cache")

        logging.debug(img_path)

        self.write(open(img_path, 'rb').read())

        #self.write({'results': 'nothing here says anders again'})

class ThumbImageMergeHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    The image handler returns actual images
    """
    def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """

        logging.debug("Hello")

        channels = {'1': ch1}

        if not ch2 == 'undefined':
            channels.update({'2': ch2})

        if not ch3 == 'undefined':
            channels.update({'3': ch3})

        # rewrite paths to thumbs
        for (key, value) in channels.items():
            new_value = "/share/imagedb/thumbs/" + str(value).strip(".tif") + ".png"
            channels.update({key: new_value})

        logging.debug(channels)

        img_path = None
        if len(channels) == 1:
            img_path = channels['1']
        else:
            img_path = merge_channels(channels, "/share/imagedb/image-cache/")


        logging.debug(img_path)

        self.write(open(img_path, 'rb').read())

        #self.write({'results': 'nothing here says anders again'})

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

class ImageViewerHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method

    def get(self, image_url):

        logging.debug(self.request.query)

        self.render('image-viewer.html',
                     image_url=image_url)

