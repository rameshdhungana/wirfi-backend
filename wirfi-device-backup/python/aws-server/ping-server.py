#!/bin/bash/env python
import urllib2,urllib,subprocess,json,os,ConfigParser,ast
filepath = os.path.dirname(os.path.realpath(__file__)) + '/device_all_configurations.cfg'
config = ConfigParser.RawConfigParser()
config.read(filepath)
url = config.get('AwsServerInfo', 'aws_server_ping_address')
print(url,'this is url')
print(filepath)

#get device secret key to access the server and pass it as data
secret_key_to_access_server = config.get('AwsServerInfo', 'secret_key_to_access_server')

#get device serial number
device_serial_number = config.get('DeviceInfo', 'device_serial_number')

#Assigning tasks to their identifier string
PRIMARY_NETWORK_CHANGED = 'primary_network_changed'
DEVICE_REBOOT = 'device_reboot'
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

def device_reboot(data):
	subprocess.call(['sudo','reboot'])
	return True

tasks_map = {
	PRIMARY_NETWORK_CHANGED:primary_network_is_changed,
	DEVICE_REBOOT:device_reboot
}

#gets the wifi network signal average signal strength
cmd = "iw dev wlan0 station dump | grep 'signal avg' | head -1"
ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = ps.communicate()[0] 
f= open('average_signal_strength.txt','w')
f.write(output)
f.close()
r = open('average_signal_strength.txt')
signal_avg = r.readline()
network_strength = signal_avg[signal_avg.find("[")+1:signal_avg.find("]")]
r.close()

values = {'device_serial_number':device_serial_number,'network_strength':network_strength,'secret_key_to_access_server':secret_key_to_access_server}
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
 

