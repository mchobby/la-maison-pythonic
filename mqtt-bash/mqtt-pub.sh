#!/bin/bash
# Send a test message to Mosquitto server
#  -h mosquitto server to contact
#  -t topic to subscribe (use # for everything)
#  -v verbose (mode bavard)
#  -u mosquitto user login (when defined on Mosquitto server)
#  -P mosquitto user password (when defined on Mosquitto server)
#
mosquitto_pub -h 192.168.1.210 -t "cmd/led" -m "on" -u pusr103 -P 21052017
sleep 2
mosquitto_pub -h 192.168.1.210 -t "cmd/led" -m "off" -u pusr103 -P 21052017

# Subscribe ALL message on unprotected mosquitto server
#
# mosquitto_pub -h 192.168.1.210 -t "cmd/led" -m "on"
# sleep 2
# mosquitto_pub -h 192.168.1.210 -t "cmd/led" -m "off"
