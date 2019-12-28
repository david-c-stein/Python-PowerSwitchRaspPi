
import tornado.web
import uuid


class IndexHandler(tornado.web.RequestHandler):

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

    def initialize(self, logger, logconfig, config):
        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.address = self.config["IPADDRESS"]
        self.port = self.config["SOCKETIOPORT"]

        if self.address == "":
            self.address = "127.0.0.1"

        # build out buttons from configuration
        self.buttonsCfg = self.config['hardware']
        self.buttonCnt = len(self.buttonsCfg)

        if self.buttonCnt <= 8:
            self.buttonsHtml = """<div class="11u 12u$(medium)"> """
            for n in range(0, self.buttonCnt):
                self.buttonsHtml += """<a onclick="window.btnPressed('""" + self.buttonsCfg[n]["id"] + """',   'btnPressed')" id='""" + self.buttonsCfg[n]["id"] + """' class="button fit disabled" title='""" + self.buttonsCfg[n]["label"] + """<'>""" + self.buttonsCfg[n]["name"] + """</a>"""
            self.buttonsHtml += """ </div> """
        else:
            self.buttonsHtml = """<div class="6u 12u$(medium)"> """
            for n in range(0, self.buttonCnt/2):
                self.buttonsHtml += """<a onclick="window.btnPressed('""" + self.buttonsCfg[n]["id"] + """',   'btnPressed')" id='""" + self.buttonsCfg[n]["id"] + """' class="button fit disabled" title='""" + self.buttonsCfg[n]["label"] + """<'>""" + self.buttonsCfg[n]["name"] + """</a>"""
            self.buttonsHtml += """ </div>  
                <div class="6u 12u$(medium)"> """
            for n in range(self.buttonCnt/2, self.buttonCnt):
                self.buttonsHtml += """<a onclick="window.btnPressed('""" + self.buttonsCfg[n]["id"] + """',   'btnPressed')" id='""" + self.buttonsCfg[n]["id"] + """' class="button fit disabled" title='""" + self.buttonsCfg[n]["label"] + """<'>""" + self.buttonsCfg[n]["name"] + """</a>"""
            self.buttonsHtml += """ </div> """

        # button IDs for js
        self.buttonIDsJS = """ l = [ '"""
        for n in self.buttonsCfg:
            self.buttonIDsJS += n["id"]
            self.buttonIDsJS += """', '"""
        self.buttonIDsJS = self.buttonIDsJS[:-2]
        self.buttonIDsJS += """];"""


    @tornado.web.asynchronous
    def get(self):

        title = self.config['system']['name']
        css = '<link rel="stylesheet" href="static/assets/css/skelBase.css" /><link rel="stylesheet" href="static/assets/css/font-awesome.min.css" />'

        self.write( """
        <!DOCTYPE html>
        <html>
            <head id="head">
                <title>""" + title + """</title>
                <meta charset="utf-8" />
                """ + css + """
            </head>
            <body id="body">
                <noscript>
                    <div class='enableJS'>You need to enable javascript</div>
                </noscript>
                <script src="static/assets/js/jquery-3.1.0.min.js"></script>
                <script src="static/assets/js/skel.min.js"></script>
                <script src="static/assets/js/kinetic-v5.1.0.min.js"></script>

            <!-- Header -->
                <header id="header">
                    <h1><a href="#">Automation</a></h1>
                    <a href="#login">Login</a>
                    <a href="#nav">Menu</a>
                </header>

            <!-- Login -->
                <login id="login">
                    <ul class="actions vertical">
                        <li><h3>Login to assume control</h3></li>
                        <li><label><b>Username</b></label></li>
                        <li><input type="text" placeholder="Enter Username" id="un" required></li>
                        <li><label><b>Password</b></label></li>
                        <li><input type="password" placeholder="Enter Password" id="pw" required></li>
                        <li><a id="loginButton" onclick="login()" href="#" class="button special fit">Login</a></li>
                    </ul>
                </login>

            <!-- Nav -->
                <nav id="nav">
                    <ul class="links">
                        <li><a href="#top">Top</a></li>
                        <li><a href="#content">Content</a></li>
                        <li><a href="#elements">Elements</a></li>
                        <li><a href="#grid">Grid System</a></li>
                    </ul>
                    <ul class="actions vertical">
                        <li><a href="#" class="button special fit">Download</a></li>
                        <li><a href="#" class="button fit">Documentation</a></li>
                    </ul>
                </nav>

            <!-- Main -->

                <!-- Status bar -->
                <div id="status" style="border-radius: 10px; text-align: center; font-size: large; color: #FFFFFF; ">Disconnected - No Automation Processes Running</span></div>

                <!-- Message modal -->
                <div id="msgModal" class="modalWindow">
                    <div>
                        <div class="modalHeader" id="modelHeader">
                            <h2>Sample modal window</h2>
                            <a href="#close" title="Close" class="close">X</a>
                        </div>
                        <div class="modalContent" id="modelContent">
                            <p>Sample model windows</p>
                        </div>
                        <div class="modalFooter" id="modelFooter">
                            <a href="#cancel" title="Cancel" class="cancel">Cancel</a>
                            <p>David Stein : 2014</p>
                            <div class="clear"></div>
                        </div>
                    </div>
                </div>

                <!-- Main content -->
                <div id="main" class="container">

                    <div class="row">

                        <div class="12u 12u$(medium)">
                            <a onclick="toggleDivs()" class="button special fit small" title="For a description"><bold>Select</bold></a>
                            <h4>Power DUT</h4>
                        </div>
                """

                + self.buttonsHtml + 

                """     <div class="1u 12u$(medium)">
                            <!-- Information Text Stuffs -->
                            <div id="info" style="display:none">
                                <h4>USB / Power</h4>
                                This innterface is used to control the USB interfaces and Power for this system.
                                <ul>
                                    <li>Pressing Buttons on device</li>
                                    <li>Using this web interface</li>
                                </ul>
                            </div>

                        </div>
                    </div>
                </div>

            <!-- Footer -->
                <footer id="footer">
                    <div class="container">
                        <div class="row double">
                            <div class="6u 12u$(medium)">
                                <h4>QA Power Manager</h4>
                                <p>QA Power Management Goodness<br/>Contact me if you experience any issues with this application. </p>
                            </div>
                        </div>
                    </div>
                    <div class="copyright">
                        David Stein : 2015
                    </div>
                </footer>

                <!---------------------------------------------->

                <script src="static/assets/js/skelBase.js"></script>
                <script type="text/javascript" id="wsScript">

                    var socket;

                    function btnPressed(event_name, event_data) {
                        if (iAmInControl == true) {
                            window.sendMsg(event_name, event_data)
                        } else {
                            var e = document.getElementById("status");
                            e.classList.add('flash');
                            setTimeout(function() {
                                e.classList.remove('flash');
                            }, 500);
                        }
                    }

                    function sendMsg(event_name, event_data) {
                        if(socket) {
                            socket.send(event_name, event_data);
                        }
                    }

                    window.onload = function() {

                        var websocket = false;

                        if("WebSocket" in window) {
                            websocket = true;
                        } else {
                            console.log("WebSocket are not supported by this browser");
                        }

                        var mySocket = function() {
                            var ws;
                            var callbacks = {};

                            try {
                                // ensure only one connection is open
                                if(ws !== undefined && ws.readyState !== ws.CLOSED) {
                                    console.log("WebSocket is already open");
                                    return;
                                }
                                // c an instance of the websocket
                                ws = new WebSocket("ws://""" + self.address + """:""" + str(self.port) + """/ws/");
                            }
                            catch(e) {
                                console.log(e.message);
                            };

                            this.bind = function(event_name, callback) {
                                callbacks[event_name] = callbacks[event_name] || [];
                                callbacks[event_name].push(callback);
                                return this;            // chainable
                            };

                            this.unbind = function(event_name) {
                                delete callbacks[event_name];
                            };

                            this.send = function(event_name, event_data) {
                                var payload = JSON.stringify({event: event_name, data:event_data});
                                waitForSocket(ws, function(){
                                    ws.send(payload);
                                });
                                return this;
                            };

                            function waitForSocket(socket, callback) {
                                setTimeout(
                                    function () {
                                        if (socket.readyState === socket.OPEN) {
                                            // connection is ready
                                            if(callback != null)
                                                callback();
                                            return;
                                        } else {
                                            // connection is not ready yet
                                            waitForSocket(socket, callback)
                                        }
                                   }, 5);  // wait 5 milliseconds for connection
                            };

                            ws.onmessage = function(env) {
                                var j = JSON.parse(env.data);
                                console.log(j)
                                dispatch(j[0], j[1]);
                            };

                            ws.onclose = function() {
                                dispatch('closed', null);
                                disableAll();
                            }

                            ws.onopen = function() {
                                dispatch('opened', null);
                            }

                            ws.onerror = function(evt) {
                                var err = evt.data;
                                console.log("Error occured");
                                dispatch('error', err);
                                disableAll();
                            };

                            var dispatch = function(event_name, message) {
                                var chain = callbacks[event_name];
                                if (typeof chain == 'undefined')
                                    return;             // no callbacks for this event
                                for(var i = 0; i < chain.length; i++)
                                    chain[i](message);
                            }
                        };

                        //-------------------------------------------------

                        if (websocket == true) {

                            socket = new mySocket();

                            socket.bind('opened', function(env) {
                                updateStatus(stateEnum.CONNECTED);
                            })

                            socket.bind('closed', function(env) {
                                updateStatus(stateEnum.DISCONNECTED);
                            })

                            socket.bind('error', function(env) {
                                updateStatus(stateEnum.ERROR);
                            })

                            socket.bind('contStatus', function(data) {
                                // control status from server

                            })

                            socket.bind('loggedIn', function(data) {
                                // sucessful login message from server
                                updateStatus(stateEnum.CONTROL);
                            })

                            socket.bind( 'stateUpdate', function(data) {
                                // state information from server

                                for(var key in data) {
                                    if( key == 'control' ){
                                        if (data[key]) {
                                            updateStatus(stateEnum.CONTROL);
                                        } else {
                                            updateStatus(stateEnum.CONNECTED);
                                        }
                                    } else {
                                        // update button
                                        var x = document.getElementById( key );
                                        x.classList.remove('disabled', 'special');
                                        if (data[key] == true){
                                            x.classList.add('special');
                                        } else {
                                            x.classList.remove('special');
                                        }
                                    }
                                }
                            })

                            socket.bind( 'alert', function(data) {

                                console.log("ALERT from server");

                                // recieved message from server to be displayed to the client
                                var hdr = document.getElementById('modelHeader');
                                var bdy = document.getElementById('modelContent');
                                var ftr = document.getElementById('modelFooter');
                                // clear revious stuffs
                                hdr.innerHTML = "";
                                bdy.innerHTML = "";
                                ftr.innerHTML = "";
                                // populate new stuffs
                                hdr.innerHTML = '<h2>' +  data['hdr'] + '</h2><a href="#close" title="Close" class="close">X</a>';
                                bdy.innerHTML = '<p>' + data['hdr'] + '</p> <p>' + data['bdy'] + '</p>';
                                var f = '';
                                if(data['ftr'] == 'Ok') {
                                    f += '<a href="#ok" title="Ok" class="ok">Ok</a>';
                                }
                                else if(data['ftr'] == 'Cancel') {
                                    f += '<a href="#cancel" title="Cancel" class="cancel">Cancel</a>';
                                }
                                else if(data['ftr'] == 'Force') {
                                    f += '<a href="#ok" onclick="forceLogin()" title="Force" class="ok">Force</a>';
                                }
                                f += '<p>For issues contact Me</p>';
                                ftr.innerHTML = f;

                                window.location.hash = '#msgModal';
                            })

                        };
                    }

                    var stateEnum = Object.freeze({ UNKNOWN: 0, DISCONNECTED: 1, CONNECTED: 2, CONTROL: 3, ERROR: 4 });
                    var iAmInControl = false;

                    function login() {
                        var x1 = document.getElementById('un').value;
                        var x2 = document.getElementById('pw').value;
                        window.sendMsg('login', [ x1, x2 ]);
                    }

                    function clearPW() {
                        document.getElementById('psw').value = "";
                    }

                    function toggleDivs() {
                        var x1 = document.getElementById('controls');
                        var x2 = document.getElementById('info');

                        if (x1.style.display === 'block') {
                            x1.style.display = 'none';
                            x2.style.display = 'block';
                        } else if (x2.style.display === 'block') {
                            x1.style.display = 'block';
                            x2.style.display = 'none';
                        }

                    }

                    function disableAll() {
                        disableAllButtons();
                    }

                    function disableAllButtons() {
                    """

                    + self.buttonIDsJS +

                    """
                        for( var i in l ) {
                            document.getElementById( l[i] ).classList.add('disabled');
                        }
                    }

                    function updateStatus( state ) {
                        var e = document.getElementById("status");

                        iAmInControl = false;

                        if (state == stateEnum.CONNECTED) {
                            e.innerHTML = "Connected - Not Logged In";
                            e.style.backgroundColor = 'darkblue';
                        }
                        else if (state == stateEnum.DISCONNECTED) {
                            e.style.backgroundColor = 'gray';
                            e.innerHTML = "Not connected";
                            window.disableAll();
                        }
                        else if (state == stateEnum.ERROR) {
                            e.style.backgroundColor = 'red';
                            e.innerHTML = "Not connected - An error has occured";
                            window.disableAll();
                        }
                        else if (state == stateEnum.CONTROL ) {
                            e.style.backgroundColor = 'green';
                            e.innerHTML = "In Control";
                            iAmInControl = true;
                        }
                        else {
                            e.style.backgroundColor = 'red';
                            e.innerHTML = "Hmmm. Something unknown has happened here";
                            window.disableAll();
                        }
                    }

                </script>
            </body>
        </html>
        """)

        self.finish()

    def write_error(self, status_code, **kwargs):
        self.write("Opps. Something's dorked - %d error." % status_code)


        
        
        
