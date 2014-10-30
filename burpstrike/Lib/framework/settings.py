'''
settings.py

Copyright 2009 Xavier Mendez Navarro aka Javi

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

import ConfigParser
import os, sys

#My modules
from patterns.singleton import Singleton

class SettingsBase:
    """
    Contains application settings. uses a ConfigParser
    """
    __metaclass__ = Singleton

    def __init__(self, save = False):
	self.cparser = ConfigParser.SafeConfigParser()

	self.set_defaults()
        self.filename = os.path.join(self.path_to_program_dir(), self.get_config_file())
	
	self.cparser.read(self.filename)

	#if save:
	#    self.save()

    def set(self, section, setting, value):
        if type(value) == type(u''):
            value = value.encode('utf-8')
        self.cparser.set(section, setting, value)

    def get(self, section, setting):
        value = self.cparser.get(section, setting)
        return value.decode('utf-8')

    def get_config_file(self):
	raise Exception, 'SettingsBase. Base class must declare get_config_file method'

    def set_defaults(self):
	raise Exception, 'SettingsBase. Base class must declare set_defaults method'

    def get_options(self, section):
    	return self.cparser.options(section)

    def get_sections(self):
    	return self.cparser.sections()

    def get_all(self):
	sett = {}

	# dump entire config file
	for section in self.cparser.sections():
	    for option in self.cparser.options(section):
		if not sett.has_key(section):
		    sett[section] = []
		sett[section].append( (option, self.cparser.get(section, option) ) )
										  
	return sett

    def save(self):
        try:
            iniFile = file(self.filename, 'w')
            self.cparser.write(iniFile)
            iniFile.close()
        except Exception, message:
	    return False
	return True

    def set_all(self, sett):
	self.cparser = ConfigParser.SafeConfigParser()
        for section, settings in sett.items():
            self.cparser.add_section(section)
            for key, value in settings:
		self.cparser.set(section, key, value)

    def path_to_program_dir(self):
	"""
	Returns path to program directory
	"""
	path = sys.argv[0]

	if not os.path.isdir(path):
	    path = os.path.dirname(path)

	if not path: return '.'

	return path

class Settings(SettingsBase):
    """
    Contains application main settings. uses SettingsBase
    """
    SEC_GRL = 'general'
    LOGFILE = 'logfile'
    DEBUG_LEVEL = 'debug_level'
    AUTO_SESSION = 'auto_save_session'
    AUTO_SSETT = 'auto_save_settings'
    AUTO_SAVE_FILE = 'auto_save_file'

    SEC_HTTP = 'http'
    CONN_TIMEOUT = 'conn_timeout'
    TOTAL_TIMEOUT = 'total_timeout'
    CONN_RETRIES = 'conn_retries'
    PROXY = 'proxy'
    INVALID_CODES = 'invalid_codes'

    SEC_PLUGIN_INTEGRATION = 'plugins'
    ACTIVE = 'active'
    ONLY_SCOPE = 'only_scope'
    PROCESS_TOOLS = 'process_burp_tools'
    EXCLUDED_REQ_TOOLS = 'excluded_request_burp_tools'
    EXCLUDED_RESP_TOOLS = 'excluded_response_burp_tools'
    W3AF_DIR = 'w3af_path'
    
    SEC_PERF = 'performance'
    MAX_THREADS = 'max_threads'
    
    DEBUG_LEVEL_DEBUG, DEBUG_LEVEL_INFO, DEBUG_LEVEL_WARNING, DEBUG_LEVEL_ERROR, DEBUG_LEVEL_CRITICAL = 'debug', 'info', 'warning', 'error', 'critical'
    AUTO_TRUE, AUTO_FALSE = 'True', 'False'

    def __init__(self):
    	SettingsBase.__init__(self, True)

    def get_config_file(self):
	return 'config.ini'

    def set_defaults(self):
	self.set_all(
	    { \
		Settings.SEC_HTTP: [ \
		    (Settings.CONN_TIMEOUT, '5'),
		    (Settings.TOTAL_TIMEOUT, '20'),
		    (Settings.CONN_RETRIES, '5'),
		    (Settings.PROXY, ''),
		    (Settings.INVALID_CODES, '401,403,404'),
		],
		Settings.SEC_PLUGIN_INTEGRATION: [ \
		    (Settings.ACTIVE, 'True'),
		    (Settings.PROCESS_TOOLS, 'True'),
		    (Settings.EXCLUDED_REQ_TOOLS, 'scanner,intruder,repeater'),
		    (Settings.EXCLUDED_RESP_TOOLS, ''),
		    (Settings.ONLY_SCOPE, 'True'),
		    (Settings.W3AF_DIR, '/home/javi/w3af-read-only/'),
		],
		Settings.SEC_PERF: [ \
		    (Settings.MAX_THREADS, '20'),
		],
		Settings.SEC_GRL: [ \
		    (Settings.LOGFILE, os.path.join(self.path_to_program_dir(),'burpstrike.log')),
		    (Settings.DEBUG_LEVEL, 'info'),
		    (Settings.AUTO_SAVE_FILE, os.path.join(self.path_to_program_dir(),'data.pkl')),
		    (Settings.AUTO_SESSION, 'True'),
		    (Settings.AUTO_SSETT, 'True'),
		],
	    }
	)
