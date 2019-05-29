#!/usr/bin/env python3
"""
Simple Tornado server.
"""

import os
import logging
import tornado
import tornado.web

from handlers.query_handler import QueryHandler, ListImagesQueryHandler
from handlers.image_handlers import (ImageViewerHandler,
                                     ImageMergeHandler,
                                     ThumbImageMergeHandler)
import settings as imgdb_settings

SETTINGS = {
    'debug': True,
    'develop': True,
    'template_path':'templates/',
    'xsrf_cookies': False, # Anders disabled this - TODO enable again
    'cookie_secret':'some-really-secret-secret',
    # static path is defined in handler below
}

class DefaultTemplateHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    This is the main handler of the application
    """
    def get(self):
        """Renders the index file as a template without arguments.
        """
        logging.debug(self.request.path)

        self.render(self.request.path.strip('/'))
        #self.render('index.html')

class IndexTemplateHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method
    """
    This is the main handler of the application, which serves the index.html template
    """
    def get(self):

        self.render('index.html')


ROUTES = [
          #(r'/images/(.*)', tornado.web.StaticFileHandler, {'path': imgdb_settings.IMAGES_ROOT_FOLDER}),
          #(r'/thumbs/(.*)', tornado.web.StaticFileHandler, {'path': '/share/imagedb/thumbs/share/mikro/IMX/MDC Polina Georgiev/'}),
          (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),
          (r'/api/query', QueryHandler),
          (r'/api/list/(?P<plate>[^\/]+)', ListImagesQueryHandler),
          (r'/api/image-merge/ch1/(?P<ch1>.+)/ch2/(?P<ch2>.+)/ch3/(?P<ch3>.+)/channels.png', ImageMergeHandler),
          (r'/api/image-merge-thumb/ch1/(?P<ch1>.+)/ch2/(?P<ch2>.+)/ch3/(?P<ch3>.+)/channels.png', ThumbImageMergeHandler),
          (r'/image-viewer/(?P<plate>[^\/]+)/(?P<timepoint>[^\/]+)/(?P<well>[^\/]+)/(?P<wellsample>[^\/]+)/(?P<channel>[^\/]+)/(?P<imageurl>.+)', ImageViewerHandler),
          (r'/bstest.html', DefaultTemplateHandler),
          (r'/index.html', DefaultTemplateHandler),
          (r'/old-index.html', DefaultTemplateHandler),
          (r'/', IndexTemplateHandler),
         ]

if __name__ == '__main__':

    tornado.log.enable_pretty_logging()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logging.getLogger().setLevel(logging.DEBUG)

    APP = tornado.web.Application(ROUTES, **SETTINGS)
    APP.listen(8080)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("Shutting down")
