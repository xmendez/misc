from basereqresp import BaseRequest
from basereqresp import Response
from basereqresp import IRequest

import logging
import urllib
import httplib

class HTTPLibRequest(BaseRequest, IRequest):
    def __init__(self):
	BaseRequest.__init__(self)
	self.__logger = logging.getLogger("HTTPLibRequest")

    def setAuth (self,method,string):
	pass

    def getAuth (self):
	pass

    def setProxy (self,prox):
	pass

    def setConnTimeout (self,time):
	pass

    def setTotalTimeout (self,time):
	pass

    def setFollowLocation(self,value):
	pass

    def parse_response(self, s):
	self.response = Response()
	self.response.parseResponse(s)

    def perform(self):
	self.__logger.debug("perform. START.")

	# forge request
	params = urllib.urlencode(dict([[i.name,i.value] for i in self.getPOSTVars()]))
	conn = httplib.HTTPConnection(self.getHost())
	self.__logger.debug("perform. getResponse: method=%s, host=%s, path=%s, params=%s, headers=%s" % (self.method, self.getHost(), self.pathWithVariables, params, self._headers))

	try:
	    conn.request(self.method, self.pathWithVariables, params, self._headers)

	    response = conn.getresponse()
	except socket.gaierror:
	    self.__logger.debug("Perform. Error in request")
	except socket.error:
	    self.__logger.debug("Perform. Error in request")
	except socket.timeout:
	    self.__logger.debug("Perform. Error in request")

	# parse response
	s = ""
	if response.version == 10:
	    s += "HTTP/1.0 "
	else:
	    s += "HTTP/1.1 "
	s += str(response.status) + "\r\n" + str(response.msg) + "\r\n" + response.read()
	conn.close()

	self.parse_response(s)

	self.__logger.debug("perform. END.")
