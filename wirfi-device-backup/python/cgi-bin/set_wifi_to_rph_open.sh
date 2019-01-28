#! /bin/ash

uci set wireless.@wifi-iface[0].ssid='RPH Open'
uci set wireless.@wifi-iface[0].key='rphengine'
uci commit
wifi
