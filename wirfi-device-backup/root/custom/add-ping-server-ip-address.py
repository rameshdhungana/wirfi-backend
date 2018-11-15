#!/usr/bin/env python
import subprocess, argparse

parser = argparse.ArgumentParser()
parser.add_argument('address')

args = parser.parse_args()
address= args.address

print(address)
print('for backup')
file = open('ping-server-ip-address.txt','w')
file.write('PING_SERVER_IP_ADDRESS={0}'.format(address))
file.close()
r_file = open('ping-server-ip-address.txt', 'r')
lines  = r_file.readlines()

print(lines[0])
r_file.close()

