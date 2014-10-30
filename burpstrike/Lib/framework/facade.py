'''
facade.py

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
from threading import BoundedSemaphore
from Queue import Queue
import logging
import sys
import traceback

from framework.datamodel import DataModel
from modulemanager.manager import ModuleManager
from modulemanager.loader import ModuleLoader
from modulemanager.registrant import MyPluginRegister
from patterns.singleton import Singleton
from framework.proxies import Plugins
from framework.proxies import Results
from framework.settings import Settings

class Facade():
    __metaclass__ = Singleton


    def __init__(self):
	self.__logger = logging.getLogger("framework.facade")

	self.mCallBacks = None
	self.mutex = BoundedSemaphore(value=1)

	self.controller = None

	# Messages queue
	self.__qmsg = Queue()
	self.jman = None

	# results storage
	self.__results = Results()

	# load plugins
	self.__logger.info("* Loading plugins")
	self.load_plugins()

	# load session
	self.__logger.info("* Loading session")
	self.__cur_session = DataModel()
	if Settings().get(Settings.SEC_GRL, Settings.AUTO_SESSION) == 'True':
	    try:
		self.__cur_session = self.load_session()
	    except Exception:
		pass

    # ------------------------------------------------
    # session management
    # ------------------------------------------------
    def load_session(self, path = None):
	if not path:
	    path = Settings().get(Settings.SEC_GRL, Settings.AUTO_SAVE_FILE)

	self.__logger.debug('load_session. START path=%s', path)

	tmp = self.__cur_session.load(path)
	tmp.plugin_data.merge(self.__plugins.plugins)

	return tmp

    def save_session(self, filename = None):
	if filename is None:
	    filename = Settings().get(Settings.SEC_GRL, Settings.AUTO_SAVE_FILE)

	self.__logger.debug('save_session. START filename=%s', filename)
	self.__cur_session.plugin_data.set(self.__plugins.plugins)


	self.__cur_session.save(filename)

    # ------------------------------------------------
    # Burp interaction
    # ------------------------------------------------
    def load_plugins(self):
	# load plugins
	self.__logger.info("load_plugins. START.")
	self.__plugins = Plugins()
	ModuleManager(MyPluginRegister(self.__plugins), ModuleLoader(), Settings().path_to_program_dir(), 'plugins')

	self.__logger.info("load_plugins. END.")


    # ------------------------------------------------
    # Burp interaction
    # ------------------------------------------------
#    def processProxyMessage(self, messageReference, messageIsRequest, remoteHost, remotePort, serviceIsHttps, httpMethod, url, resourceType, statusCode, responseContentType, message, interceptAction): 
#	headers = self.mCallBacks.getHeaders(message)
#
#	self.__logger.debug("processProxyMessage. START ")
#
#        #print "yo q se %s" % ' '.join(headers[0].split(' ')[2:])
#	#print "messageReference %s" % messageReference
#	#print "messageIsRequest %s" % messageIsRequest
#	#print "remoteHost %s" % remoteHost
#	#print "remotePort %s" % remotePort
#	#print "serviceIsHttps %s" % serviceIsHttps
#	#print "url %s" % url
#	#print "httpMethod %s" % httpMethod
#	#print "resourceType %s" % resourceType
#	#print "statusCode %s" % statusCode
#	#print "responseContentType %s" % responseContentType
#	#print "message %s" % message
#	#print "headers %s" % headers
#	#print "headers[0] %s" % headers[0]
#	#print "message.tostring %s" % message.tostring()
#
#
#	http_msg = MyHTTPMsg.from_ProxyMessage(headers, messageIsRequest, remoteHost, remotePort, serviceIsHttps, httpMethod, url, resourceType, statusCode, responseContentType, message, interceptAction)
#	self.__qmsg.put(http_msg)
#
#	self.__logger.debug("processProxyMessage. END")

    def issue_alert(self, msg):
	self.mutex.acquire()

	if not self.mCallBacks:
	    raise Exception('Facade: Need to define mCallBacks first.')
	self.mCallBacks.issueAlert(msg)

	self.mutex.release()

    def exit_burp(self):
	self.mCallBacks.exitSuite(False)

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
	self.__logger.error("Unhandled exception at %s: %s" % (where, s))

	print s

    # ------------------------------------------------
    # proxies interfaces
    # ------------------------------------------------
    def get_msg_queue(self):
	return self.__qmsg

    def get_plugins(self):
	return self.__plugins

    def get_results(self):
	return self.__results

    def get_jobman(self):
	return self.jman

    def get_controller(self):
	return self.controller

