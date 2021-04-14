#!/bin/bash
# Collecter les pilotes nécessaires
rm tsl2591.py
rm bme280.py
wget https://raw.githubusercontent.com/mchobby/esp8266-upy/master/bme280-bmp280/bme280.py
wget https://raw.githubusercontent.com/mchobby/esp8266-upy/master/tsl2591/lib/tsl2591.py
