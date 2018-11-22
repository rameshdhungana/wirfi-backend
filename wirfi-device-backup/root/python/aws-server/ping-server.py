#!/bin/bash/env python
import urllib2,urllib,subprocess,json,os,ConfigParser
filepath = os.path.dirname(os.path.realpath(__file__)) + '/aws_server_info.cfg'
config = ConfigParser.RawConfigParser()
config.read(filepath)
url = config.get('AwsServerInfo', 'aws_server_ping_address')
print(url,'this is url')
print(filepath)

values = {'os':'openwrt', 'name':'wirifi','device_serial_number':111111}
print(values)
data = urllib.urlencode(values)
print(data)
print('before encode:', type(values),' after encode:',type(data))
res = urllib2.Request(url,data)
r = urllib2.urlopen(res)
response = r.read()
d_data = json.dumps(response)
p_data = json.loads(d_data)
print(p_data,type(p_data))
#mac = subprocess.call(['ifconfig','-a','|','grep', 'eth0'],shell=False)
#print(mac)
if 'model' in  p_data:
	if  p_data['model']=='DeviceNetwork':
		ssid = p_data['data']['ssid_name']
		password = p_data['data']['password']
		print(ssid, password,111111111111)
		subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].ssid={0}'.format(ssid)], shell=False)
		subprocess.call(['sudo','uci','set', 'wireless.@wifi-iface[0].key={0}'.format(password)], shell=False)
		subprocess.call(['sudo','uci','commit'], shell=False)
		subprocess.call(['sudo','wifi'], shell=False)
		print('ssid and password is  changed successfully')
       

