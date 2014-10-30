'''
burpreqresp.py

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
from basereqresp import BaseRequest
from basereqresp import Response
from basereqresp import IRequest

from framework.facade import Facade

class BurpRequest(BaseRequest, IRequest):
    def __init__(self):
	BaseRequest.__init__(self)

	self.__mCallBacks = Facade().mCallBacks

    def setAuth (self,method,string):
	pass

    def getAuth (self):
	pass

    def setProxy (self,prox):
	pass

    def setConnTimeout (self,time):
	pass

    def setTotalTimeout (self,time):
	pass

    def setFollowLocation(self,value):
	pass

    def parse_response(self, msg):
	self.response = Response()
	self.response.parseResponse(msg)

    def perform(self):
	if self.getHost().find(":") > 0:
	    host, p = self.getHost().split(':')
	    port = int(p)
	else:
	    host = self.getHost()
	    port = 80

	if self.schema == "http":
	    useHttps = False
	elif self.schema == "https":
	    useHttps = True
	else:
	    raise Exception("Unknown HTTP schema")

	#self.__mCallBacks.sendToRepeater(host,port,useHttps,[ord(x) for x in self.getAll()], "test")

	#print "performeando:"
	#print self.getAll()
	#aa = [ord(x) for x in self.getAll()]
	#print "to string...................."
	#print aa
	#print ''.join([chr(x) for x in aa])
	#print "fiinnnto string...................."
	msg = self.__mCallBacks.makeHttpRequest(host, port, useHttps, [ord(x) for x in self.getAll()]) 

	#print "resultado"
	#print msg
	self.parse_response(msg.tostring())


