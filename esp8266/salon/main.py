# coding: utf8
""" La Maison Pythonic - Object Salon v0.1 

	Envoi des données température et senseur PIR vers serveur MQTT
 """ 

from machine import Pin, I2C, reset
from time import sleep, time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = 'salon'

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

# --- CHANGE FROM HERE --------------------------------
try:
	from ads1x15 import *
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )

# créer les senseurs
try:
	adc = ADS1115( i2c=i2c, address=0x48, gain=0 )
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
	global adc
	# tmp36 - senseur température
	valeur = adc.read( rate=0, channel1=0 )
	mvolts = valeur * 0.1875
	t = (mvolts - 500)/10
	t = "{0:.2f}".format(t)  # transformer en chaine de caractère
	q.publish( "maison/rez/salon/temp", t )


def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	sleep( 0.2 )

async def run_every( fn, min= 1, sec=None):
	""" Execute a function fn every min minutes or sec secondes"""
	global led
	wait_sec = sec if sec else min*60
	while True:
		led.value( 1 ) # eteindre pendant envoi/traitement
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
loop.create_task( run_every(heartbeat, sec=10) )
try:
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

loop.close()
led.value( 1 ) # eteindre 
print( "Fin!")
