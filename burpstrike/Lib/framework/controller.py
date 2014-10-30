'''
controller.py

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

from framework.settings import Settings
from framework.facade import Facade

class Controller:
    def on_enable_plugin(self, name, state):
	if name == "All" and state:
	    Facade().issue_alert("Enabled all plugins")
	    Facade().get_plugins().enable_all()
	elif name == "All" and not state:
	    Facade().issue_alert("Disabled all plugins")
	    Facade().get_plugins().disable_all()

    def on_enable_tool(self, value):
	if value:
	    Facade().issue_alert("Enabled burpstrike")
	else:
	    Facade().issue_alert("Disabled burpstrike")

	Settings().set(Settings.SEC_PLUGIN_INTEGRATION, Settings.ACTIVE, str(value))

