#!/usr/bin/env python
import ConfigParser

config = ConfigParser.RawConfigParser()
config.add_section('AwsServerInfo')

config.set('AwsServerInfo', 'aws_server_ip_address', '192.168.1.181:8000')
config.set('AwsServerInfo', 'aws_server_ping_address', 'http://192.168.1.181:8000/ping-server/')

# Writing our configuration file to 'device_login_credentials.cfg'
with open('aws_server_info.cfg', 'wb') as configfile:
    config.write(configfile)


