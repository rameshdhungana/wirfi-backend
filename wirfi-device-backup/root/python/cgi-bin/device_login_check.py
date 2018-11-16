#!/usr/bin/python

# Import modules for CGI handleing
import cgi, cgitb
import subprocess
import logging
import ConfigParser

logger = logging.getLogger('loginCredentialCheckScript')
hdlr = logging.FileHandler('/tmp/loginCredentialCheck.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
username = form.getvalue('ssid')
logger.info(username)
password = form.getvalue('password')
logger.info(password)

config = ConfigParser.RawConfigParser()
config.read('device_login_credentials.cfg')
uname = config.get('deviceLoginCredentials', 'username')
pword = config.get('deviceLoginCredentials', 'password')
if username ==uname and password == pword:
	 
	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>WiRFi Settings</title>"
	print "</head>"
	print "<body>"
	print "<h2>Login credentials: %s/%s</h2>" % (username, password)
	print "<br>"
	print "</body>"
	print "</html>"

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>WiRFi Settings</title>"
print "</head>"
print "<body>"
print "<h2>Login credentials: %s/%s</h2>" % (username, password)
print "<br>"
print "</body>"
print "</html>"


