#!/usr/bin/env python
import ConfigParser

config = ConfigParser.RawConfigParser()
config.add_section('deviceLoginCredentials')
config.set('deviceLoginCredentials', 'username', 'WiRFiUser')
config.set('deviceLoginCredentials', 'password', 'Asdf1234!@#$')

# Writing our configuration file to 'device_login_credentials.cfg'
with open('device_login_credentials.cfg', 'wb') as configfile:
    config.write(configfile)
