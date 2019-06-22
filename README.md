# proxy-server
  It can be used to record all the requests sent by the service under test to the external services. The recorded
  requests can be used for validation or analysis. This is useful to verify the requests that service under test has
  been sent, without needing to mock any requests


  ![picture alt](https://github.com/ArunKumarJain/proxy-server/blob/master/images/proxy_server.png)

### Steps to execute tests

* Checkout the code to a local folder<br>
* Install modules in requirements.txt<br>
* Run tests using command "python tests/test_proxy_server.py"
* Refer the proxyserver.log for requests and responses logs