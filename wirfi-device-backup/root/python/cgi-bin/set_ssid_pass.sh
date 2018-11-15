#!/bin/sh

while getopts s:p: option
do
	case "${option}"
	in
	s) SSID=${OPTARG};;
	p) PASSWORD=${OPTARG};;
	esac
done

#ssid=$1
#password=$2

uci batch << EOF
set wireless.@wifi-iface[0].ssid='$SSID'
set wireless.@wifi-iface[1].key='$PASSWORD'

commit
EOF
wifi
