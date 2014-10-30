#!/usr/bin/python
'''
certlookup.py

Copyright 2011 Xavier Mendez (xmendez@edge-security.com)
reportIP function shamesly copied from: http://phreakmonkey.com/index.php/archives/100

certlookup is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

certlookup is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
import sys
import socket
import getopt

from xml.dom import minidom


try:
    from M2Crypto import SSL
except ImportError:
    sys.stderr.write('You need M2Crypto module')
    sys.stderr.flush()
    sys.exit(2)

class MyException(Exception):
    pass

class CertLookup:
    def __init__(self, ip_list, verbose = False):
	self.ip_list = ip_list
	self.len_list = len(ip_list)
	self.current = 0
	self.verbose = verbose

    def __iter__(self):
	return self

    def next(self):
	if self.current >= self.len_list:
	    raise StopIteration
	else:
	    host, port = self.ip_list[self.current]
	    ip = self.verify_ip(host)
	    self.current += 1

	    ns = None

	    try:
		ns = self.resolve_cert(self.reportIP(ip, int(port)), ip)
	    except MyException,e:
		sys.stderr.write('Error: %s\n' % e)
		sys.stderr.flush()
	    else:
		return (ns, ip)

    def reportIP(self, IPaddress, port):
	"""
	Shamesly copied from: http://phreakmonkey.com/index.php/archives/100

	A quick hack to probe for SSL Certificate Information
	Requres python & m2crypto  

	2007.09.26 - phreakmonkey.com / phreakmonkey at gmail 
	"""
	ctx = SSL.Context()
	ctx.set_allow_unknown_ca(True)
	ctx.set_verify(SSL.verify_none, 1)
	conn = SSL.Connection(ctx)
	conn.postConnectionCheck = None
	timeout = SSL.timeout(15)
	conn.set_socket_read_timeout(timeout)
	conn.set_socket_write_timeout(timeout)

	try:
	    if self.verbose:
		sys.stderr.write('Connecting '+IPaddress+'.\n')
		sys.stderr.flush()
	    conn.connect((IPaddress, port))
	except KeyboardInterrupt:
	    raise KeyboardInterrupt
	except TypeError:
	    raise MyException('connect: Malformed address specified')
	except socket.gaierror:
	    raise MyException('connect: No address associated with hostname')
	except socket.error:
	    raise MyException('timeout connecting with hostname.')
	except SSL.SSLError:
	    raise MyException('SSL_HANDSHAKE_FAILED.')

	if self.verbose:
	    sys.stderr.write('Retrieving cert info.\n')
	    sys.stderr.flush()

	cert = conn.get_peer_cert()
	try:
	    cissuer = cert.get_issuer().as_text()
	except SSL.SSLError:
	    raise MyException('Error:  No Valid Cert Presented.')

	conn.close

	return cert

    def resolve_cert(self, cert, ip):
	cCN = ""

	try:
	    cCN = cert.get_subject().CN
	    if self.verbose:
		sys.stderr.write('Obtained cert\'s CN attribute: %s\n' % cCN)
		sys.stderr.flush()
	except AttributeError:
	    raise MyException('Error: Cert without CN attribute.')

	try:
	    resolving = socket.gethostbyname(cCN)
	    if self.verbose:
		sys.stderr.write('Looking up CN name, result: %s\n' % resolving)
		sys.stderr.flush()

	    if resolving == ip:
		return cCN.lower()
	    else:
		if self.verbose:
		    sys.stderr.write('Error: Cert not issued for this IP\n')
		    sys.stderr.flush()

		return None
	except socket.gaierror:
	    raise MyException('DNS Error: No address associated with hostname %s.' % cCN)

	return None

    def verify_ip(self, ip):
	try:
	    socket.inet_aton(ip)
	except socket.error:
	    raise MyException("You must supply a valid IP address")

	return ip

    @staticmethod
    def to_magictree(hostlist):
	def create_xml_element(parent, caption, text):
	    # Create a <xxx> element
	    doc = minidom.Document()
	    el = doc.createElement(caption)
	    parent.appendChild(el)

	    # Give the <xxx> element some text
	    ptext = doc.createTextNode(text)

	    el.appendChild(ptext)
	    return el
	doc = minidom.Document()

	#<magictree class="MtBranchObject">
	node_mt = doc.createElement("magictree") 
	node_mt.setAttribute("class", "MtBranchObject")

	#<testdata class="MtBranchObject">
	node_td = doc.createElement("testdata") 
	node_td.setAttribute("class", "MtBranchObject")
	node_mt.appendChild(node_td)

	#<host>209.85.146.105
	for cn, ip in hostlist:
	    node_h = create_xml_element(node_td, "host", str(ip))
	    create_xml_element(node_h, "hostname", str(cn))

	return node_mt

    @staticmethod
    def about():
	print """
	    certlookup - is a tool for performing reverse IP lookups interrogating SSL servers for certificate's CN attribute.

		Although is normally used with command-line arguments, it also has a magic tree mode of operation for reading lookup
		requests from a file and outputing in XML. 

		Coded by Xavier Mendez aka Javi (xavi.mendez@gmail.com)
	"""


def main():
    def usage():
	print """
Usage: certlookup.py [--help] [--verbose] -h <ip> [-i=$in] [-p <port>] [--mtree=$out]

Examples:

    $ python certlookup.py -h 69.58.181.89 
    www.verisign.com (69.58.181.89)

    $ echo -e "69.58.181.89\\t443" > /tmp/a
    $ python certlookup.py -i /tmp/a
    www.verisign.com (69.58.181.89)

MagicTree integration:
    certlookup.py -i=$i --mtree=$out

    The input file must be a list of: ip<TAB>port 
	"""
	sys.exit(0)

    # command line options variables
    verbose = False
    host = ""
    port = 443
    mtree_file_name = None
    input_file_name = None

    # get command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vh:p:i:", ["help","verbose","mtree="])
    except getopt.GetoptError, err:
	usage()

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-i",):
	    input_file_name = a
        elif o in ("--mtree",):
	    mtree_file_name = a
        elif o in ("--help",):
            CertLookup.about()
            sys.exit(0)
        elif o in ("-h",):
            host = a
        elif o in ("-p",):
            port = int(a)
        else:
            assert False, "unhandled option"

    if len(sys.argv) < 2 or (host=="" and input_file_name is None):
	usage()

    # file or -h input
    l = []
    try:
	if input_file_name is not None:
	    ips = [i.split('\t') for i in open(input_file_name, 'r')]
	else:
	    ips = [[host, port]]

	for ns, ip in CertLookup(ips, verbose):
	    print "%s (%s)" % (ns, ip)
	    l.append((ns, ip))
    except IOError:
	sys.stderr.write('Error: reading input list\n')
	sys.stderr.flush()
	sys.exit(2)
    except KeyboardInterrupt:
	sys.exit(2)
    except ValueError:
	sys.stderr.write('Error: Incorrect input list format. It should be: ip<tab>port\n')
	sys.stderr.flush()
    except MyException,e:
	sys.stderr.write('Error: %s\n' % e)
	sys.stderr.flush()
    except Exception,e:
	sys.stderr.write('Unhandled exception!')
	sys.stderr.flush()
	sys.exit(2)

    # magictree output
    if mtree_file_name is not None:
	f = None
	try:
	    f = open(mtree_file_name, 'w')
	    CertLookup.to_magictree(l).writexml(f)
	except IOError:
	    sys.stderr.write('Error: writing magictree XML file.\n')
	    sys.stderr.flush()
	    sys.exit(2)
	finally:
	    if f: f.close()

if __name__ == "__main__":
    main()

