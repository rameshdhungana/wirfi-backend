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
print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
#print "<link rel='stylesheet' href='/cgi-bin/style_index.css'>"
print "</head>"
print "<body style='background-color:#1e212a;'>"
print"<div class='container' style='min-height:100vh;'>"
print "<div class='row' style='margin-top:10rem;'>"
print "<div class='col-sm-12 text-center' style='color:white; padding-bottom:6rem;'>"
#print "<img src='/cgi-bin/wirfi-logo.png'>"
print "<h4 style='padding-bottom:2rem;'>WiRFi device Network (SSID) name and Password are successfully changed.</h4>"
print "<h4 style='padding-bottom:2rem;'>Network (SSID) Name:  %s </h4>" %(ssid)
print "<h4 style='padding-bottom:2rem;'>Network Password is:  %s</h4>"%(password)
print "<h4 style='padding-bottom:2rem;'>Please Go back to your app now.</h4>"
print "</div>"
print "</div>"
print "</div>"
print "</body>"
print "</html>"

