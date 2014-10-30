'''
baseclass.py

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
from framework.facade import Facade
from framework.proxies import Result

#class BStorableData:
#    def save(self, filename):
#	output = None
#	try:
#	    output = open(filename, 'w+b')
#	    pickle.dump(self, output)
#	except IOError, e:
#	    raise e
#	finally:
#	    if output: output.close()
#
#    def load(self, path):
#	pkl_file = None
#	pkl = None
#
#	try:
#	    pkl_file = open(path, 'r+b')
#	    pkl = pickle.load(pkl_file)
#	except IOError, e:
#	    raise e
#	except EOFError, e:
#	    raise e
#	finally:
#	    if pkl_file: pkl_file.close()
#
#	return pkl
#
#    def _has_item(self, key):
#	raise NotImplemented
#
#    def merge(self, mandatory_data):
#	# self.data key exist = mandatory_data value
#	for k, v in [(k, v) for k, v in mandatory_data.items() if not self._has_item(k)]:
#	    self.data[k] = v

class BPlugin:
    PROCESS_REQUEST, PROCESS_RESPONSE = range(2)

    def generate_alert(self, msg):
	Facade().issue_alert(msg)

    def put_results(self, msg, item):
	r = Result()
	r.source = self.name()
	r.issue = self.issue()
	r.detail = item
	r.msg = msg

	Facade().issue_alert("New issue %s from %s" % (r.issue, r.source))
	Facade().get_results().add_result(r)

    def process(self, msg, q):
	try:
	    self._process(msg)
	except Exception, e:
	    Facade().formatExceptionInfo("BPLugin. process")
	finally:
	    if q:
		q.get()
		q.task_done()
