# Test les differents senseurs du montage Cabane

from machine import Pin, I2C
from time import sleep

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )

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
from am2315 import AM2315
am = AM2315( i2c=i2c )
am.measure() # reactive le senseur
sleep( 1 )
am.measure()
print( "am2315: {0:.2f}C".format( am.temperature() ) )
print( "am2315: {0:.2f}%Rh".format( am.humidity() ) )

print( "All done!" )