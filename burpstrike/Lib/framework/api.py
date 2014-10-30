'''
api.py

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

from framework.facade import Facade
from framework.myhttp import MyHTTPMsg

from reqresp.reqresp import Request

# ------------------------------------------------
# burp interaction
# ------------------------------------------------
def api_issue_alert(msg):
    Facade().issue_alert(msg)

def api_make_http_req(url, postdata):
    r = Request()
    r.setUrl(url)
    r.setPostData(postdata)

    print "API111"
    print r.getAll()
    r.perform()

    print "API22222"
    print r.response.getContent()


def api_getProxyHistory():
    return [MyHTTPMsg.from_IHttpRequestResponse(i) for i in Facade().mCallBacks.getProxyHistory()]

def api_getSiteMap(urlprefix):
    return [MyHTTPMsg.from_IHttpRequestResponse(i) for i in Facade().mCallBacks.getSiteMap(urlprefix)]

# ------------------------------------------------
# burpstrike interaction
# ------------------------------------------------
def api_get_cache_map(plugin_name):
    pass

def api_is_url_in_cache(msg, plugin_name):
    pass

def api_process_msg(msg, plugin_name):
    plugin = Facade().get_plugins().get(plugin_name)
    plugin.process(msg, None)


def api_activate_plugin(plugin_name):
    Facade().get_plugins().set_state(plugin_name, True)

def api_deactivate_plugin(plugin_name):
    Facade().get_plugins().set_state(plugin_name, False)

