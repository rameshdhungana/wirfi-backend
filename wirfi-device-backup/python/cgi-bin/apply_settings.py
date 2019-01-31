#!/usr/bin/env python
import cgi
import subprocess
import render_html

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
ssid = form.getvalue('ssid')
password = form.getvalue('password')

if ssid and password:
    subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].ssid={0}'.format(ssid)], shell=False)
    subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].key={0}'.format(password)], shell=False)
    subprocess.call(['sudo','uci','commit'], shell=False)
    subprocess.call(['sudo','wifi'], shell=False)

    render_html.render_html('device_page.html')

else:
	render_html.render_html('network_settings.html')


