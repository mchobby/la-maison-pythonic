#!/bin/bash
# Subscribe ALL the messages with "#"
#  -h mosquitto server to contact
#  -t topic to subscribe (use # for everything)
#  -v verbose (mode bavard)
#  -u mosquitto user login (when defined on Mosquitto server)
#  -P mosquitto user password (when defined on Mosquitto server)
#
#   Piping with ts utility will display date and time in the output
#   (ts may requires "sudo apt install moreutils" to get installed) 
#
mosquitto_sub -h 192.168.1.210 -t "#" -v -u pusr103 -P 21052017 | ts

# Subscribe ALL message on unprotected mosquitto server
#
# mosquitto_sub -h 192.168.1.210 -t "#" -v
