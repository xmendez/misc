#Covered by GPL V2.0
#Coded by Carlos del Ojo Elias (deepbit@gmail.com)
#inheritance modification by Xavi Mendez aka Javi
from time import localtime, strftime
import threading
from datetime import date

from basereqresp import BaseRequest
from basereqresp import Response
from basereqresp import IRequest

try:
	from TextParser import *
except:
	pass

try:
    import pycurl
except ImportError:
    sys.stderr.write('You need to install pycurl first\n')
    sys.exit(255)

mutex=1
Semaphore_Mutex=threading.BoundedSemaphore(value=mutex)
REQLOG=True


class PyCurlRequest(BaseRequest, IRequest):
    def __init__(self):
	BaseRequest.__init__(self)
	self.__performHead=""
	self.__performBody=""

	self.__proxy=None
	self.__timeout=None
	self.__totaltimeout=None

	self.followLocation=False

	self.__authMethod=None
	self.__userpass=""


############## Autenticacion ###########################
	def setAuth (self,method,string):
		self.__authMethod=method
		self.__userpass=string

	def getAuth (self):
		return self.__authMethod, self.__userpass

############### PROXY ##################################
    def setProxy (self,prox):
	    self.__proxy=prox

############## TIMEOUTS ################################
    def setConnTimeout (self,time):
	    self.__timeout=time

    def setTotalTimeout (self,time):
	    self.__totaltimeout=time

    def header_callback(self,data):
	    self.__performHead+=data

    def body_callback(self,data):
	    self.__performBody+=data

############### FOLLOW LOCATION ########################
    def setFollowLocation(self,value):
	    self.followLocation=value
	
    def head(self):
	    conn=pycurl.Curl()
	    conn.setopt(pycurl.SSL_VERIFYPEER,False)
	    conn.setopt(pycurl.SSL_VERIFYHOST,1)
	    conn.setopt(pycurl.URL,self.completeUrl)

	    conn.setopt(pycurl.HEADER, True) # estas dos lineas son las que importan
	    conn.setopt(pycurl.NOBODY, True) # para hacer un pedido HEAD

	    conn.setopt(pycurl.WRITEFUNCTION, self.header_callback)
	    conn.perform()

	    rp=Response()
	    rp.parseResponse(self.__performHead)
	    self.response=rp

    def perform(self):
	    global REQLOG
	    if REQLOG:
		    Semaphore_Mutex.acquire()
		    f=open("/tmp/REQLOG-%d-%d" % (date.today().day,date.today().month) ,"a")
		    f.write( strftime("\r\n\r\n############################ %a, %d %b %Y %H:%M:%S\r\n", localtime()))
		    f.write(self.getAll())
		    f.close()
		    Semaphore_Mutex.release()


	    self.__performHead=""
	    self.__performBody=""
	    self._headersSent=""

	    conn=pycurl.Curl()
	    conn.setopt(pycurl.SSL_VERIFYPEER,False)
	    conn.setopt(pycurl.SSL_VERIFYHOST,1)
	    conn.setopt(pycurl.URL,self.completeUrl)

	    if self.__authMethod or self.__userpass:
		    if self.__authMethod=="basic":
			    conn.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
		    elif self.__authMethod=="ntlm":
			    conn.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_NTLM)
		    elif self.__authMethod=="digest":
			    conn.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_DIGEST)
		    conn.setopt(pycurl.USERPWD, self.__userpass)

	    if self.__timeout:
		    conn.setopt(pycurl.CONNECTTIMEOUT, self.__timeout)
		    conn.setopt(pycurl.NOSIGNAL, 1)

	    if self.__totaltimeout:
		    conn.setopt(pycurl.TIMEOUT, self.__totaltimeout)
		    conn.setopt(pycurl.NOSIGNAL, 1)

	    conn.setopt(pycurl.WRITEFUNCTION, self.body_callback)
	    conn.setopt(pycurl.HEADERFUNCTION, self.header_callback)

	    if self.__proxy!=None:
		    conn.setopt(pycurl.PROXY,self.__proxy)
		    if self._headers.has_key("Proxy-Connection"):
			    del self._headers["Proxy-Connection"]

	    conn.setopt(pycurl.HTTPHEADER,self._getHeaders())
	    if self.method=="POST":
		    conn.setopt(pycurl.POSTFIELDS,self.postdata)
    
	    conn.perform()

	    rp=Response()
	    rp.parseResponse(self.__performHead)
	    rp.addContent(self.__performBody)

	    if self.schema=="https" and self.__proxy:
		    self.response=Response()
		    self.response.parseResponse(rp.getContent())
	    else:
		    self.response=rp

	    if self.followLocation:
		    if self.response.getLocation():
			    a=PyCurlRequest()
			    newurl=self.createPath(self.response.getLocation())
			    a.setUrl(newurl)
			    #url=urlparse(self.response.getLocation())
			    #if not url[0] or not url[1]:
			    #	sc=url[0]
			    #	h=url[1]
			    #	if not sc:
			    #		sc=self.schema
			    #	if not h:
			    #		h=self.__host
			    #	a.setUrl(urlunparse((sc,h)+url[2:]))
			    #	self.__finalurl=urlunparse((sc,h)+url[2:])
			    #else:
			    #	a.setUrl(self.response.getLocation())
			    #	self.__finalurl=self.response.getLocation()
			    a.setProxy(self.__proxy)

			    ck=""

			    if "Cookie" in self._headers:
				    ck=self._headers["Cookie"]
			    if self.response.getCookie():
				    if ck:
					    ck+=";"+self.response.getCookie()
				    else:
					    ck=self.response.getCookie()

			    if ck:
				    self.addHeader("Cookie",ck)

			    a.perform()
			    self.response=a.response


