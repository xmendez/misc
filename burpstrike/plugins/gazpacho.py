'''
gazpacho.py
#A port from proxystrike plugin gazpacho
#Coded by Carlos del Ojo Elias (deepbit@gmail.com)

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
from framework.interfaces import IPlugin
from framework.baseclass import BPlugin

from reqresp.reqresp import Request

import logging
from urlparse import *
import re
import copy

XSS_SET=[
["<!--%23echo%20var='HTTP_USER_AGENT'%20-->" , "XSSIPWNR" , "SERVER SIDE INCLUDE"],
['XSS\'PWNR', 'XSS\'PWNR', "' (Single Quotes)"],
['XSS"PWNR','XSS"PWNR' ,'" (Double Quotes)'],
['XS<SP>WNR','XS<SP>WNR' ,'<, > (Less than and great than symbols)'],
['XS(SP)WNR','XS(SP)WNR' ,'( ) (Parenthesis)'],
['XS-<SCRIPT>alert(document.cookie)</SCRIPT>-SPWNR','XS-<SCRIPT>alert(document.cookie)</SCRIPT>-SPWNR' ,'Scripting keywords enabled']
]

CARS=['<','>',"'",'(',')']

ENCODING=[
('%hex', 'url encoding (%hex)'),
('%25hex', 'doble url encoding (%25hex)'),
('%2525hex', 'triple url encoding (%25hex)'),
('\\xhex', 'utf8 encoding (\\xhex)'),
('\\u00hex', 'utf8 encoding (\\u00Hex)')
]

STRENCODED="XSSPWNR"
for x,y in ENCODING:
	STRENCODED+="-"+x.replace("hex","41")
STRENCODED+="-XSSPWNR2"


######################################################################################################
######################################################################################################
######################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################

class crossiter(BPlugin, IPlugin):
    ''' Container of request variants ''' 
    def __init__(self, api):
	self.logger = logging.getLogger('plugins.Gazpacho')

	self.posGET=0
	self.posPOST=0

    #    if 'g' in str.lower():
    #	    self.GET=True
    #    if 'p' in str.lower():
    #	    self.POST=True

	self.resultSet=[]
	self.success=False

    def name(self): 
	return "Gazpacho"

    def description(self): 
	return """
	Automatizes the work of detecting blind SQL Injection vulnerabilities.

	* It uses SqPyfia plugin from deepbit\'s ProxyStrike (http://code.google.com/p/proxystrike/).
	"""
    def issue(self):
	return "Cross site scripting"

    def parameters(self): 
	return {}

    def _process(self, msg):
	# reset pq el objeto es el mismo. es lo kiero???
	self.posGET=0
	self.posPOST=0
	self.resultSet=[]
	self.success=False
	#####

	#self.req = msg.get_request()
	self.req = copy.deepcopy(msg.get_request())
	self.GET = True
	self.POST = True
	self.req.addHeader("User-Agent","Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.XSSIPWNR)")

	self.GETvars = self.req.getGETVars()
	self.POSTvars = self.req.getPOSTVars()

	for i in self:
	    if i[0]:
		self.success=True
		self.resultSet.append(i)
	
	result = self.getRAWResults()

	if result is not None and len(result)>0:
	    self.put_results(msg, self.getRAWResults())

    def ptype(self):
	return BPlugin.PROCESS_REQUEST

    def getRAWResults(self):
	if self.success:
	    return self.resultSet
	else:
	    return []

    def __iter__ (self):
	self.logger.debug("================== XSS/SSI ====================\r\n%s\r\n=============================================" % (str(self.req)))
	self.posGET = 0
	self.posPOST = 0
	return self

    def perform(self, pattern, searchPatt,var):
	matchPatt = False

	var.update(pattern)

	for i in range (5):
		try:
			self.req.perform()
			break
		except:
			pass

	var.restore()


	if self.req.response.getContent().count(searchPatt):
		matchPatt = True

	return matchPatt

    def testEncoding(self,var):
	    global STRENCODED

	    var.update(STRENCODED)

	    for i in range (5):
		    try:
			    self.req.perform()
			    break
		    except:
			    pass

	    var.restore()


	    res=[('','Normal Encoding')]
	    encodings=re.findall("XSSPWNR(.*)XSSPWNR2",self.req.response.getContent())
	    if encodings:
		    encodings=encodings[0].replace("%2D","-")
		    encodings=encodings.replace("%2d","-")
		    encodings=re.findall("-[^-]+",encodings)

		    for i in range(len(ENCODING)):
			    try:
				    if encodings[i][1:]=='A':
					    res.append(ENCODING[i])
			    except:
				    print "-----------------EXCEPCION PUTA!----------------"

	    return res
		

    def next(self):
	    if self.GET and self.posGET < len (self.GETvars):
		    var=self.GETvars[self.posGET]
		    method="GET"
		    self.posGET+=1

	    elif self.POST and self.posPOST < len (self.POSTvars):
		    var=self.POSTvars[self.posPOST]
		    method="POST"
		    self.posPOST+=1

	    else:
		    self.logger.debug("++++++++++++++++++ FINISH XSS/SSI +++++++++++++++++\r\n%s\r\n+++++++++++++++++++++++++++++++++++++++++++++++++++" % (str(self.req)))
		    raise StopIteration

	    if var.name in ["__LASTFOCUS", "__EVENTTARGET", "__EVENTARGUMENT", "__VIEWSTATE", "__ASYNCPOST"]:
	    #if var.name in ["__LASTFOCUS", "__EVENTTARGET", "__EVENTARGUMENT", "__VIEWSTATE", "__ASYNCPOST", "ctl00%24ContentPlaceHolder1%24OrderList1%24txtProductRocheTo%24tb"]:
		    self.logger.debug("++++++++++++++++++ Variable prohibida: %s => FINISH XSS/SSI +++++++++++++++++" % (str(var.name)))
		    return (False,method,var.name,[],var.value)

	    #if var.name not in ["ctl00%24ContentPlaceHolder1%24OrderList1%24txtProductRocheTo%24tb"]:
	    #	self.logger.debug("++++++++++++++++++ Variable prohibida2: %s => FINISH XSS/SSI +++++++++++++++++" % (str(var.name)))
	    #	return (False,method,var.name,[],var.value)

	    var.update("XSSPWNR")

	    for i in range(5):
		    #try:
		    self.req.perform()
		    #break
		#    except:
		#	    self.logger.debug('\tError performing request')
		#	    pass

	    var.restore()
    
	    self.logger.debug('\tTrying %s...' % (var.name))
	    

	    if self.req.response.getContent().count("XSSPWNR"):
		    self.logger.debug('\t\t%s: Single string injectable' % (var.name))
		    setout=[]

		    AVAIL_ENCS=self.testEncoding(var)
    
		    
		    for x,z,y in XSS_SET:
			    for enco, desc in AVAIL_ENCS:
				    xx = ''
				    if enco:
					    for car in x:
						    xx += enco.replace("hex",hex(ord(car))[2:])
				    else:
					    xx=x

				    self.logger.debug('\t\tTrying %s (%s) (%s)...' % (var.name, y, desc))
				    if self.perform(xx, z,var):
					    self.logger.debug('\t\t%s: %s (%s)' % (var.name,y, desc))
					    setout.append(y + " " + "(%s)" %(desc))

		    #			self.logger.debug('\t\tIf encoding works we dont try next...')
					    break;

		    return (True,method,var.name,setout,var.value)
	    else:
		    return (False,method,var.name,[],var.value)



def load(api):
    return  crossiter(api)
