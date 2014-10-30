#Covered by GPL V2.0
#Coded by Carlos del Ojo Elias (deepbit@gmail.com)

#inheritance modification by Xavi Mendez aka Javi


from urlparse import *
import gzip
import StringIO
import string
import re


try:
	from TextParser import *
except:
	pass

class Variable:
	def __init__(self,name,value="",extraInfo=""):
		self.name=name
		self.value=value
		self.initValue=value
		self.extraInfo=extraInfo

	def restore(self):
		self.value=self.initValue

	def change(self,newval):
		self.initValue=self.value=newval

	def update(self,val):
		self.value=val

	def append(self,val):
		self.value+=val

	def __str__(self):
		return "[ %s : %s ]" % (self.name,self.value)

class VariablesSet:
	def __init__(self):
		self.variables=[]
		self.boundary=None

	def names(self):
		dicc=[]
		for i in self.variables:
			dicc.append(i.name)

		return dicc

	def existsVar(self,name):
		return name in self.names()

	def addVariable(self,name,value="",extraInfo=""):
		self.variables.append(Variable(name,value,extraInfo))


	def getVariable(self,name):
		dicc=[]
		for i in self.variables:
			if i.name==name:
				dicc.append(i)

		if len(dicc)>1:
			raise Exception, "Variable exists more than one time!!! :D" % (name)

		if not dicc:
			var=Variable(name)
			self.variables.append(var)
			return var

		return dicc[0]

	
	def urlEncoded(self):
		return "&".join(["=".join([i.name,i.value]) for i in self.variables])

	def parseUrlEncoded(self,cad):
		dicc=[]

		for i in cad.split("&"):
			if i:
				list=i.split("=",1)
				if len (list)==1:
					dicc.append(Variable(list[0],""))
				elif len (list)==2:
					dicc.append(Variable(list[0],list[1]))

		self.variables=dicc

	def multipartEncoded(self):
		if not self.boundary:
			self.boundary="---------------------------D33PB1T0R3QR3SP0B0UND4RY2203"
		pd=""
		pos=0
		for i in self.variables:
			pd+="--"+self.boundary+"\r\n"
			pd+="%s\r\n\r\n%s\r\n" % ("\r\n".join(i.extraInfo),i.value)
		pd+="--"+self.boundary+"--\r\n"
		return pd

	def parseMultipart(self,cad,boundary):
		self.boundary=boundary
		dicc=[]
		tp=TextParser()
		tp.setSource("string",cad)

		while True:
			headers=[]
			if not tp.readUntil("name=\"([^\"]+)\""):
				break
			var=tp[0][0]
			headers.append(tp.lastFull_line.strip())
			while True:
				tp.readLine()
				if tp.search("^([^:]+): (.*)$"):
					headers.append(tp.lastFull_line.strip())
				else:
					break

			value=""
			while True:
				tp.readLine()
				if not tp.search(boundary):
					value+=tp.lastFull_line
				else:
					break

			if value[-2:]=="\r\n":
				value=value[:-2]


			dicc.append(Variable(var,value,headers))

		self.variables=dicc

class Response:

	def __init__ (self,protocol="",code="",message=""):
		self.protocol=protocol         # HTTP/1.1
		self.code=code			# 200
		self.message=message		# OK
		self._headers=[]		# bueno pues las cabeceras igual que en la request
		self.__content=""		# contenido de la response (si i solo si Content-Length existe)
		self.md5=""             # hash de los contenidos del resultado
		self.charlen=""         # Cantidad de caracteres de la respuesta

	def addHeader (self,key,value):
		k=string.capwords(key,"-")
		self._headers+=[(k,value)]

	def delHeader (self,key):
		for i in self._headers:
			if i[0].lower()==key.lower():
				self._headers.remove(i)


	def addContent (self,text):
		self.__content=self.__content+text

	def __getitem__ (self,key):
		for i,j in self._headers:
			if key==i:
				return  j
		print "Error al obtener header!!!"

	def getCookie (self):
		str=[]
		for i,j in self._headers:
			if i.lower()=="set-cookie":
				str.append(j.split(";")[0])
		return  "; ".join(str)


	def has_header (self,key):
		for i,j in self._headers:
			if i.lower()==key.lower():
				return True
		return False
	
	def getLocation (self):
		for i,j in self._headers:
			if i.lower()=="location":
				return j
		return None

	def header_equal (self,header,value):
		for i,j in self._headers:
			if i==header and j.lower()==value.lower():
				return True
		return False

	def getHeaders (self):
		return self._headers

	def getContent (self):
		return self.__content

	def getTextHeaders(self):
		string=str(self.protocol)+" "+str(self.code)+" "+str(self.message)+"\r\n"
		for i,j in self._headers:
			string+=i+": "+j+"\r\n"

		return string

	def getAll (self):
		string=self.getTextHeaders()+"\r\n"+self.getContent()
		return string

	def Substitute(self,src,dst):
		a=self.getAll()
		b=a.replace(src,dst)
		self.parseResponse(b)

	def getAll_wpost (self):
		string=str(self.protocol)+" "+str(self.code)+" "+str(self.message)+"\r\n"
		for i,j in self._headers:
			string+=i+": "+j+"\r\n"
		return string


	def parseResponse (self,rawResponse,type="curl"):
		self.__content=""
		self._headers=[]

		tp=TextParser()
		tp.setSource("string",rawResponse)

		while True:
			tp.readUntil("(HTTP\S*) ([0-9]+)")

			try:
				self.protocol=tp[0][0]
			except:
				self.protocol="unknown"

			try:
				self.code=tp[0][1]
			except:
				self.code="0"

			if self.code!="100":
				break


		self.code=int(self.code)

		while True:
			tp.readLine()
			if (tp.search("^([^:]+): ?(.*)$")):
				self.addHeader(tp[0][0],tp[0][1])
			else:
				break

		while tp.skip(1):
			self.addContent(tp.lastFull_line)

		if type=='curl':
			self.delHeader("Transfer-Encoding")

		if self.header_equal("Transfer-Encoding","chunked"):
			result=""
			content=StringIO.StringIO(self.__content)
			hexa=content.readline()	
			nchunk=int(hexa.strip(),16)
			
			while nchunk:
				result+=content.read(nchunk)
				content.readline()
				hexa=content.readline()	
				nchunk=int(hexa.strip(),16)

			self.__content=result

		if self.header_equal("Content-Encoding","gzip"):
			compressedstream = StringIO.StringIO(self.__content)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			body=gzipper.read()
			self.__content=body
			self.delHeader("Content-Encoding")

