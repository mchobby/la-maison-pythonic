#!/bin/bash
# Collecter les pilotes nécessaires 
rm tsl2561.py
rm bme280.py
rm am2315.py
wget https://raw.githubusercontent.com/mchobby/esp8266-upy/master/tsl2561/tsl2561.py
wget https://raw.githubusercontent.com/mchobby/esp8266-upy/master/bme280-bmp280/bme280.py
wget https://raw.githubusercontent.com/mchobby/esp8266-upy/master/am2315/am2315.py


