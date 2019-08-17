import os
from flask import request, Response, Flask
from flask_cors import CORS
import requests
from threading import Thread
import time
import logging

DEFAULT_LOG_FOLDER = os.path.dirname(__file__)
DEFAULT_LOG_FILE_NAME = "proxyserver"

logging.getLogger("werkzeug").propagate = False
logging.getLogger("urllib3").propagate = False

class ProxyServer(Thread):

    def __init__(self, serverUrl, port, host = "127.0.0.1", ssl = True, certFile = None, keyFile = None,
                 logDir = DEFAULT_LOG_FOLDER, logFileName = DEFAULT_LOG_FILE_NAME):
        """
        Parameters:
            (str) host: give 0.0.0.0 to have server available externally. Default is 127.0.0.1
            (int) port: port of the web server
        """

        super(ProxyServer, self).__init__()
        self._initialise_logger(logDir = logDir, logFileName = logFileName)
        self.app = Flask(__name__)
        CORS(self.app, resources = {r"/api/*": {"origins": "*"}})
        self.host = host
        self.port = port
        self.app.add_url_rule("/shutdown", view_func = self._shutdown_server)
        self.serverUrl = serverUrl
        self.certFile = certFile
        self.keyFile = keyFile
        self.ssl = ssl

    def _initialise_logger(self, logDir, logFileName):

        self.logFilePath = os.path.join(logDir, "{}.log".format(logFileName))
        self.logger = logging.getLogger(logFileName)
        self.logger.setLevel(logging.DEBUG)
        fH = logging.FileHandler(filename = self.logFilePath, mode = 'a', delay = 0)
        fH.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        fH.setFormatter(formatter)
        self.logger.addHandler(fH)

    def _shutdown_server(self):

        if not 'werkzeug.server.shutdown' in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):

        requests.get("http://localhost:%s/shutdown" % self.port)
        self.join()

    def _proxy(self, **kwargs):

        self.logger.debug("Url: '{}'\nMethod: '{}'\nHeaders: '{}'\ndata: {}\n".
                     format(request.url, request.method, request.headers, request.get_data()))
        resp = requests.request(
            method = request.method,
            url = request.url.replace(request.host_url, self.serverUrl),
            headers = {key: value for (key, value) in request.headers if key != 'Host'},
            data = request.get_data(),
            cookies = request.cookies,
            allow_redirects = False)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        response.headers['Access-Control-Allow-Origin'] = "*"
        self.logger.debug("Response: {}\n{}\n".format(resp.content, str('-' * 120)))
        return response

    def run(self):

        sslContext = None
        if self.ssl:
            sslContext = 'adhoc'
            if self.certFile and self.keyFile:
                sslContext = (self.certFile, self.keyFile)

        self.app.run(host = self.host, port = self.port, ssl_context = sslContext)

    def initialise(self):

        self.daemon = True
        self.start()

        # adding little sleep as start & shutdown mock server very often creates connection problems
        time.sleep(0.5)

        self.app.add_url_rule(rule = "/", view_func = self._proxy, defaults = {"request": request},
                              methods = ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"])
        self.app.add_url_rule(rule = "/<path:path>", view_func = self._proxy, defaults = {"request": request},
                              methods = ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"])