'''
registrant.py

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
import logging

from modulemanager.interfaces import IModuleRegistrant
from framework.proxies import MyPlugin

class BRegister():
    def __init__(self, plugins):
	self.plugins = plugins


class MyPluginRegister(IModuleRegistrant, BRegister):
#class Plugins(IModuleLoader, BStorableData):
    def __init__(self, plugins):
	BRegister.__init__(self, plugins)
	self.__logger = logging.getLogger("framework.MyPluginRegister")

#    # ------------------------------------------------
#    # Storable data
#    # ------------------------------------------------
#    def _has_item(self, k):
#	return self.plugins.has_key(k)

    # ------------------------------------------------
    # module loading
    # ------------------------------------------------
    def register(self, id, module):
	self.__logger.debug('register. START, id=%s' % (id))

	#self.plugins[module.name()] = module
	if not module: return
	self.plugins.plugins[id] = MyPlugin(module, id)

    def end_loading(self, list):
	pass

