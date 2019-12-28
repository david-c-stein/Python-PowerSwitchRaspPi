import Global

import json
import time
import datetime
import os.path
import tornado.web
import tornado.websocket
from tornado.escape import json_encode, json_decode
from tornado.options import options
import uuid
import base64


def getClientID():
    return ('ID_' + str(uuid.uuid1()).replace('-',''))


class WSHandler(tornado.websocket.WebSocketHandler):

    # web clients
    clients = {}

    # state of hw
    hwState = {}

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

    def initialize(self, logger, logconfig, queHdw, queWeb, config):

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # check to see if hwState is uninitialized
        if not WSHandler.hwState:
            for i in self.config['hardware']:
                WSHandler.hwState[i['id']] = False

        # message queues
        self.getMsg = queWeb
        self.putMsgHwd = queHdw.put

        # setup message handler
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=.2), self.msgHandler)

    #=============================================================

    def msgHandler(self):
        if not self.getMsg.empty():
            msg = self.getMsg.get()
            if not Global.__MULTIPROCESSING__:
                self.getMsg.task_done()

            if (msg != None):
                if (msg[0] == 'stateUpdate'):
                    for i in msg[1]:
                        WSHandler.hwState[i] = msg[1][i]
                    WSHandler.sendAllStatus();

        # continue message handler
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=.2), self.msgHandler)

    #=============================================================

    def check_origin(self, origin):
        return True

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self, *args):

        # get client ip address
        x_real_ip = self.request.headers.get("X-Real-IP")
        self.ipAddr = x_real_ip or self.request.remote_ip
        # Get unique client ID
        self.id = getClientID()

        #self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        WSHandler.clients[self.id] = {"id": self.id, "object": self, "loggedIn": False}
        self.logger.info("Client added: id " + self.id + " IP addr: " + self.ipAddr)

        # update new client with the state of things
        self.sendAlert( 'Welcome to QA Power Management', 'This is located in the San Jose lab', 'Ok' )        
        self.sendStatus()
        
    def on_close(self):
        if self.id in WSHandler.clients:
            del WSHandler.clients[self.id]
        self.logger.info("Client closed: id " + self.id + " IP address " + self.ipAddr)

    def on_message(self, message):
        self.logger.info("Client : " + self.id + " msg: " + message)
        self.msg = json_decode(message)

        # login message
        if (self.msg['event'] == 'login'):
            if( self.verifyLogin(self.msg) ):
                WSHandler.clients[self.id]['loggedIn'] = True
                self.senddata(['loggedIn',  True]);
            else:
                self.sendAlert( 'Login warning', 'Incorrect username or password.', 'Ok')

        # get status message
        elif (self.msg['event'] == 'getStatus'):
            self.sendStatus()

        else:
            # all other message requre login
            if (WSHandler.clients[self.id]['loggedIn']):
                if self.msg['event'] in WSHandler.hwState:
                    # send message to the HW side
                    self.putMsgHwd(self.msg)
                else:
                    self.logger.warn(' ??? ' + str(self.msg) )
            else:
                self.senddata( ["contStatus", "Not Logged In" ] )

    def senddata(self, a):
        self.write_message( json_encode(a) )

    @classmethod
    def sendAllData(cls, a):
        for c in cls.clients:
            cls.clients[c]['object'].senddata(a);

    @classmethod
    def sendOthersData(cls, id, a):
        for c in cls.clients:
            if cls.clients[c]['id'] != id:
                cls.clients[c]['object'].senddata(a);

    @classmethod
    def sendOneData(cls, id, a):
        for c in cls.clients:
            if cls.clients[c]['id'] == id:
                cls.clients[c]['object'].senddata(a);

    #---------------------------------------------------

    @classmethod
    def sendAllStatus(cls):
        powerStates = {}
        for i in cls.hwState:
            powerStates[i] = cls.hwState[i]
        for c in cls.clients:
            cls.clients[c]['object'].senddata(['stateUpdate', powerStates])
    
    def sendStatus(self):
        # Send new client current state
        powerStates = {}
        currentState = WSHandler.hwState        
        for i in currentState:
            powerStates[i] = currentState[i]
        self.senddata(['stateUpdate', powerStates])

    def sendAllAlert(self, hdr, body, ftr='Ok'):
        self.senddata( ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def sendOthersAlert(self, id, hdr, body, ftr='Ok'):
        WSHandler.sendOthersData( id, ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def sendOneAlert(self, id, hdr, body, ftr='Ok'):
        WSHandler.sendOneData( id, ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def sendAlert(self, hdr, body, ftr='Ok'):
        self.senddata( ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def verifyLogin(self, msg):
        if((msg['data'][0] == Global.__USERNAME__) and (msg['data'][1] == Global.__PASSWORD__)):
            return True
        else:
            return False

