#!/usr/bin/env python3
"""
This file has the ImageHandler, it gets request for images and returns images.
"""

import logging
import json
import os

import tornado.web
import tornado.escape
from imageutils import (merge_channels, tif2png)
import settings as imgdb_settings


class ImageMergeHandler(tornado.web.StaticFileHandler): #pylint: disable=abstract-method
    """
    The image handler returns actual images, not just links
    """
    async def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """
        normalize_arg = self.get_query_argument('normalize', None) or '0'
        normalization = normalize_arg.lower() in ('1', 'true', 'yes')
        equalize_arg = self.get_query_argument('equalize', None) or '0'
        equalize = equalize_arg.lower() in ('1', 'true', 'yes')

        logging.debug("ch1:" + ch1)
        logging.debug("ch2:" + ch2)
        logging.debug("ch3:" + ch3)

        overwrite_cache = False
        if "nikon" in ch1:
            normalization = True
            overwrite_cache = True

        channels= {'1':ch1}

        if not ch2 == 'undefined':
            channels.update({'2': ch2})

        if not ch3 == 'undefined':
            channels.update({'3': ch3})

        logging.debug(channels)

        img_path = None
        if len(channels) == 1:
            img_path = tif2png(channels, imgdb_settings.IMAGES_CACHE_FOLDER,overwrite_existing=overwrite_cache, normalize=normalization)
        else:
            img_path = await merge_channels(channels,
                                            imgdb_settings.IMAGES_CACHE_FOLDER,
                                            overwrite_existing=overwrite_cache,
                                            normalization=normalization,
                                            equalize=equalize)

        #logging.debug(img_path)

        logging.info("done merge")

        # Serve via StaticFileHandler
        rel_path = os.path.relpath(img_path, self.root)
        await super().get(rel_path)


class ThumbImageMergeHandler(tornado.web.StaticFileHandler): #pylint: disable=abstract-method
    """
    The image handler returns actual images, not just links
    """
    async def get(self, ch1, ch2, ch3):
        """Handles GET requests.
        """
        logging.debug("Inside ThumbImageMergeHandler")

        normalize_arg = self.get_query_argument('normalize', None) or '0'
        normalization = normalize_arg.lower() in ('1', 'true', 'yes')
        equalize_arg = self.get_query_argument('equalize', None) or '0'
        equalize = equalize_arg.lower() in ('1', 'true', 'yes')

        channels = {'1': ch1}

        if not ch2 == 'undefined':
            channels.update({'2': ch2})

        if not ch3 == 'undefined':
            channels.update({'3': ch3})

        # rewrite paths to thumbs
        for (key, value) in channels.items():
            value = os.path.splitext(value)[0]+'.png'
            new_value = imgdb_settings.IMAGES_THUMB_FOLDER + "/" + value
            channels.update({key: new_value})

        # logging.debug(channels)

        img_path = None
        if len(channels) == 1:
            img_path = channels['1']
        else:
            img_path = await merge_channels(channels, imgdb_settings.IMAGES_CACHE_FOLDER, normalization=normalization, equalize=equalize)

         # logging.debug(img_path)

        # Serve via StaticFileHandler
        rel_path = os.path.relpath(img_path, self.root)  # self.root == COMMON_ROOT
        await super().get(rel_path)


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



