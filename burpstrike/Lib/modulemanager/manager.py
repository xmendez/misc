'''
manager.py

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

import os.path
import logging

class ModuleManager:
    """
    handles the load of python extensions.
    """

    def __init__(self, module_registrant, module_loader, base_path, dir_name):
	self.__logger = logging.getLogger("framework.ModuleManager")

	self.module_registrant = module_registrant
	self.module_loader = module_loader
	self.base_path = base_path
	self.dir_name = dir_name

	self.load_all(dir_name)

    def load_all(self, dir_name):
	"""
	loads all plugins and creates a loaded list of scripts from directory plugins like:
	[ ( category,[script1, script2,...] ), (category2,[script1, (subcategory,[script1,script2]),...]) ]
	"""
	scripts = []

	current = os.path.join(self.base_path, dir_name)
	if os.path.isdir(current):
	    l = self.__load_dir_tree(current)
	    scripts.append((current,l))
	    self.module_registrant.end_loading(scripts)

    def __load_dir_tree(self, dir):
	l=[]

	self.__logger.debug('__load_dir_tree. START dir=%s', dir)

        for f in os.listdir(dir):
	    current = os.path.join(dir, f)
	    if os.path.isfile(current) and f.endswith("py"):
		self.module_registrant.register(
		    self.build_id(current),
		    self.module_loader.load_py_from_file(current)
		)
		l.append(os.path.splitext(f)[0])
	    elif os.path.isfile(current) and f.endswith("egg"):
		self.module_registrant.register(
		    self.build_id(current),
		    self.module_loader.load_egg_from_file(current)
		)
		l.append(os.path.splitext(f)[0])
	    elif os.path.isdir(current):
		ret = self.__load_dir_tree(current)
		if ret: l.append( (f,ret) )
	return l

    def build_id(self, filename):
	dir, filename = os.path.split(filename)

	fn = os.path.splitext(filename)[0]

	id = dir.split(self.dir_name)[1][1:] + '/' + fn
	if id.startswith('/'): id = id[1:]

	return id