'''
                        <div class="6u 12u$(medium)">
                            <h4>Power DUT</h4>
                            <a onclick="window.btnPressed('pwrOne',   'btnPressed')" id="pwrOne"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[0] + """</a>
                            <a onclick="window.btnPressed('pwrTwo',   'btnPressed')" id="pwrTwo"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[1] + """</a>
                            <a onclick="window.btnPressed('pwrThree', 'btnPressed')" id="pwrThree" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[2] + """</a>
                            <a onclick="window.btnPressed('pwrFour',  'btnPressed')" id="pwrFour"  class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[3] + """</a>
                            <a onclick="window.btnPressed('pwrFive',  'btnPressed')" id="pwrFive"  class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[4] + """</a>
                            <a onclick="window.btnPressed('pwrSix',   'btnPressed')" id="pwrSix"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[5] + """</a>
                            <a onclick="window.btnPressed('pwrSeven', 'btnPressed')" id="pwrSeven" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[6] + """</a>
                            <a onclick="window.btnPressed('pwrEight', 'btnPressed')" id="pwrEight" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[7] + """</a>
                        </div>

                        <div class="6u 12u$(medium)">
                            <a onclick="window.btnPressed('pwrOne',   'btnPressed')" id="pwrOne"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[0] + """</a>
                            <a onclick="window.btnPressed('pwrTwo',   'btnPressed')" id="pwrTwo"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[1] + """</a>
                            <a onclick="window.btnPressed('pwrThree', 'btnPressed')" id="pwrThree" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[2] + """</a>
                            <a onclick="window.btnPressed('pwrFour',  'btnPressed')" id="pwrFour"  class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[3] + """</a>
                            <a onclick="window.btnPressed('pwrFive',  'btnPressed')" id="pwrFive"  class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[4] + """</a>
                            <a onclick="window.btnPressed('pwrSix',   'btnPressed')" id="pwrSix"   class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[5] + """</a>
                            <a onclick="window.btnPressed('pwrSeven', 'btnPressed')" id="pwrSeven" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[6] + """</a>
                            <a onclick="window.btnPressed('pwrEight', 'btnPressed')" id="pwrEight" class="button fit disabled" title="Press to Enable/Disable Power">""" + self.btnNames[7] + """</a>
                        </div>

                        l = [ 'pwrOne',
                              'pwrTwo',
                              'pwrThree',
                              'pwrFour',
                              'pwrFive',
                              'pwrSix',
                              'pwrSeven',
                              'pwrEight'
                            ];


'''
