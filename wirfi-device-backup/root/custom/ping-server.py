#!/bin/bash/env python
import urllib2,urllib,subprocess,json
url = 'http://192.168.1.161:8000/ping-server/'
try:
	file = open('ping-server-ip-address.txt','r')
	lines = file.readlines()
	print(lines[0])
	url = (lines[0].split('='))[1]
	print url
	
except:
	file = open('ping-server-ip-address.txt','w')
	file.write('PING_SERVER_IP_ADDRESSS={0}'.format(url))
file.close()

	
values = {'os':'openwrt', 'name':'wirifi','device_serial_number':111111}
print(values)
data = urllib.urlencode(values)
print(data)
print('before encode:', type(values),' after encode:',type(data))
res = urllib2.Request(url,data)
r = urllib2.urlopen(res)
response = r.read()
d_data = json.dumps(response)
p_data = json.loads(response)
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
       

