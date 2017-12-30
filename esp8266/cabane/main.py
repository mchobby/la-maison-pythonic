# coding: utf8
""" La Maison Pythonic - Object Cabane v0.1 

    Envoi des données toutes les 5 minutes vers serveur MQTT
 """ 

from machine import Pin, I2C, reset
from time import sleep, time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = 'cabane'

# Utiliser résolution DNS (serveur en ligne) 
# MQTT_SERVER = 'test.mosquitto.org'
#
# Utiliser IP si le Pi en adresse fixe 
# (plus fiable sur réseau local/domestique)
# MQTT_SERVER = '192.168.1.220'
#
# Utiliser le hostname si Pi en DHCP et que la propagation du
# hostname atteind le modem/router (voir aussi gestion mDns sur router).
# (pas forcement fiable sur réseau domestique)
# MQTT_SERVER = 'pythonic'
#
# Attention: MicroPython sous ESP8266 ne gère pas mDns!

MQTT_SERVER = "192.168.1.210"

# Mettre a None si pas utile
MQTT_USER = 'pusr103'
MQTT_PSWD = '21052017'

# redemarrage auto après erreur 
ERROR_REBOOT_TIME = 3600 # 1 h = 3600 sec

# temps pause entre 2 mesures
SLEEP_TIME = 60*5  # 5 minutes = 300 secondes

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = Pin( 0, Pin.OUT )
led.value( 1 ) # eteindre

def led_error( step ):
	global led
	t = time()
	while ( time()-t ) < ERROR_REBOOT_TIME:
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
	# Re-start the ESP
	reset()



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
except Exception as e:
	print( e )
	led_error( step=2 ) # check MQTT_SERVER, MQTT_USE- MQTT_PSWD

try:
	from tsl2561 import TSL2561
	from bme280 import BME280, BMP280_I2CADDR
	from am2315 import AM2315
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )

# créer les senseurs
try:
	tsl = TSL2561( i2c=i2c )
	bmp = BME280( i2c=i2c, address=BMP280_I2CADDR )
	am = AM2315( i2c=i2c )
except Exception as e:
	print( e )
	led_error( step=4 )

try:
	# annonce connexion objet
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.publish( "connect/%s" % CLIENT_ID , sMac )
except Exception as e:
	print( e )
	led_error( step=5 )

try:
	while runapp.value()==1:
		led.value( 1 ) # eteindre pendant envoi
		# tsl2561 - senseur lux
		lux = "{0:.2f}".format( tsl.read() )
		q.publish( "maison/exterieur/cabane/lux", lux ) 
		# bmp280 - senseur pression/température
		(t,p,h) = bmp.raw_values # capturer les valeurs sous format texte
		t = "{0:.2f}".format(t)  # transformer en chaine de caractère
		p = "{0:.2f}".format(p)
		q.publish( "maison/exterieur/cabane/pathm", p )
		q.publish( "maison/exterieur/cabane/temp", t )
		# am2315 - humidité/temperature
		am.measure() # reactive le senseur
		sleep( 1 )
		am.measure()
		t = "{0:.2f}".format( am.temperature() )
		h = "{0:.2f}".format( am.humidity() )
		q.publish( "maison/exterieur/jardin/temp", t )
		q.publish( "maison/exterieur/jardin/hrel", h )
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
except Exception as e:
	print( e )
	led_error( step=6 )
