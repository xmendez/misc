'''
proxies.py

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
#from framework.baseclass import BStorableData

import logging
from threading import BoundedSemaphore
import sys

import urllib2

from framework.settings import Settings

class BasePlugin:
    def __init__(self, module, name):
	self.module = module

	self.enabled = False
	self.priority = 99
	self.dependencies = []

	self.name = name

    def get_name(self):
        raise NotImplemented

    def get_type(self):
        raise NotImplemented

    def get_description(self):
        raise NotImplemented

    def get_summary(self):
        raise NotImplemented

    def __str__(self):
	return ', '.join(
	    map(lambda x:
		{0: 'PROCESS_REQUEST',
		1: 'PROCESS_RESPONSE'}[x], self.get_type()))

class MyPlugin(BasePlugin):
    def __init__(self, module, name):
	BasePlugin.__init__(self, module, name)

    def get_name(self):
        return self.module.name()

    def get_type(self):
        return self.module.ptype()

    def get_description(self):
        return self.module.description()

    def get_summary(self):
        pass

    def process(self, msg, q):
	self.module.process(msg, q)

class Plugins():
    def __init__(self):
	self.plugins = {}	
	self.__logger = logging.getLogger("framework.Plugins")

    # ------------------------------------------------
    # data functions
    # ------------------------------------------------
    def items(self):
	return self.plugins.items()

    def names(self):
        return self.plugins.keys()

    def get(self, plugin_name):
        return self.plugins[plugin_name]

    def get_list(self, db):
	l = [['Enabled', 'Type', 'Name', 'Description']]

	for pl in self.plugins:
	    l.append([str(pl.enabled), str(pl), pl.get_name(), pl.get_description()])

	return l

    # ------------------------------------------------
    # activation functions
    # ------------------------------------------------
    def disable_all(self):
	for f in self.plugins.values():
	    f.enabled = False

    def enable_all(self):
	for f in self.plugins.values():
	    f.enabled = True

    def set_state(self, name, state):
	self.plugins[name].enabled = state

    def merge_sett(self, data):
	for f, k in [(self.filters[k], k) for k in data.keys() if self.filters.has_key(k)]:
	    f.enabled, f.priority = data[k]

class Result:
    def __init__(self):
	self.issue = None
	self.source = None
	self.detail = None
	self.msg = None

    def __str__(self):
	return "%s\n\tURL:%s\n\tOrigin: %s\n\tDetail: %s\n" % (self.issue, self.msg.get_request().completeUrl, self.source, self.detail)

class Results:
    def __init__(self):
	self.mutex = BoundedSemaphore(value=1)
	self.__issues = []

    def __len__(self):
	return len(self.__issues)

    # ------------------------------------------------
    # data functions
    # ------------------------------------------------
    def add_result(self, result):
	self.mutex.acquire()
	self.__issues.append(result)
	self.mutex.release()

    def get_result(self, index):
	self.mutex.acquire()
	item = self.__issues[index]
	self.mutex.release()

	return item


