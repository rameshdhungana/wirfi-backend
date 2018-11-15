#!/usr/bin/env python

# Import modules for CGI handleing
import cgi, cgitb
import subprocess
import logging

logger = logging.getLogger('applySettingsScript')
hdlr = logging.FileHandler('/tmp/applySettings.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
ssid = form.getvalue('ssid')
logger.info(ssid)
password = form.getvalue('password')
logger.info(password)

subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].ssid={0}'.format(ssid)], shell=False)
subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].key={0}'.format(password)], shell=False)
subprocess.call(['sudo','uci','commit'], shell=False)
subprocess.call(['sudo','wifi'], shell=False)

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>WiRFi Settings</title>"
print "</head>"
print "<body>"
print "<h2>Login credentials: %s/%s</h2>" % (ssid, password)
print "<br>"
print "</body>"
print "</html>"
