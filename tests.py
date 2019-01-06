import unittest
import requests
import api_proxy

class TestProxyServer(unittest.TestCase):

    def setUp(self):

        self.server = api_proxy.ProxyServer(serverUrl = "http://services.groupkt.com/", port = 5001, ssl = False)
        self.server.initialise()
        self.url = "http://127.0.0.1:5001"

    def test_get_url_segement_params(self):

        response = requests.get(self.url + "/country/get/iso3code/IND")
        self.assertEqual(200, response.status_code)

    def test_get_url_params(self):
        response = requests.get(self.url + "/country/search?text=un")
        self.assertEqual(200, response.status_code)

    def tearDown(self):

        self.server.shutdown_server()

if __name__ == '__main__':
    unittest.main()