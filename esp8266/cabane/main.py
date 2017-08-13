# coding: utf8
# Envoi des données vers MQTT Broker 

from machine import Pin, I2C
from time import sleep, time

CLIENT_ID = 'cabane'

# Utiliser ceci pour tester avec le serveur de test Mosquitto 
# MQTT_SERVER = 'test.mosquitto.org'
# Utiliser ceci si le Pi est en adresse fixe (car pas de propagation du Hostname)
# MQTT_SERVER = '192.168.1.220'
# Utiliser ceci (hostname) si le Pi utilise le DHCP (car propagation du Hostname)
MQTT_SERVER = 'pythonic'

# Mettre a None si pas utile
MQTT_USER = 'pusr103'
MQTT_PSWD = '21052017'

SLEEP_TIME = 60*5 # 5 minutes = 300 secondes

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = Pin( 0, Pin.OUT )
led.value( 1 ) # eteindre
def led_error( step ):
	global led
	while True:
		for i in range( 20 ):
		    led.value(not(led.value()))
		    sleep(0.100)
		led.value( 1 ) # eteindre
		sleep( 1 )
		# clignote nbr fois
		for i in range( step ):
			led.value( 0 ) 
			sleep( 0.5 )
			led.value( 1 )
			sleep( 0.5 )
		sleep( 1 )


if runapp.value() != 1:
	from sys import exit
	exit(0)

led.value( 0 ) # allumer

# --- Programme Pincipal ---
from umqtt.simple import MQTTClient
try: 
    q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
    if q.connect() != 0:
    	led_error( step=1 )
except:
    led_error( step=2 ) # check MQTT_SERVER 

try:
    from tsl2561 import TSL2561
    from bme280 import BME280, BMP280_I2CADDR
    from am2315 import AM2315
except:
	led_error( step=3 )

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )

# créer les senseurs
try:
    tsl = TSL2561( i2c=i2c )
    bmp = BME280( i2c=i2c, address=BMP280_I2CADDR )
    am = AM2315( i2c=i2c )
except:
	led_error( step=4 )

while runapp.value()==1:
    led.value( 1 ) # eteindre pendant envoi
    # tsl2561 - senseur lux
    lux = "{0:.2f}lx".format( tsl.read() )
    q.publish( "maison/exterieur/cabane/lux", lux )
    # bmp280 - senseur pression/température
    (t,p,h) = bmp.values # capturer les valeurs sous format texte
    q.publish( "maison/exterieur/cabane/pression", p )
    q.publish( "maison/exterieur/cabane/temperature", t )
    # am2315 - humidité/temperature
    am.measure() # reactive le senseur
    sleep( 1 )
    am.measure()
    t = "{0:.2f}C".format( am.temperature() )
    h = "{0:.2f}%Rh".format( am.humidity() )
    q.publish( "maison/exterieur/jardin/temperature", t )
    q.publish( "maison/exterieur/jardin/humidite", h )
    led.value( 0 ) # allumer

    # pause de x sec
    n = time() # now(). Temps en sec
    nhb = time() 
    while ( time()-n ) < SLEEP_TIME:
        # heartbeat 200ms / 10 sec
        if (time()-nhb) > 10:
        	led.value( 1 ) # eteindre
        	sleep( 0.2 )
        	led.value( 0 ) # allumer 
        	nhb = time()
        sleep( 0.300 )

led.value( 1 ) # eteindre
