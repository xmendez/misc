'''
jobman.py

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

from threading import Thread
#from threading import Timer
from Queue import Queue
from collections import defaultdict
#from threading import BoundedSemaphore
import logging
import time

from framework.facade import Facade
from framework.baseclass import BPlugin
from framework.settings import Settings
from framework.myhttp import MyHTTPMsg

class JobMan(Thread):
    def __init__(self):
        Thread.__init__(self)

	self.__logger = logging.getLogger("framework.JobMan")

	self.__walking_threads = Queue(int(Settings().get(Settings.SEC_PERF, Settings.MAX_THREADS)))

	#self.mutex = BoundedSemaphore(value=1)

	# statistics timer
	self.__watch = True
	self.__watch_man = Thread(target = self.__watchman)
	#self.__watch_man.start()

	self.__processed = 0

	# cache map
	self.__cache_map = defaultdict(list)

    # ------------------------------------------------
    # url cache control
    # ------------------------------------------------
    def flush_cache(self):
	self.__cache_map = defaultdict(list)

    def msg_in_cache(self, msg, plugin_name):
	self.__logger = logging.getLogger('msg_in_cache. START')

	req = msg.get_request()
	key = req.urlWithoutVariables

	dicc = {}

	for j in [i.name for i in req.getGETVars()]:
	    dicc[j]=True

	for j in [i.name for i in req.getPOSTVars()]:
	    dicc[j]=True

	vars = dicc.keys()

	#if not vars:
	#    return False

	vars.sort()

	key += "-" + "-".join(vars)

	# first hit
	if not self.__cache_map.has_key(key):
	    self.__cache_map[key].append(plugin_name)
	    ret = False
	else:
	    if not plugin_name in self.__cache_map[key]:
		self.__cache_map[key].append(plugin_name)
		ret = False
	    else:
		ret = True

	self.__logger = logging.getLogger('msg_in_cache. END')
	return ret

    # ------------------------------------------------
    # threading
    # ------------------------------------------------
    def __watchman(self):
	while self.__watch:
	    time.sleep(10)
	    print "Queue size: %d" % Facade().get_msg_queue().qsize()
	    print "Walking threads queue: %d" % self.__walking_threads.qsize()
	    print "Processed msgs: %d" % self.__processed

    def stop(self):
	self.__logger.debug('stop. START')
	self.__logger.debug('waiting for enqueued tasks.')
	self.__walking_threads.join()
	self.__logger.debug('waiting for watchman.')
	self.__watch = False
	self.__watch_man.join()
	self.__logger.debug('stop. END')
	
    def run(self):
	try:
	    while 1:
		self.__logger.debug('Run. waiting for messages......................................')
		# http://bugs.python.org/issue1360
		msg = Facade().get_msg_queue().get(True, 365 * 24 * 60 * 60)

		self.__processed += 1

		excluded_req_tools = Settings().get(Settings.SEC_PLUGIN_INTEGRATION, Settings.EXCLUDED_REQ_TOOLS).split(',')
		excluded_resp_tools = Settings().get(Settings.SEC_PLUGIN_INTEGRATION, Settings.EXCLUDED_RESP_TOOLS).split(',')

		for name, plugin in Facade().get_plugins().items():
		    if plugin.enabled is not True:
			self.__logger.debug('Run. Plugin %s not enabled.' % name)
			continue

		    # exclusions
		    if plugin.get_type() == BPlugin.PROCESS_REQUEST and msg.source in excluded_req_tools:
			self.__logger.debug('Run. Request in excluded sources. url=%s, type=%d, source=%s, excluded=%s' % (msg.get_url(), msg.mtype, msg.source, excluded_req_tools))
			continue
		    elif plugin.get_type() == BPlugin.PROCESS_RESPONSE and msg.source in excluded_resp_tools:
			self.__logger.debug('Run. Response in excluded sources. url=%s, type=%d, source=%s, excluded=%s' % (msg.get_url(), msg.mtype, msg.source, excluded_resp_tools))
			continue
		    elif plugin.get_type() == BPlugin.PROCESS_REQUEST and not msg.mtype == MyHTTPMsg.BURP_TOOL:
			self.__logger.debug('Run. Request type %d not processed. url=%s' % (msg.mtype, msg.get_url()))
			continue
		    elif plugin.get_type() == BPlugin.PROCESS_RESPONSE and not (msg.mtype == MyHTTPMsg.BURP_TOOL or msg.mtype == MyHTTPMsg.BSTRIKE):
			self.__logger.debug('Run. Response not processed. type=%d, source=%s, excluded=%s' % (msg.mtype, msg.source, excluded_resp_tools))
			continue
		    # current cache only valid for req? => processing all responses!!
		    elif plugin.get_type() == BPlugin.PROCESS_REQUEST and self.msg_in_cache(msg, name):
			self.__logger.debug('Run. Request already processed by %s.' % name)
			continue
		    else:
			self.__logger.debug('processing message. plugin: %s ...' % name)
			th = Thread(target = plugin.process, kwargs={"msg": msg, "q": self.__walking_threads})

			self.__logger.debug('putting task. plugin: %s ...' % name)
			self.__walking_threads.put(th)

			self.__logger.debug('starting thread. plugin: %s ...' % name)
			th.start()
	except Exception, e:
	    Facade().formatExceptionInfo("JobMan")
	finally:
	    self.stop()
