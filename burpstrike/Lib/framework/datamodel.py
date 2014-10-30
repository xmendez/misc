'''
datamodel.py

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
import pickle
from UserDict import UserDict

class DataModel:
    def __init__(self):
	self.plugins_data = PluginsData()

    def save(self, filename):
	output = None
	try:
	    output = open(filename, 'w+b')
	    pickle.dump(self, output)
	except IOError, e:
	    raise e
	finally:
	    if output: output.close()

    def load(self, path):
	pkl_file = None
	pkl = None

	try:
	    pkl_file = open(path, 'r+b')
	    pkl = pickle.load(pkl_file)
	except IOError, e:
	    raise e
	except EOFError, e:
	    raise e
	finally:
	    if pkl_file: pkl_file.close()

	return pkl

class PluginsData(UserDict):
    def __init__(self, data = {}):
	self.data = data

    def set(self, mandatory_data):
	for k, v in mandatory_data.items():
	    self.data[k] = v

    def merge(self, non_mandatory_data):
	# non_mandatory_data has current extensive data whitout configured values, self.data has (or not) configured values

	# non_mandatory_data key exist => value = self data value
	for k, v in [(k, v) for k, v in self.data.items() if self.non_mandatory_data.has_key(k)]:
	    self.non_mandatory_data[k].enabled = v

	# self.data key not exist = non_mandatory_data value
	for k, v in [(k, v) for k, v in mandatory_data.items() if not self.data.has_key(k)]:
	    self.data[k] = v.enabled

