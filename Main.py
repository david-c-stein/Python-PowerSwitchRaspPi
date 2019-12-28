#!/usr/bin/env python

import datetime
import getopt
import inspect
import json
import os
import platform
import sys
import time
import threading

from Global import __MULTIPROCESSING__


__version__ = '0.1'


if __MULTIPROCESSING__:
    import multiprocessing
    from multiprocessing import Queue
else:
    if sys.version_info[0] < 3:
        from Queue import Queue
    else:
        from queue import Queue

import Logger

starttime = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")

#-----------------------
class myApp(object):

    logger = None
    logconfig = None

    pHW = None  # Hardware thread/process
    pWS = None  # WebServices thread/process

    def main(self, argv):

        self.logger  = Logger.logging.getLogger(__name__)
        self.logconfig = Logger.logconfig

        self.logger.info("Start time: " + starttime)

        self.configFile = None


        # parse command line arguments
        try:
            opts, args = getopt.getopt(argv, "hd:", ["help", "desc="])
        except getopt.GetoptError as e:
            self.logger.exception(str(e))
            self.usage()
            return
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                return
            elif opt in ("-d"):
                self.configFile = arg
            else:
                self.usage()
                return

        if(self.configFile == None):
            self.usage()
            return

        # initilize and run
        self.initilize()
        self.start()
        self.stop()

    #-----------------------
    def initilize(self):
        try:
            # identify platform
            self.logger.info("------------------------------")
            self.logger.info("  machine: " + platform.machine())
            self.logger.info("  version: " + platform.version())
            self.logger.info(" platform: " + platform.platform())
            self.logger.info("   system: " + platform.system())
            self.logger.info("processor: " + platform.processor())
            if __MULTIPROCESSING__:
                self.logger.info("    cores: " + str(multiprocessing.cpu_count()))
            self.logger.info("    nodes: " + platform.node())
            self.logger.info("PythonImp: " + platform.python_implementation())
            self.logger.info("PythonVer: " + platform.python_version())
            self.logger.info("starttime: " + starttime)
            self.logger.info("scriptver: " + __version__)
            self.logger.info("------------------------------")

            # include paths
            dirs = ['pythonLibs', 'Hardware', 'WebServices']
            self.initPaths(dirs)

            # initialize queues
            if __MULTIPROCESSING__:
                self.queHdw = multiprocessing.Queue()
                self.queWeb = multiprocessing.Queue()
            else:
                self.queHdw = Queue()
                self.queWeb = Queue()

            # hardware configuration
            self.configHW = {
                "HTTPPORT" : 8888,
                "SOCKETIOPORT" : 8888,
            }

            # include configuation from file
            data = self.readFile(self.configFile)
            self.configHW.update(data)
            #print(self.configHW)

            # initialize hardware process
            try:
                import Hardware
                self.pHW = Hardware.Hardware(self.logger, self.logconfig, self.queHdw, self.queWeb, self.configHW)
            except Exception as e:
                self.logger.exception(e)
                print( "Hardware Initialization Error: " + str(e) )

            # initialize web services process
            try:
                import WebServices
                self.pWS = WebServices.WebServices(self.logger, self.logconfig, self.queHdw, self.queWeb, self.configHW)
            except Exception as e:
                self.logger.exception(e)
                print( "Web Initialization Error: " + str(e) )

        except Exception as e:
            self.logger.exception(e)
            print( "Initialization Error: " + str(e) )
            exit(1)

        return

    #-----------------------
    # json file methods

    def readFile(self, path):
        with open(path, 'r') as datafile:
            return(json.load(datafile))

    def writeFile(self, path, data):
        with open(path, 'w') as datafile:
            json.dump(data, datafile)

    #-----------------------
    def start(self):
        try:
            # start hardware process
            self.pHW.start()
            # start webservices process
            self.pWS.start()

            RUNNING = True;

            while RUNNING:
                try:
                    # TODO : include a curses command line gui here
                    time.sleep(0.200)

                except (KeyboardInterrupt, SystemExit):
                    self.logger.info("Interrupted")
                    self.stop()
                    exit()
                except Exception as e:
                    self.logger.exception(str(e))

        except Exception as e:
            self.logger.exception(str(e))

    #-----------------------
    def stop(self):
        # stop processes
        if(self.pHW != None):
            self.pHW.stop()
        if(self.pWS != None):
            self.pWS.stop()

    #-----------------------
    def usage(self):
        print("\n\n python " + __file__ + " -d <config>.cfg \n")
        exit()

    #-----------------------
    def initPaths(self, dirs):

        try:
            # include <local> paths   NOTE: realpath() works with simlinks
            cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
            if cmd_folder not in sys.path:
                sys.path.insert(0, cmd_folder)
                self.logger.info("Path Added : " + cmd_folder)

            # include dirs passed
            for dir in dirs:
                cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], dir)))
                if cmd_subfolder not in sys.path:
                    sys.path.insert(0, cmd_subfolder)
                    self.logger.info("Path Added : " + cmd_subfolder)

        except Exception as e:
            self.logger.exception(str(e))
            raise


if __name__== '__main__':
    myApp().main(sys.argv[1:])

