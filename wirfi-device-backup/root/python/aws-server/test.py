#!/usr/bin/env python
import subprocess
print 'hello world'
import logging
logging.info('logger check')
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('s')
parser.add_argument('p')
args = parser.parse_args()
ssid = args.s
password = args.p
print(ssid)
print(password)


