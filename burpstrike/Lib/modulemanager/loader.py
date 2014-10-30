'''
loader.py

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
'''import imp
import os.path
import logging

from modulemanager.interfaces import IModuleLoader

class ModuleLoader(IModuleLoader):
    """
    handles the load of python extensions.
    """

    def __init__(self, create_inst = True, api = None):
	self.__logger = logging.getLogger("framework.ModuleManager")

	IModuleLoader.__init__(self, create_inst, api)

    def load_egg_from_file(self, fullName):
	self.__logger.debug('load_egg_from_file. START, file=%s' % (fullName,))

	try:
	    import pkg_resources
	except:
	    self.__logger.critical('load_egg_from_file. No support to load .egg plugins. Install package pkg_resources.')
	    return

	pkg_resources.working_set.add_entry(fullName)
	dist_generator = pkg_resources.find_distributions(fullName)
	for dist in dist_generator:
	    try:
		extension_class = dist.load_entry_point("pysqlin.plugins", "plugin")
		# create an instance of the class
		extension = extension_class(self.api)
		return self.__register(extension)
	    except Exception, e :
		self.__logger.critical('load_egg_from_file. Exception, msg=%s' % (e,))
	    
    def load_py_from_file(self, filename):
	"""
	Opens "filename" and loads the python code into a module
	"""

	self.__logger.debug('load_py_from_file. START, file=%s' % (filename,))

	dir, filename = os.path.split(filename)
	fn = os.path.splitext(filename)[0]
	exten_file = None

	try:
	    exten_file, filename, description = imp.find_module(fn, [dir])
	    module = imp.load_module(fn, exten_file, filename, description)
	    return self.__register(module)
	except ImportError, msg:
	    self.__logger.critical('load_py_from_file. Exception, msg=%s' % (msg,))
	except SyntaxError, msg:
	    # incorrect python syntax in file
	    self.__logger.critical('load_py_from_file. Exception, msg=%s' % (msg,))
	finally:
	    if exten_file: exten_file.close()

	self.__logger.debug('load_py_from_file. END, loaded file=%s' % (filename,))
	    
    def __register(self, script):
	"""
	Checks script module and saves it in memory 
	Returns false/true when failure/success
	"""

	# check if the necessary attributes are present
	requiredAttributes = ("load",)
	missingAttrs = []
	for attr in requiredAttributes:
	    if not hasattr(script, attr):
		missingAttrs.append(attr)

	if missingAttrs:
	    self.__logger.debug('__register. Exception: Module must define required attributes')
	    raise Exception('__register. Exception: Module must define required attributes')

	try:
	    if self.create_inst:
		return script.load(self.api)
	    else:
		return script 
	except Exception, msg:
	    self.__logger.critical('__register. Exception, msg=%s' % (msg,))
