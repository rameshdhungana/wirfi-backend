#!/usr/bin/env python
# Import modules for CGI handleing
import cgi, cgitb
import subprocess
import logging
import ConfigParser

logger = logging.getLogger('applySettingsScript')
hdlr = logging.FileHandler('/tmp/applySettings.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
username = form.getvalue('username')
logger.info(username)
password = form.getvalue('password')
logger.info(password)

config = ConfigParser.RawConfigParser()
config.read('/root/python/cgi-bin/device_login_credentials.cfg')
uname = config.get('deviceLoginCredentials', 'username')
pword = config.get('deviceLoginCredentials', 'password')
print uname,pword

if username == uname and password == pword:
	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>Settings</title>"
	print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
	#print "<link rel='stylesheet' href='/cgi-bin/style_index.css'>"
	print "</head>"
	print "<body style='background-color:#1e212a;'>"
	print"<div class='container' style='min-height:100vh;'>"
	print "<div class='row' style='margin-top:10rem;'>"
	print "<div class='col-sm-12 text-center' style='color:white; padding-bottom:6rem;'>"
	#print "<img src='/cgi-bin/wirfi-logo.png'>"
	print "<h4>Lets get your WiRFi online and running.</h4>"
	print "<h4>Please enter the network name and password of the.</h4>"
	print "<h4>router you would  like to connect to?</h4>"
	print "</div>"
	print "<div class='col-sm-12 text-center'>"
	print "<form action = \"/cgi-bin/apply_settings.py\" method = \"post\">"
	print "<div  class='form-group'>"
	print "<input type = \"text\" name = \"ssid\"  class='form-control form-control-lg' placeholder='Network Name (SSID Name)'  style='background-color:#3c3e4d;height:60px;border:1px solid #3c3e4d;color:#fff'><br/>"
	print "</div>"
	print "<div  class='form-group'>"
	print "<input type = \"text\" name = \"password\" class='form-control form-control-lg' placeholder='Network Password (SSID Password)' style='background-color:#3c3e4d;height:60px;border:1px solid #3c3e4d;color:#fff'/>"
	print "</div>"
	print "<input type = \"submit\" class='btn btn-light btn-block btn-lg' value = \"Apply Settings\" style='margin-top:4rem;background-color:white;'/>"
	print "<h4 style='color:white'> %s, %s,%s,%s,%s,%s</h4>" %(username,password, uname,pword,username==uname, password==pword)
	print "</form>"
	print "</div>"
	print "</div>"
	print "</div>"
	print "</body>"
	print "</html>"

else:
	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>Settings</title>"
	print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
	print "</head>"
	print "<body style='background-color:#1e212a;'>"
	print"<div class='container' style='min-height:100vh;'>"
	print "<div class='row' style='margin-top:10rem;'>"
	print "<div class='col-sm-12 text-center' style='color:white; padding-bottom:6rem;'>"
	print "<h4>Please enter Username and Password</h4>"
	print "<h4> to login into WiRFi device.</h4>"
	print "<h4 style='color:red;padding-top:2rem;'>Invalid Username Or password.Please re-enter</h4>"
	print "</div>"
	print "<div class='col-sm-12 text-center'>"
	print "<form action = \"/cgi-bin/device_login_check.py\" method = \"post\">"
	print "<div  class='form-group'>"
	print "<input type = \"text\" name = \"username\"  class='form-control form-control-lg' placeholder='Username'  style='background-color:#3c3e4d;height:60px;border:1px solid #3c3e4d;color:#fff'><br/>"
	print "</div>"
	print "<div  class='form-group'>"
	print "<input type = \"text\" name = \"password\" class='form-control form-control-lg' placeholder='Password' style='background-color:#3c3e4d;height:60px;border:1px solid #3c3e4d;color:#fff'/>"
	print "</div>"
	print "<input type = \"submit\" class='btn btn-light btn-block btn-lg' value = \"Login\" style='margin-top:4rem;background-color:white;'/>"
	print "<h4 style='color:white'> %s, %s,%s,%s,%s,%s</h4>" %(username,password, uname,pword,username==uname, password==pword)
	
	print "</div>"
	print "</form>"
	print "</div>"
	print "</div>"
	print "</body>"
	print "</html>"
	
