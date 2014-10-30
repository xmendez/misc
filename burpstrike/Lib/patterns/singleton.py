'''
Singleton.py

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

import sys
import traceback

class Singleton(type):
    ''' Singleton metaclass. Use by defining the metaclass of a class Singleton,
        e.g.: class ThereCanBeOnlyOne:
                  __metaclass__ = Singleton 
    '''              

    def __call__(class_, *args, **kwargs):
	try:
	    if not class_.hasInstance():
		class_.instance = super(Singleton, class_).__call__(*args, **kwargs)
	    return class_.instance
	except Exception, e:
	    error_type, error_value, trbk = sys.exc_info()
	    tb_list = traceback.format_tb(trbk, 6)    
	    s = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__, error_value)
	    for i in tb_list:
		s += "\n" + i

	    print s
	    return None

    def deleteInstance(class_):
        ''' Delete the (only) instance. This method is mainly for unittests so
            they can start with a clean slate. '''
        if class_.hasInstance():
            del class_.instance

    def hasInstance(class_):
        ''' Has the (only) instance been created already? '''
        return hasattr(class_, 'instance')
