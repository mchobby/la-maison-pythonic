# Test les differents senseurs du montage Cabane - v0.2
#
# V0.1 - Initial Writing
# v0.2 - remove AM2315 (too sensitive)
#

from machine import Pin, I2C
from time import sleep

# --- Abstraction ESP32 et ESP8266 ---
def get_i2c():
	""" Abstraction du bus I2C pour ESP32 et ESP8266 """
	import os
	if os.uname().nodename == 'esp32':
		return I2C( sda=Pin(23), scl=Pin(22) )
	else:
		return I2C( sda=Pin(4), scl=Pin(5) )

# declare le bus i2c
i2c = get_i2c()

# Tester le tsl2561 - senseur lux
from tsl2561 import TSL2561
tsl = TSL2561( i2c=i2c )
print( "tsl2561: {0:.2f}lx".format( tsl.read() ) )

# tester le bmp280 - senseur pression/température
from bme280 import BME280, BMP280_I2CADDR
bmp = BME280( i2c=i2c, address=BMP280_I2CADDR )
(t,p,h) = bmp.values # capturer les valeurs sous format texte
print( "bmp280: %s" % t ) # temperature
print( "bmp280: %s" % p ) # pression

# tester le am2315 - senseur humidité/température
# (Capteur parfois très tatillon)
#
#from am2315 import AM2315
#am = AM2315( i2c=i2c )
#am.measure() # reactive le senseur
#sleep( 1 )
#am.measure()
#print( "am2315: {0:.2f}C".format( am.temperature() ) )
#print( "am2315: {0:.2f}%Rh".format( am.humidity() ) )

print( "All done!" )
