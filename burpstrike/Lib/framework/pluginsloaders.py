'''
pluginsloaders.py

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

from modulemanager.interfaces import IModuleLoader
from modulemanager.interfaces import IModuleRegistrant
from framework.proxies import MyPlugin

class BRegister():
    def __init__(self, plugins):
	self.plugins = plugins


w3afPath="/home/javi/herramientas/w3af-read-only/"
sys.path.append(w3afPath)

# w3af srelated
import core.data.kb.knowledgeBase as kb
from core.data.parsers.urlParser import getPathQs
from core.data.url.httpResponse import httpResponse
from core.controllers.misc.factory import factory
from core.controllers.w3afException import w3afException

class W3AFLoader(IModuleLoader):
    def __init__(self, create_inst = True, api = None):
	self.__logger = logging.getLogger("framework.W3AFLoader")

	IModuleLoader.__init__(self, create_inst, api)

    def load_egg_from_file(self, fullName):
	pass

    def load_py_from_file(self, filename):
	try:
	    print "Loading %s... " % filename
	    #return factory('plugins.' + pluginName)
	    #print "%s%s" % (' '*(30-len(pluginName)),  "Success")              
	except w3afException, e:
	    print str(e)  # This needs to be uncommented to see what is the exception
	    #print "%s%s" % (' '*(30-len(pluginName)),  "Failed")
	    pass

#class W3AFRegister(IModuleRegistrant, BRegister):
#    def __init__(self, plugins):
#plugins = ['grep.domXss',  'grep.error500', 'grep.errorPages', 'grep.feeds',  
#           'grep.fileUpload','grep.hashFind', 'grep.httpAuthDetect',
#           'grep.privateIP', 'grep.ssn', 'grep.strangeHeaders',
#           'grep.strangeHTTPCode', 'grep.strangeReason', 'grep.svnUsers',
#           'grep.wsdlGreper']
#	BRegister.__init__(plugins)
#
#    def register(self, id, module):
#	self.__logger.debug('register. START, id=%s' % (id))
#
#	#self.plugins[module.name()] = module
#	self.plugins[id] = Plugin(module, id)
#
#    def end_loading(self, list):
#	pass
#
#    def processGrepPlugin(self,plugin,response):
#        pluginName=plugin.__class__.__name__
#        try:
#            # I am assuming that grep plugins don't look at requests, it is not the case
#            # for one of them so it will be caught as an exception
#            plugin.grep(None,response)
#        except:
#            print "ignoring issue with plugin: grep." + pluginName
#        # Retrieve report
#        kbData=kb.kb.getData(pluginName)
#        if kbData and kbData.has_key(pluginName):
#            for vuln in kbData[pluginName]: 
#                if (vuln.getURL()==response.getURL()):
#                    desc = "%s: %s" % (pluginName, vuln.getDesc())
#                    print "Issue found with w3af plugin " + desc
#    def grep(self, request, response):
#        '''
#        Plugin entry point.
#        
#        @parameter request: The HTTP request object.
#        @parameter response: The HTTP response object
#        @return: None, all results are saved in the kb.
#        '''
#        if response.is_text_or_html() and response.getURL() not in self._already_inspected:
#            
#            # Don't repeat URLs
#            self._already_inspected.append( response.getURL() )
#            
#            res = self._script_re.search( response.getBody() )
#            if res:
#                i = info.info()
#                i.setName('Ajax code')
#                i.setURL( response.getURL() )
#                i.setDesc( 'The URL: "' + i.getURL() + '" has a ajax code.'  )
#                i.setId( response.id )
#                i.addToHighlight( res.group(0) )
#                kb.kb.append( self, 'ajax', i )
#                    self.mCallBacks.issueAlert("w3af " + desc)
    
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
	self.plugins.plugins[id] = MyPlugin(module, id)

    def end_loading(self, list):
	pass

