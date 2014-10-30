from burp import IBurpExtender
from burp import IMenuItemHandler

from framework.myhttp import MyHTTPMsg
from reqresp.reqresp import Request

from threading import Thread
from urlparse import *
import logging
import traceback
import re
import copy
import sys

import java

class BurpExtender(IBurpExtender):
    # ------------------------------------------------
    # Initialization
    # ------------------------------------------------
    def __init__(self):
	self.set_logging()

	self.__logger = logging.getLogger("BurpExtender")

	self.__logger.info('-------------------------------------------------------------------')
	self.__logger.info('Starting BurpStrike...')
	self.__logger.info('-------------------------------------------------------------------')


	self.root = ['http://localhost:8080/injection_CSRF/', 'http://localhost:8080/injection_CSRF/index.jsp']
	self.parser = re.compile("org.apache.catalina.filters.CSRF_NONCE=(.*?)\"",re.MULTILINE|re.DOTALL)
	self.token_param = "org.apache.catalina.filters.CSRF_NONCE"
	self.tool_list = ['scanner', 'repeater']

    def registerExtenderCallbacks(self, callbacks):
	self.__logger.debug('registerExtenderCallbacks. START')

	try:
	    self.mCallBacks = callbacks
	    #callbacks.registerMenuItem("De/Activate CSRF plugin ...", BurpStrikeMenuItem())
	    self.__logger.info('* setting burp callbacks')

	except Exception, e:
	    traceback.print_exc(file=sys.stdout)
	    self.formatExceptionInfo("registerExtenderCallbacks")
	finally:
	    self.__logger.debug('registerExtenderCallbacks. END')

    def set_logging(self):
	level = logging.DEBUG

	logging.basicConfig(level = level,
			    format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
			    datefmt = '%m-%d %H:%M',
			    filename = "burpstrike.log",
			    filemode = 'a')

    # ------------------------------------------------
    # Unhandled exceptions
    # ------------------------------------------------
    def formatExceptionInfo(self, where, level = 6):
	error_type, error_value, trbk = sys.exc_info()
	tb_list = traceback.format_tb(trbk, level)    
	s = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__, error_value)
	for i in tb_list:
	    s += "\n" + i

	print "Unhandled exception at %s: %s" % (where, error_type.__name__)
	self.__logger.error(s)

    # ------------------------------------------------
    # process
    # ------------------------------------------------
    def processHttpMessage(self, toolName, messageIsRequest, messageInfo):
	self.__logger.debug('processHttpMessage. START, toolName=%s isReq=%s url=%s' % (toolName, str(messageIsRequest), messageInfo.getUrl()))

	try:
	
	    if toolName in self.tool_list and messageIsRequest and self.mCallBacks.isInScope(messageInfo.getUrl()):
		http_msg = MyHTTPMsg.from_processHttpMessage(toolName, messageIsRequest, messageInfo)

		old_token = None
		if http_msg.get_request().existsGETVar(self.token_param):
		    old_token = http_msg.get_request().getVariableGET(self.token_param)

		if old_token is not None:
		    new_token, new_referer = self.referer_walk(http_msg)

		    if new_token:
			self.__logger.debug('processHttpMessage. old token=%s new token=%s' % (old_token, new_token))

			http_msg.get_request().setVariableGET("org.apache.catalina.filters.CSRF_NONCE", new_token )
			if new_referer: http_msg.get_request().addHeader('Referer', new_referer)

			import jarray
			new_msg = http_msg.get_request().getAll()

			s = str(new_msg)
			#print new_msg
			a = jarray.array(s, 'b')

			messageInfo.setRequest(a)

	except Exception, e:
	    self.formatExceptionInfo("processHttpMessage")
	finally:
	    self.__logger.debug('processHttpMessage. END')

    def find_referer(self, url):
	for i in reversed([MyHTTPMsg.from_IHttpRequestResponse(i) for i in self.mCallBacks.getProxyHistory()]):
	    #print "url %s i %s" % (url, i.get_request().completeUrl)
	    if  url == i.get_request().completeUrl:
		return i.get_request()

	return None

    def look_for_token(self, data):
	for i in self.parser.findall(data):
	    return i

	return None

    def referer_walk(self, msg):
	self.__logger.debug('referer_walk. START, url=%s' % (msg.get_request().completeUrl))

	l = []

	i = msg.get_request()
	l.append(i)

	reached_root = False

	while i is not None:
	    i = self.find_referer(i["Referer"])

	    if i is not None:
		if i.completeUrl in self.root:
		    reached_root = True
		    l.append(i)
		    self.__logger.debug('referer_walk. Reached ROOT, request list=%s' % map(lambda x: x.completeUrl, l)) 
		    break

		if i.completeUrl in map(lambda x: x.completeUrl, l):
		    self.__logger.debug('referer_walk. Detected a bucle, aborting...')
		    return (None, None)

		l.append(i)

	new_token = None

	if reached_root:
	    for i in reversed(l[1:]):

		a = Request()
		a.addHeader('Cookie', i['Cookie'])
		a.setUrl(i.completeUrl)
		if i.completeUrl in self.root:
		    a.perform()
		    content = a.response.getContent()

		    new_token = self.look_for_token(content)
		    new_referer = a.completeUrl
		    self.__logger.debug('referer_walk. re-requesting cookie %s URL=%s, new token=%s, new ref=%s' % (a['Cookie'], a.completeUrl, new_token, new_referer))

		else:
		    if not new_token:
			self.__logger.debug('referer_walk. New token is none, aborting...')
			return (None, None)

		    a.setVariableGET("org.apache.catalina.filters.CSRF_NONCE", new_token )
		    if new_referer: a.addHeader('Referer', new_referer)

		    a.perform()

		    new_token = self.look_for_token(a.response.getContent())
		    new_referer = a.completeUrl

		    self.__logger.debug('referer_walk. re-requesting cookie %s URL=%s, new token=%s, new ref=%s' % (a['Cookie'], a.completeUrl, new_token, new_referer))

	self.__logger.debug('referer_walk. END, new token=%s, new referer=%s' % (new_token, new_referer))
	return (new_token, new_referer)
