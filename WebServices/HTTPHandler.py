
import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import os
import tornado.web

import IndexHandler
import WSHandler



# HTTP Web Service
class HTTPHandler( tornado.web.Application ):

    def __getstate__(self):
        # Process safe logger copy
        d = self.__dict__.copy()
        if 'logger' in d:
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        # Process safe logger copy
        if 'logger' in d:
            logging.config.dictConfig(d['logconfig'])
            d['logger'] = logging.getLogger(d['logger'])
        self.__dict__.update(d)

    def __init__(self, logger, logconfig, queHdw, queWeb, config):

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # message queues
        self.queHdw = queHdw
        self.queWeb = queWeb

        self.static_dir = os.path.join(self.config["DIRNAME"], "static")
        self.static_dir_dict = dict(path=self.static_dir)

        # define handlers
        self.handlers = [
            # public
            (r'/', IndexHandler.IndexHandler, dict(logger=self.logger, logconfig=self.logconfig, config=self.config)),
            (r'/ws/(.*)', WSHandler.WSHandler, dict(logger=self.logger, logconfig=self.logconfig, queHdw=self.queHdw, queWeb=self.queWeb, config=self.config)),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path" : 'static/favicon.ico'}),
            (r'/(.*.js)', tornado.web.StaticFileHandler, {"path" : 'static/assets/js/.*.js'})
        ]

        self.settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        tornado.web.Application.__init__(self, handlers=self.handlers, default_host="", transforms=None, **self.settings)



