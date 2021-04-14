# coding: utf8
""" La Maison Pythonic - Objet Environnemental

	Envoi des données sur la qualité de l'air vers serveur MQTT

 	v0.1 - Initial Writing (ESP32 ONLY)
 """

from machine import Pin, I2C, ADC, reset
import time
from ubinascii import hexlify
from network import WLAN
import os

CLIENT_ID = 'environ-0'

# Utiliser résolution DNS (serveur en ligne)
# MQTT_SERVER = 'test.mosquitto.org'
#
# Utiliser IP si le Pi en adresse fixe
# (plus fiable sur réseau local/domestique)
# MQTT_SERVER = '192.168.1.220'
#
# Utiliser le hostname si Pi en DHCP et que la propagation
# du # hostname atteind le modem/router (voir aussi
# gestion mDns sur router). # (pas forcement fiable sur
# réseau domestique)
# MQTT_SERVER = 'pythonic'
#
# Attention: MicroPython sous ESP8266 ne gère pas mDns!

MQTT_SERVER = "192.168.1.210"

# Mettre a None si pas utile
MQTT_USER = 'pusr103'
MQTT_PSWD = '21052017'

# redemarrage auto après erreur
ERROR_REBOOT_TIME = 3600 # 1 h = 3600 sec
# Capteur de température TMP36
A2 = 34 # A2 on ESP32
TMP36_PIN =  A2

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
	t = time.time()
	while ( time.time()-t ) < ERROR_REBOOT_TIME:
		for i in range( 20 ):
			led.value(not(led.value()))
			time.sleep(0.100)
		led.value( 1 ) # eteindre
		time.sleep( 1 )
		# clignote nbr fois
		for i in range( step ):
			led.value( 0 )
			time.sleep( 0.5 )
			led.value( 1 )
			time.sleep( 0.5 )
		time.sleep( 1 )
	# Re-start the ESP
	reset()

if runapp.value() != 1:
	from sys import exit
	exit(0)

led.value( 0 ) # allumer

# --- Programme Pincipal ---
from umqtt.simple import MQTTClient
try:
	if os.uname().nodename != 'esp32':
		raise Exception( "ESP32 only project (3.3V Analog required)")

	q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.set_last_will( topic="disconnect/%s" % CLIENT_ID , msg=sMac )

	if q.connect() != 0:
		led_error( step=1 )

except Exception as e:
	print( e )
	# check MQTT_SERVER, MQTT_USER, MQTT_PSWD
	led_error( step=2 )

# chargement des bibliotheques
try:
	from ccs811 import CCS811
	from machine import Pin
except Exception as e:
	print( e )
	led_error( step=3 )

# créer les capteurs
try:
	i2c = get_i2c()
	adc = ADC( Pin(TMP36_PIN) )
	adc.atten( ADC.ATTN_2_5DB ) # 1.5V max
	# Capteur temp CCS811
	ccs = CCS811( i2c )
	if ccs.check_error:
		raise Exception( "CCS811 ERROR_ID = %s" % ccs.error_id.as_text )
except Exception as e:
	print( e )
	led_error( step=4 )

try:
	# annonce connexion objet
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.publish( "connect/%s" % CLIENT_ID , sMac )
	# Annonce l'état
except Exception as e:
	print( e )
	led_error( step=5 )

import uasyncio as asyncio

def capture_5min():
	""" Executé pour capturer la temperature et CCS toutes les 5 min """
	global ccs
	global adc
	# Attendre capteur prêt
	while not ccs.data_ready:
		time.sleep( 0.100 )
	# transformer en chaine de caractères
	eco2 = "{0:d}".format(ccs.eco2) # PPM
	q.publish( "maison/rez/salle/eco2", eco2 )
	tvoc = "{0:d}".format(ccs.tvoc) # PPB
	q.publish( "maison/rez/salle/tvoc", tvoc )

	# temperature
	mv = (adc.read_u16() * 1.5 )/65.635
	temp = "{0:.2f}".format((mv-500)/10) # temp °C
	q.publish( "maison/rez/salle/temp", temp )


def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	# PS: LED déjà éteinte par run_every!
	time.sleep( 0.2 )


async def run_every( fn, min= 1, sec=None):
	""" Execute a function fn every min minutes
	    or sec secondes"""
	global led
	wait_sec = sec if sec else min*60
	while True:
		led.value( 1 ) # eteindre pendant envoi/traitement
		try:
			fn()
		except Exception:
			print( "run_every catch exception for %s" % fn)
			raise # quitter loop
		led.value( 0 ) # allumer
		await asyncio.sleep( wait_sec )

async def run_app_exit():
	""" fin d'execution lorsque quitte la fonction """
	global runapp
	while runapp.value()==1:
		await asyncio.sleep( 10 )
	return

loop = asyncio.get_event_loop()
loop.create_task( run_every(capture_5min  , min=5  ) )
loop.create_task( run_every(heartbeat     , sec=10 ) )
try:
	# Execution du scheduler
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

loop.close()
led.value( 1 ) # eteindre
print( "Fin!")