class IRequest:
    def perform(self):
	raise NotImplemented

    def setProxy (self,prox):
	raise NotImplemented

    def setConnTimeout (self,time):
	raise NotImplemented

    def setTotalTimeout (self,time):
	raise NotImplemented

    def setFollowLocation(self,value):
	raise NotImplemented

    def setAuth (self,method,string):
	raise NotImplemented

    def getAuth (self):
	raise NotImplemented

class BaseRequest:

	def __init__ (self):

		self.__host=None	  		# www.google.com:80
		self.__path=None			# /index.php
		self.__params=None			# Mierdaza de index.php;lskjflkasjflkasjfdlkasdf?
		self.schema="http" 			# http

		##### Variables calculadas por getters NO SE PUEDEN MODIFICAR
		# self.urlWithoutPath                    # http://www.google.es
		# self.pathWithVariables    	         	# /index.php?a=b&c=d
		# self.urlWithoutVariables=None 	 		# http://www.google.es/index.php
		# self.completeUrl=""					# http://www.google.es/index.php?a=b
		# self.finalUrl=""					# Url despues de hacer el FollowLocation
		# self.postdata=""		# Datos por POST, toto el string
		################

		self.ContentType="application/x-www-form-urlencoded"      # None es normal encoding 
		self.multiPOSThead={}

		self.__variablesGET=VariablesSet()
		self.__variablesPOST=VariablesSet()

		# diccionario, por ejemplo headers["Cookie"]
		self._headers={'Content-Type': 'application/x-www-form-urlencoded',
				"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1 HECHO EN LA BASE)"
		}
		
		self.response=None		# Apunta a la response que produce dicha request

		################### lo de debajo no se deberia acceder directamente

		self.time=None    		# 23:00:00
		self.ip=None	   		# 192.168.1.1
		self.method="GET" 		# GET o POST (EN MAYUSCULAS SI PUEDE SER)
		self.protocol="HTTP/1.1"	# HTTP/1.1

		self.description=""     # For temporally store imformation

		self.__finalurl=""


	def __str__(self):
		str="[ URL: %s" % (self.completeUrl)
		if self.method=="POST":
			str+=" - POST: \"%s\"" % self.postdata
		if "Cookie" in self._headers:
			str+=" - COOKIE: \"%s\"" % self._headers["Cookie"]
		str+=" ]"
		return str

	def getHost(self):
		return self.__host

	def getXML(self,obj):
		r=obj.createElement("request")
		r.setAttribute("method",self.method)
		url=obj.createElement("URL")
		url.appendChild(obj.createTextNode(self.completeUrl))
		r.appendChild(url)
		if self.method=="POST":
			pd=obj.createElement("PostData")
			pd.appendChild(obj.createTextNode(self.postdata))
			r.appendChild(pd)
		if "Cookie" in self._headers:
			ck=obj.createElement("Cookie")
			ck.appendChild(obj.createTextNode(self._headers["Cookie"]))
			r.appendChild(ck)

		return r
	
	def __getattr__ (self,name):
		if name=="urlWithoutVariables":
			return urlunparse((self.schema,self.__host,self.__path,'','',''))
		elif name=="pathWithVariables":
			return urlunparse(('','',self.__path,'',self.__variablesGET.urlEncoded(),''))
		elif name=="completeUrl":
			return urlunparse((self.schema,self.__host,self.__path,self.__params,self.__variablesGET.urlEncoded(),''))
		elif name=="finalUrl":
			if self.__finalurl:
				return self.__finalurl
			return self.completeUrl
		elif name=="urlWithoutPath":
			return "%s://%s" % (self.schema,self._headers["Host"])
		elif name=="path":
			return self.__path
		elif name=="postdata":
			if self.ContentType=="application/x-www-form-urlencoded":
				return self.__variablesPOST.urlEncoded()
			elif self.ContentType=="multipart/form-data":
				return self.__variablesPOST.multipartEncoded()
			else:
				return self.__uknPostData
		else:
			raise AttributeError

	def setUrl (self, urltmp):
		self.__variablesGET=VariablesSet()
		self.schema,self.__host,self.__path,self.__params,variables,f=urlparse(urltmp)
		self._headers["Host"]=self.__host

		if variables:
			self.__variablesGET.parseUrlEncoded(variables)
			
