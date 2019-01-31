#!/usr/bin/env python

# Import modules for CGI handleing
import cgi, cgitb
import subprocess
import urllib, urllib2
import os
import ConfigParser
import json
import ast

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
ssid = form.getvalue('ssid')
password = form.getvalue('password')
if ssid and password:
	
	# Get url from ~/python/aws-server/device_all_configurations.cfg
	#filepath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/aws-server/device_all_configurations.cfg' 
	#print(filepath)
	#config = ConfigParser.RawConfigParser()
	#config.read(filepath)
	#url = config.get('AwsServerInfo', 'aws_server_set_primary_network_address')
	#print url
	
	# get device_serial_number as well
	#device_serial_number = config.get('DeviceInfo', 'device_serial_number') 
	
	# get device_secret_key_to_access_server to authenticate device in server
	#secret_key_to_access_server = config.get('AwsServerInfo', 'secret_key_to_access_server')
	
	#provide the ssid name, password and device serial number and ping server to store it to database
	#values = {'primary_ssid_name':ssid,'primary_password':password,'device_serial_number':device_serial_number,'secret_key_to_access_server':secret_key_to_access_server}
	#print(values)
	#data = urllib.urlencode(values)
	#res = urllib2.Request(url,data)
	#r = urllib2.urlopen(res)
	#response = r.read()
	#p_data = ast.literal_eval(response)
	#print p_data,'/n','---------'	
	
	#if p_data['device_serial_number'] == device_serial_number and p_data['code'] == 1:
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
	print "<div class='container' style='min-height:100vh;'>"
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
	
	#else:
		#print "Content-type:text/html\r\n\r\n"
                #print "<html>"
                #print "<head>"
                #print "<title>WiRFi Settings</title>"
                #print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
                #print "<link rel='stylesheet' href='/cgi-bin/style_index.css'>"
                #print "</head>"
                #print "<body style='background-color:#1e212a;'>"
                #print "<div class='container' style='min-height:100vh;'>"
                #print "<div class='row' style='margin-top:10rem;'>"
                #print "<div class='col-sm-12 text-center' style='color:white; padding-bottom:6rem;'>"
                #print "<img src='/cgi-bin/wirfi-logo.png'>"
                #print "<h4 style='padding-bottom:2rem;'>There is problem setting up the device.</h4>"
                #print "<h4 style='padding-bottom:2rem;'>It seems like you have not added device. </h4>"
                #print "<h4 style='padding-bottom:2rem;'>Or the you have entered the device serial number incorrectly while adding device.</h4>"
                #print "<h4 style='padding-bottom:2rem;'>Please Go back to your Mobile app or Web Portal and fix the issue. </h4>"
                #print "</div>"
                #print "</div>"
                #print "</div>"
                #print "</body>"
                #print "</html>"

else:
	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>Settings</title>"	
	print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
	print "</head>"
	print "<body style='background-color:#1e212a;'>"
	print "<div class='container' style='min-height:100vh;'>"
	print "<div class='row' style='margin-top:10rem;'>"
	print "<div class='col-sm-12 text-center' style='color:white; padding-bottom:6rem;'>"
	print "<h4>Please enter Username and Password</h4>"
	print "<h4> to login into WiRFi device.</h4>"
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
	print "</div>"
	print "</form>"
	print "</div>"
	print "</div>"
	print "</body>"
	print "</html>"


