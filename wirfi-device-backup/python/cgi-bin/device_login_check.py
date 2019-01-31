#!/usr/bin/env python

import cgi
import ConfigParser
import os
import render_html

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
username = form.getvalue('username')
password = form.getvalue('password')

filepath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/aws-server/device_all_configurations.cfg'

config = ConfigParser.RawConfigParser()
config.read(filepath)
uname = config.get('DeviceLoginCredentials', 'username')
pword = config.get('DeviceLoginCredentials', 'password')

if username == uname and password == pword:
    render_html.render_html('network_settings.html')

else:
    render_html.render_html('login_page.html')