############## TRATAMIENTO VARIABLES GET & POST #########################

	def existsGETVar(self,key):
		return self.__variablesGET.existsVar(key)

	def existPOSTVar(self):
		return self.__variablesPOST.existsVar(key)


	def setVariablePOST (self,key,value):
		self.method="POST"
		v=self.__variablesPOST.getVariable(key)
		v.update(value)
#		self._headers["Content-Length"]=str(len(self.postdata))

	def setVariableGET (self,key,value):
		v=self.__variablesGET.getVariable(key)
		v.update(value)

	def getGETVars(self):
		return self.__variablesGET.variables

	def getPOSTVars(self):
		return self.__variablesPOST.variables

	def setPostData (self,pd,boundary=None):
		self.__variablesPOST=VariablesSet()
		self.method="POST"
		if self.ContentType=="application/x-www-form-urlencoded":
			self.__variablesPOST.parseUrlEncoded(pd)
		elif self.ContentType=="multipart/form-data":
			self.__variablesPOST.parseMultipart(pd,boundary)
		else:
			self.__uknPostData=pd

############################################################################

	def addHeader (self,key,value):
		k=string.capwords(key,"-")
		if k.lower() not in ["accept-encoding","content-length","if-modified-since","if-none-match"]:
			self._headers[k]=value

	def delHeader (self,key):
		k=string.capwords(key,"-")
		del self._headers[k]

	def __getitem__ (self,key):
		k=string.capwords(key,"-")
		if k in self._headers:
			return self._headers[k]
		else:
			return ""

	def _getHeaders(self):
		list=[]
		for i,j in self._headers.items():
			list+=["%s: %s" % (i,j)]
		return list

	def createPath(self,newpath):
		'''Creates new url from a location header || Hecho para el followLocation=true'''
		if "http" in newpath[:4].lower():
			return newpath

		parts=urlparse(self.completeUrl)
		if "/" != newpath[0]:
			newpath="/".join(parts[2].split("/")[:-1])+"/"+newpath

		return urlunparse([parts[0],parts[1],newpath,'','',''])

	######### ESTE conjunto de funciones no es necesario para el uso habitual de la clase

	def getAll (self):
		pd=self.postdata
		string=str(self.method)+" "+str(self.pathWithVariables)+" "+str(self.protocol)+"\n"
		for i,j in self._headers.items():
			string+=i+": "+j+"\n"
		string+="\n"+pd

		return string

	##########################################################################

	def Substitute(self,src,dst):
		a=self.getAll()
		rx=re.compile(src)
		b=rx.sub(dst,a)
		del rx
		self.parseRequest(b,self.schema)

	def parseRequest (self,rawRequest,prot="http"):
		''' Aun esta en fase BETA y por probar'''
		tp=TextParser()
		tp.setSource("string",rawRequest)

		self.__variablesPOST=VariablesSet()
		self._headers={}		# diccionario, por ejemplo headers["Cookie"]

		tp.readLine()
		try:
			tp.search("^(\w+) (.*) (HTTP\S*)$")
			self.method=tp[0][0]
			self.protocol=tp[0][2]
		except Exception,a:
			print rawRequest
			raise a

		pathTMP=tp[0][1].replace(" ","%20")
		pathTMP=('','')+urlparse(pathTMP)[2:]
		pathTMP=urlunparse(pathTMP)

		while True:
			tp.readLine()
			if (tp.search("^([^:]+): (.*)$")):
				self.addHeader(tp[0][0],tp[0][1])
			else:
				break

		self.setUrl(prot+"://"+self._headers["Host"]+pathTMP)

		if self.method.upper()=="POST":

			pd=""
			while tp.readLine(): 
				pd+=tp.lastFull_line

			boundary=None
			if "Content-Type" in self._headers:
				values=self._headers["Content-Type"].split(";")
				self.ContentType=values[0].strip().lower()
				if self.ContentType=="multipart/form-data":
					boundary=values[1].split("=")[1].strip()

			self.setPostData(pd,boundary)

		
