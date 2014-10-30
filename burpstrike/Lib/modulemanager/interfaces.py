'''
interfaces.py

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
'''class IModuleLoader:
    def __init__(self, create_inst = True, api = None):
	self.create_inst = create_inst
	self.api = api

    def load_py_from_file(self, filename):
	raise NotImplemented

    def load_egg_from_file(self, filename):
	raise NotImplemented
	
class IModuleRegistrant:
    def register(self, id, module):
	raise NotImplemented

    def end_loading(self, categories):
	raise NotImplemented

