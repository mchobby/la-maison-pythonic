# coding: utf8
""" La Maison Pythonic - Object Cabane v0.2

    Envoi des données toutes les 5 minutes vers serveur MQTT

	v0.1 - initial Writing
	v0.2 - remove AM2315 (too sensitive)
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

# --- Abstraction ESP32 et ESP8266 ---
class LED:
	""" Abstraction LED Utilisateur pour ESP32 et ESP8266 """
	# User LED set ESP32 is on #13 with direct logic,
	# ESP8266 on pin #0 with reverse Logic

	# Comme le code initial était développé en logique inverse sur ESP8266
	# il faut réinverser la logique pour être compatible avec ESP32
	def __init__( self ):
		import os
		if os.uname().nodename == 'esp32':
			self._led = Pin( 13, Pin.OUT )
			self._reverse = True # LED in direct logic
		else:
			self._led = Pin( 0, Pin.OUT )
			self._reverse = False # LED in reverse logic

	def value( self, value=None ):
		""" contrôle the LED state """
		if value == None:
			# lire l'état de la LED
			if self._reverse:
				return not( self._led.value() )
			else:
				return self._led.value()
		else:
			# Modifier l'état de la LED
			if self._reverse:
				value = not( value )
			self._led.value( value )

def get_i2c():
	""" Abstraction du bus I2C pour ESP32 et ESP8266 """
	import os
	if os.uname().nodename == 'esp32':
		return I2C( sda=Pin(23), scl=Pin(22) )
	else:
		return I2C( sda=Pin(4), scl=Pin(5) )

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = LED()
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
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = get_i2c()

# créer les senseurs
try:
	tsl = TSL2561( i2c=i2c )
	bmp = BME280( i2c=i2c, address=BMP280_I2CADDR )
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
