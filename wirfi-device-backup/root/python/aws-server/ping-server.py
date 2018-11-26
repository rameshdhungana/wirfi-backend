#!/bin/bash/env python
import urllib2,urllib,subprocess,json,os,ConfigParser,ast
filepath = os.path.dirname(os.path.realpath(__file__)) + '/aws_server_info.cfg'
config = ConfigParser.RawConfigParser()
config.read(filepath)
url = config.get('AwsServerInfo', 'aws_server_ping_address')
print(url,'this is url')
print(filepath)

#Assigning tasks to their identifier string
PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
SECONDARY_NETWORK_CHANGED = 'secondary_network_changed'
DEVICE_CREATED = 'device_created'

def primary_network_is_changed(data):
	print(data)
	ssid = data['ssid_name']
        password = data['password']
        print(ssid, password,111111111111)
        subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].ssid={0}'.format(ssid)], shell=False)
        subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].key={0}'.format(password)], shell=False)
        subprocess.call(['sudo','uci','commit'], shell=False)
        subprocess.call(['sudo','wifi'], shell=False)
        print('ssid and password is  changed successfully')

	return True

def secondary_network_is_changed(data):
        print(data,'this is secondary network change')
	return True


tasks_map = {
	PRIMARY_NETWORK_CHANGED:primary_network_is_changed,
	SECONDARY_NETWORK_CHANGED:secondary_network_is_changed
}

values = {'os':'openwrt', 'name':'wirifi','device_serial_number':1111111111}
print(values)
data = urllib.urlencode(values)
print(data)
print('before encode:', type(values),' after encode:',type(data))
res = urllib2.Request(url,data)
r = urllib2.urlopen(res)
response = r.read()
p_data = ast.literal_eval(response)
print p_data
#mac = subprocess.call(['ifconfig','-a','|','grep', 'eth0'],shell=False)
#print(mac)
for task in p_data:
	if task['code'] and task['device_serial_number']=='1111111111':
		tasks_map[task['action']](task['data'])
 

