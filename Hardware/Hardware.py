#!/usr/bin/env python

import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import time
import threading
from tornado.escape import json_encode, json_decode
import re

import RaspPi


class Hardware(multiprocessing.Process if Global.__MULTIPROCESSING__ else threading.Thread):

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
        if Global.__MULTIPROCESSING__:
            #-- multiprocessing
            multiprocessing.Process.__init__(self)
        else:
            #-- threading
            super(Hardware, self).__init__()

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.debug("Initializing " + __file__)
        
        # message queues
        self.getMsg = queHdw
        self.putMsgWeb = queWeb.put
       
        self.hw = {}
        self.gpioPins = RaspPi.PI3b
        
        # identify pin assignments
        pinChk = re.compile("PIN_(\d+)")
        
        # Verify pins in config correspond to valid gpio pins
        for i in self.config['hardware']:
        
            r = pinChk.search(i['relay'])
            pin_relay = int(r.group(1))
            if pin_relay in self.gpioPins:
                self.gpioPins = [x for x in self.gpioPins if x != pin_relay]
            else:
                raise ValueError('Unknow or duplicate pin value : ' + str(i))

            if i.has_key('led'):
                r = pinChk.search(i['led'])
                pin_led = int(r.group(1))
                if pin_led in self.gpioPins:
                    self.gpioPins = [x for x in self.gpioPins if x != pin_led]
                else:
                    raise ValueError('Unknow or duplicate pin value : ' + str(i))
            else:
                pin_led = None

            if i.has_key('button'):
                r = pinChk.search(i['button'])
                pin_button = int(r.group(1))
                if pin_button in self.gpioPins:
                    self.gpioPins = [x for x in self.gpioPins if x != pin_button]
                else:
                    raise ValueError('Unknow or duplicate pin value : ' + str(i))    
            else:
                pin_button = None

            self.hw[i['id']] = RaspPi.HWSet(i['id'], pin_relay, pin_led, pin_button)

        self.sendWebCurrentState()


    def getCurrentState(self):
        powerStates = {}
        for i in self.hw:
            powerStates[i] = self.hw[i].getState()
        return ['stateUpdate', powerStates ]


    def sendWebCurrentState(self):
        self.putMsgWeb( self.getCurrentState() )


    def run(self):
        # called on start() signal
        try:
            self.logger.debug("Running HW process")

            while True:
                try:
                    # do run HW stuffs
                    # ----------------------

                    # check for messages from the WebService
                    if (not self.getMsg.empty()):

                        self.msg = self.getMsg.get()
                        if not Global.__MULTIPROCESSING__:
                            self.getMsg.task_done()

                        self.logger.debug( 'HW : ' + str(self.msg) )

                        event = self.msg['event']
                        data = self.msg['data']

                        if event in self.hw:
                            if data == 'btnPressed':
                                self.hw[event].toggle()
                            elif data == 'On':
                                self.hw[event].on()
                            elif data == 'Off':
                                self.hw[event].off()
                            elif data == 'Toggle':
                                self.hw[event].toggle()
                            else:
                                self.logger.warn( event + ": unknown cmd: " + data )

                            self.sendWebCurrentState()

                    # HW butt presses hancled in callbacks
                    time.sleep(.2)

                except(KeyboardInterrupt, SystemExit):
                    self.logger.debug("Interupted HW process")
                    self.stop()
                    exit()

                except Exception as e:
                    self.logger.exception(e)

        except Exception as e:
            self.logger.exception(e)

    def stop(self):
        return




