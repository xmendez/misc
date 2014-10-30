'''
console.py

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

from cmd import Cmd
from code import InteractiveConsole

from framework.settings import Settings
from framework.facade import Facade

class CLI(InteractiveConsole):
    def __init__(self, loc=None, filename="<console>", histfile=None):
        InteractiveConsole.__init__(self, loc, filename)
        try:
            import readline
	    import rlcompleter
	    readline.set_completer(rlcompleter.Completer(loc).complete)
            readline.parse_and_bind("tab: complete")
        except ImportError:
	    print "error importando readline"
            pass

        self.interact()


class Console(Cmd):
    """Simple command processor example."""
    def do_about(self, line):
        """about
        Show about dialog"""

	print 'BurpStrike @Javi'
    
    def do_EOF(self, line):
        return True

#    def do_cli2(self, line):
#	#try:
#	import framework.api
#	loc = framework.api.__dict__
#	#CLI(dict([(k,loc[k]) for k in loc.keys() if k.startswith("api_")]))
#	CLI(globals())
#        #except ImportError:
#	#    print "error importando api"
#        #    pass
#
#    def do_cli(self, line):
#	#try:
#	import framework.api
#	loc = framework.api.__dict__
#	CLI(dict([(k,loc[k]) for k in loc.keys() if k.startswith("api_")]))
#        #except ImportError:
#	#    print "error importando api"
#        #    pass

    def do_flushcache(self, line):
	Facade().get_jobman().flush_cache()

    def do_reload(self, line):
	Facade().load_plugins()

    def do_plugins(self, line):
	for i in Facade().get_plugins().names():
	    print i

    def do_disable(self, line):
	Facade().get_controller().on_enable_tool(False)

    def do_enable(self, line):
	Facade().get_controller().on_enable_tool(True)

    def do_activate_plugins(self, line):
	Facade().get_controller().on_enable_plugin("All", True)

    def do_deativate_plugins(self, line):
	Facade().get_controller().on_enable_plugin("All", False)

    def do_issues(self, line):
	for i in range(len(Facade().get_results())):
	    print str(Facade().get_results().get_result(i))


