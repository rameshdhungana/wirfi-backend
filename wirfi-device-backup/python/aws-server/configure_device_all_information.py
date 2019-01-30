#!/usr/bin/env python
import ConfigParser

config = ConfigParser.RawConfigParser()
#server related information section
config.add_section('AwsServerInfo')

config.set('AwsServerInfo', 'aws_server_ip_address', 'http://api.wirfi.testiw.codesamaj.com/')
config.set('AwsServerInfo', 'aws_server_ping_address', 'http://api.wirfi.testiw.codesamaj.com/server/ping/')
config.set('AwsServerInfo', 'aws_server_set_primary_network_address', 'http://api.wirfi.testiw.codesamaj.com/server/set-primary-network/')
config.set('AwsServerInfo', 'secret_key_to_access_server', 'qRY,1QC;>#^,S|6M*Ky~<m-+p{ADEfWIRFI')

#device related information section
config.add_section('DeviceInfo')
config.set('DeviceInfo', 'device_serial_number', '1111111111')

# device login credentials to login into device to change primary network settings
config.add_section('DeviceLoginCredentials')
config.set('DeviceLoginCredentials','username','WiRFiUser')
config.set('DeviceLoginCredentials','password','Asdf1234!@#$')

# Writing our configuration file to 'device_all_configurations.cfg'
with open('device_all_configurations.cfg', 'wb') as configfile:
    config.write(configfile)

