import unittest
import requests
import sys
sys.path.append(".")
import proxyserver
from flask import Response

class TestProxyServer(unittest.TestCase):

    def setUp(self):

        self.server = proxyserver.ProxyServer(serverUrl = "http://services.groupkt.com/", port = 5001, ssl = False)
        self.server.initialise()
        self.url = "http://127.0.0.1:5001"

    def _countryCallback(self, **kwargs):

        response = Response({"code": "bad_request"}, 400, {})
        return response

    def test_get_url_segement_params(self):

        self.server.app.add_url_rule(rule = "/country/get/<path:path>", view_func = self._countryCallback,
                                     methods = ["GET"])

        response = requests.get(self.url + "/country/get/iso3code/IND")
        self.assertEqual(400, response.status_code)

        # code to remove the callback function which was set of a specific endpoint
        list(map(lambda rule: self.server.app.url_map._rules.remove(rule) \
            if str(rule) == "/country/get/<path:path>" else None, self.server.app.url_map._rules))

    def test_get_url_params(self):

        self.server.app.add_url_rule(rule = "/country/<path:path>", view_func = self._countryCallback,
                                     methods = ["GET"])
        response = requests.get(self.url + "/country/search?text=un")
        self.assertEqual(400, response.status_code)

        # code to remove the callback function which was set of a specific endpoint
        list(map(lambda rule: self.server.app.url_map._rules.remove(rule) \
            if str(rule) == "/country/get/<path:path>" else None, self.server.app.url_map._rules))

    def tearDown(self):

        self.server.shutdown_server()

if __name__ == '__main__':
    unittest.main()