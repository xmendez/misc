'''
myhttp.py

Copyright 2009 Xavier Mendez Navarro aka Javi

This file is part of pysqlin

pysqlin is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

pysqlin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pysqlin; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import logging
import sys
import time
from java.net import URL

from urlparse import *

from reqresp.reqresp import Request


class MyHTTPMsg():
    BSTRIKE, BURP_TOOL= range(2)

    SPIDER = "spider"
    PROXY = "proxy"
    SCANNER = "scanner"
    TARGET = "target"
    REPEATER = "repeater"
    INTRUDER = "intruder"
    SEQUENCER = "sequencer"

    def __init__(self, req = None):
	self.__logger = logging.getLogger('framework.myhttp.MyHTTPMsg')

	self.__req = req

	# msg attributes
	self.mtype = None
	self.source = None


	# burp attributes
	self.comment = ""

    # ------------------------------------------------
    # Factory functions
    # ------------------------------------------------
    @staticmethod
    def from_ProxyMessage(headers, messageIsRequest, remoteHost, remotePort, serviceIsHttps, httpMethod, url, resourceType, statusCode, responseContentType, message, interceptAction):
	req = Request()

	if messageIsRequest:
	    req.parseRequest(message.tostring())
	else:
	    req.parse_response(message.tostring())

	if serviceIsHttps:
	    req.schema = "https"

	if url and remoteHost and remotePort:
	    req.setUrl(req.schema + "://" + remoteHost + url)
	    #req.setUrl(req.schema + "://" + remoteHost + ":" + str(remotePort) + url)
	elif url and remoteHost:
	    req.setUrl(req.schema + "://" + remoteHost + url)

	my = MyHTTPMsg(req)

	return my

    @staticmethod
    def from_IHttpRequestResponse(hrrmsg):
	ireq = hrrmsg.getRequest()
	iresp = hrrmsg.getResponse()
	url = hrrmsg.getUrl()

	req = Request()

	if ireq is not None:
	    req.parseRequest(ireq.tostring())

	if iresp is not None:
	    req.parse_response(iresp.tostring())

	if url:
	    req.setUrl(hrrmsg.getUrl().toString())

	my = MyHTTPMsg(req)

	return my

    @staticmethod
    def from_processHttpMessage(toolName, messageIsRequest, ireqresp):
	# request messages are commonly uncompleted until response arrives
	#if messageIsRequest:
	#    return None
	#else:

	ireq = ireqresp.getRequest()

	iresp = None
	if not messageIsRequest:
	    iresp = ireqresp.getResponse()

	url = ireqresp.getUrl()

	req = Request()

	if ireq is not None:
	    req.parseRequest(ireq.tostring())

	if iresp is not None:
	    req.parse_response(iresp.tostring())

	if url:
	    req.setUrl(ireqresp.getUrl().toString())

	my = MyHTTPMsg(req)
	my.source = toolName

	return my

    # ------------------------------------------------
    # Java conversions
    # ------------------------------------------------
    def get_java_url(self):
	self.__logger.debug('get_java_url. START')

	port = 80
	host = self.__req.getHost()

	if self.__req.getHost().find(":") > 0:
	    host, p = self.__req.getHost().split(":")
	    port = int(p)

	uUrl = URL(self.__req.schema, host, port, self.__req.pathWithVariables)

	self.__logger.debug('get_java_url. END. uUrl=%s' % (uUrl))

	return uUrl

    # ------------------------------------------------
    # HTTP functions
    # ------------------------------------------------
    def get_url(self):
	return self.__req.completeUrl

    def has_response(self):
	return self.__req.response

    def get_response_content(self):
	return self.__req.response.getContent()

    def get_response_code(self):
	return self.__req.response.code

    def get_response(self):
	return (self.__req.response.code, self.__req.response.getContent())

    # ------------------------------------------------
    # legacy reqresp
    # ------------------------------------------------
    def get_request(self):
	return self.__req

