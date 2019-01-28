import socket
import sys
import datetime
import time

#inspired by http://planzero.org/blog/2012/01/26/system_uptime_in_python,_a_better_way
def uptime():
	with open('/proc/uptime','r') as f:
		uptime_seconds = float(f.readline().split()[0])
		return str(uptime_seconds)


#create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#now connect
s.connect(('colton.cybernetics.ro',8888))

#mysql seems to expect YYYY-MM-DD HH:MM:SS.SSSSSS
#s.send(str(datetime.datetime.now().time()))
s.send("'" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "',1," + uptime())

time.sleep(2)

response = s.recv(1024)

print(response)

s.close()
