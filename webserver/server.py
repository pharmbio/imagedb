import os
import logging
import tornado
import tornado.web
import tornado.ioloop

from handlers.query_handlers import (ListAllPlatesQueryHandler,
                                     GetPlateQueryHandler,
                                     ListImageAnalysesHandler,
                                     MoveAcqIDToTrashHandler)

from handlers.image_handlers import (ImageMergeHandler,
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
    def get(self, barcode='', acqid=''):

        barcode = self.get_argument("barcode", '')
        acqid = self.get_argument("acqid", '')
        pipelinegui_url = imgdb_settings.PIPELINEGUI_URL
        pipelinegui_static_results_dir = imgdb_settings.PIPELINEGUI_STATIC_RESULTS_DIR
        adminer_url = imgdb_settings.ADMINER_URL

        self.render('index.html', barcode=barcode, acqid=acqid, pipelinegui_url=pipelinegui_url,
                                  pipelinegui_static_results_dir=pipelinegui_static_results_dir,
                                  adminer_url=adminer_url)

class ImageViewerTemplateHandler(tornado.web.RequestHandler): #pylint: disable=abstract-method

    def get(self, plate, acquisition, well, site, zpos, channel, imageurl):

        logging.debug('plate' + str(plate))
        logging.debug('acquisition' + str(acquisition))
        logging.debug('well' + str(well))
        logging.debug('site' + str(site))
        logging.debug('zpos' + str(zpos))
        logging.debug('channel' + str(channel))
        logging.debug(self.request.body_arguments)

        self.render('image-viewer.html',
                     image_url=imageurl,
                     plate=plate,
                     acquisition=acquisition,
                     well=well,
                     site=site,
                     zpos=zpos,
                     channel=channel)


ROUTES = [
          (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),
          (r'/api/move-to-trash/(?P<acqID>.+)', MoveAcqIDToTrashHandler),
          (r'/api/list-plates', ListAllPlatesQueryHandler),
          (r'/api/list/image_analyses/(?P<limit>.+)/(?P<sortorder>.+)/(?P<plate_barcode>.+)', ListImageAnalysesHandler),
          (r'/api/plate/(?P<plate>.+)/(?P<acqID>.+)', GetPlateQueryHandler),
          (r'/api/image-merge/ch1/(?P<ch1>.+)/ch2/(?P<ch2>.+)/ch3/(?P<ch3>.+)/channels.png', ImageMergeHandler),
          (r'/api/image-merge-thumb/ch1/(?P<ch1>.+)/ch2/(?P<ch2>.+)/ch3/(?P<ch3>.+)/channels.png', ThumbImageMergeHandler),
          (r'/image-viewer/(?P<plate>.+)/tp/(?P<acquisition>.+)/well/(?P<well>.+)/site/(?P<site>.+)/zpos/(?P<zpos>.+)/ch/(?P<channel>.+)/url/(?P<imageurl>.+)', ImageViewerTemplateHandler),
          (r'/bstest.html', DefaultTemplateHandler),
          (r'/index.html', IndexTemplateHandler),
          (r'/', IndexTemplateHandler),
         ]

if __name__ == '__main__':

    #tornado.log.enable_pretty_logging()

    logging.getLogger('tornado.access').disabled = True

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    APP = tornado.web.Application(ROUTES, **SETTINGS)
    APP.listen(8080)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("Shutting down")
