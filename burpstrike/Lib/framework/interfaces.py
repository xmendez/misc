'''
interfaces.py

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
class IPlugin:
    def name(self):
        raise NotImplemented

    def issue(self):
        raise NotImplemented

    def description(self):
        raise NotImplemented

    def parameters(self):
        raise NotImplemented

    def _process(self, msg):
        raise NotImplemented

    def ptype(self, msg):
        raise NotImplemented

