# coding: utf8
""" La Maison Pythonic - Object Cabane2 v0.2

	Envoi des données toutes les heures + 20 minutes
	vers serveur MQTT

 	v0.1 - Initial Writing
 	v0.2 - minor fix, ESP32 support
 """

from machine import Pin, I2C, reset
from time import sleep, time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = 'cabane2'

# Utiliser résolution DNS (serveur en ligne)
# MQTT_SERVER = 'test.mosquitto.org'
#
# Utiliser IP si le Pi en adresse fixe
# (plus fiable sur réseau local/domestique)
# MQTT_SERVER = '192.168.1.220'
#
# Utiliser le hostname si Pi en DHCP et que la propagation
# du hostname atteind le modem/router (voir aussi gestion
# mDns sur router).
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
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.set_last_will( topic="disconnect/%s" % CLIENT_ID , msg=sMac )
	if q.connect() != 0:
		led_error( step=1 )
except Exception as e:
	print( e )
	# check MQTT_SERVER, MQTT_USER, MQTT_PSWD
	led_error( step=2 )

try:
	from tsl2591 import TSL2591
	from bme280 import BME280, BME280_I2CADDR
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = get_i2c()

# créer les capteurs
try:
	tsl = TSL2591( i2c=i2c )
	bme = BME280( i2c=i2c, address=BME280_I2CADDR )
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

import uasyncio as asyncio

def capture_1h():
	""" Executé pour capturer des donnees chaque heure """
	global q
	global tsl

	# tsl2561 - senseur lux
	lux = "{0:.2f}".format( tsl.lux )
	q.publish( "maison/exterieur/cabane/lux", lux )

def capture_20min():
	""" Executé pour capturer des donnees toutes les 20 mins """
	global q
	global bme
	# bme280 - capteur pression/température/humidité
	# capturer les valeurs sous format texte
	(t,p,h) = bme.raw_values
	# transformer en chaine de caractère
	t = "{0:.2f}".format(t)
	p = "{0:.2f}".format(p)
	h = "{0:.2f}".format(h)
	q.publish( "maison/exterieur/cabane/pathm", p )
	q.publish( "maison/exterieur/cabane/temp", t )
	q.publish( "maison/exterieur/cabane/hrel", h )

def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	sleep( 0.2 )

async def run_every( fn, min= 1, sec=None):
	""" Execute a function fn every min minutes or sec secondes"""
	global led
	wait_sec = sec if sec else min*60
	while True:
		# eteindre pendant envoi/traitement
		led.value( 1 )
		fn()
		led.value( 0 ) # allumer
		await asyncio.sleep( wait_sec )

async def run_app_exit():
	""" fin d'execution lorsque quitte la fonction """
	global runapp
	while runapp.value()==1:
		await asyncio.sleep( 10 )
	return

loop = asyncio.get_event_loop()
loop.create_task( run_every(capture_1h, min=60) )
loop.create_task( run_every(capture_20min, min=20) )
loop.create_task( run_every(heartbeat, sec=10) )
try:
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

loop.close()
led.value( 1 ) # eteindre
print( "Fin!")
