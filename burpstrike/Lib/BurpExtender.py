'''
BurpExtender.py

Copyright 2011 Xavier Mendez Navarro aka Javi

This file is part of burpstrike

burpstrike is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

burpstrike is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with burpstrike; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
from burp import IBurpExtender
from burp import IMenuItemHandler

from ui.console import Console
from framework.facade import Facade
from framework.jobman import JobMan
from framework.controller import Controller
from framework.settings import Settings
from framework.myhttp import MyHTTPMsg

from threading import Thread
import logging
import traceback
import sys

class ConsoleWorker(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
	try:
	    Console().cmdloop()
	except KeyboardInterrupt:
	    print "Exiting...."
	    Facade().exit()
	except Exception, e:
	    Facade().formatExceptionInfo("ConsoleWorker")

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

    def registerExtenderCallbacks(self, callbacks):
	self.__logger.debug('registerExtenderCallbacks. START')

	try:
	    #callbacks.registerMenuItem("Dis/Enable burpstrike...", BurpStrikeMenuItem())
	    #callbacks.registerMenuItem("De/Activate all plugins...", BurpStrikeMenuItem())

	#    for m in Facade().get_plugins().names():
	#	callbacks.registerMenuItem("Send to %s" % m, BurpStrikeMenuItem())

	    self.__logger.info('* setting burp callbacks in facade')
	    Facade().mCallBacks = callbacks

	    self.__logger.debug('* initializating controller')
	    Facade().controller = Controller()

	    self.__logger.debug('* initializating jobman')
	    Facade().jman = JobMan()
	    Facade().jman.start()

	    self.__logger.debug('* initializating ui')
	    cw = ConsoleWorker()
	    cw.start()
	except Exception, e:
	    traceback.print_exc(file=sys.stdout)
	    Facade().formatExceptionInfo("registerExtenderCallbacks")
	finally:
	    self.__logger.debug('registerExtenderCallbacks. END')

    def set_logging(self):
	debuglevel = Settings().get(Settings.SEC_GRL, Settings.DEBUG_LEVEL)

	if debuglevel == Settings.DEBUG_LEVEL_DEBUG:
		level = logging.DEBUG
	elif debuglevel == Settings.DEBUG_LEVEL_INFO:
		level = logging.INFO
	elif debuglevel == Settings.DEBUG_LEVEL_WARNING:
		level = logging.WARNING
	elif debuglevel == Settings.DEBUG_LEVEL_ERROR:
		level = logging.ERROR
	elif debuglevel == Settings.DEBUG_LEVEL_CRITICAL:
		level = logging.CRITICAL

	logging.basicConfig(level = level,
			    format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
			    datefmt = '%m-%d %H:%M',
			    filename = Settings().get(Settings.SEC_GRL, Settings.LOGFILE),
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

    def applicationClosing(self):
	self.__logger.debug('applicationClosing. START')
	self.__logger.debug('killing jobman... ')
	self.__logger.debug('applicationClosing. END')

    # ------------------------------------------------
    # process
    # ------------------------------------------------
    def __add_to_queue(self, msg):
	self.__logger.debug('__add_to_queue. START')

	if Settings().get(Settings.SEC_PLUGIN_INTEGRATION, Settings.ACTIVE) != 'True':
	    self.__logger.debug('__add_to_queue. Url not enqueued, plugins not active')
	    return
	
	uurl = msg.get_java_url()
	
	if Settings().get(Settings.SEC_PLUGIN_INTEGRATION, Settings.ONLY_SCOPE) == 'True' and not Facade().mCallBacks.isInScope(uurl):
	    self.__logger.debug('__add_to_queue. Url not enqueued, not in scope: %s.' % uurl)
	    return
	else:
	    self.__logger.debug('__add_to_queue. url queued: %s.' % uurl)
	    Facade().get_msg_queue().put(msg)

	self.__logger.debug('__add_to_queue. END')

    def processHttpMessage(self, toolName, messageIsRequest, messageInfo):
	self.__logger.debug('processHttpMessage. START, toolName=%s' % toolName)

	try:
	    # request messages are commonly uncompleted until response arrives (also containing the request)
	    # even burp complains with java.lang.Exception: java.lang.Exception: request has not yet been issued

	    if not messageIsRequest:
		http_msg = MyHTTPMsg.from_processHttpMessage(toolName, messageIsRequest, messageInfo)

		http_msg.mtype = MyHTTPMsg.BURP_TOOL

		self.__add_to_queue(http_msg)
	    else:
		self.__logger.debug('processHttpMessage. ignored request msg')
	except Exception, e:
	    Facade().formatExceptionInfo("processHttpMessage")
	finally:
	    self.__logger.debug('processHttpMessage. END')

# more sense when modyfing msg
#    def processProxyMessage(self, messageReference, messageIsRequest, remoteHost, remotePort,
#                            serviceIsHttps, httpMethod, url, resourceType, statusCode,
#                            responseContentType, message, interceptAction):
#
#	try:
#	    headers = Facade().mCallBacks.getHeaders(message)
#
#	    self.__logger.debug('processProxyMessage. START, httpMethod=%s, serviceIsHttps=%s, remoteHost=%s, remotePort=%s, url=%s' % (httpMethod, serviceIsHttps, remoteHost, remotePort, url))
#	    self.__logger.debug('\t\tmessageReference=%s, messageIsRequest=%s, resourceType=%s' % (messageReference, messageIsRequest, resourceType))
#	    self.__logger.debug('\t\tstatusCode=%s, headers=%s, responseContentType=%s' % (statusCode, headers, responseContentType))
#
#	    http_msg = MyHTTPMsg.from_ProxyMessage(headers, messageIsRequest, remoteHost, remotePort, serviceIsHttps, httpMethod, url, resourceType, statusCode, responseContentType, message, interceptAction)
#	    http_msg.source = "proxy"
#
#	    if messageIsRequest:
#		http_msg.mtype = MyHTTPMsg.PROXY_REQ
#	    else:
#		http_msg.mtype = MyHTTPMsg.PROXY_RESP
#
#	    self.__add_to_queue(http_msg)
#	except Exception, e:
#	    Facade().formatExceptionInfo("processProxyMessage")
#	    traceback.print_exc(file=sys.stdout)
#	finally:
#	    self.__logger.debug('processProxyMessage. END')
#	    return message

class BurpStrikeMenuItem(IMenuItemHandler):
    def __init__(self):
	self.__logger = logging.getLogger("BurpStrikeMenuItem")

	self.tool_state = Settings().get(Settings.SEC_PLUGIN_INTEGRATION, Settings.ACTIVE)
	self.plugin_state = False

    def menuItemClicked(self, menuItemCaption, messageInfo):
	self.__logger.debug('menuItemClicked. START, %s' % menuItemCaption)

	plname = ""
	if menuItemCaption == "Send to gazpacho":
	    plname = "gazpacho"
	elif menuItemCaption.startswith("Send to sqpyfia"):
	    plname = "sqpyfia-0.9-py2.6"
	elif menuItemCaption == "Dis/Enable burpstrike...":
		self.tool_state = not self.tool_state
		Facade().get_controller().on_enable_tool(self.tool_state)
	elif menuItemCaption == "De/Activate all plugins...":
		self.plugin_state = not self.plugin_state
		Facade().get_controller().on_enable_plugin("All", self.plugin_state)

	if plname:
	    for m in messageInfo:
		msg = MyHTTPMsg.from_IHttpRequestResponse(m)

		plugin = Facade().get_plugins().get(plname)
		plugin.process(msg, None)
	    
	self.__logger.debug('menuItemClicked. END.')
