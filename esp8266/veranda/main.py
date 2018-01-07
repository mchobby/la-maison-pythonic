# coding: utf8
""" La Maison Pythonic - Object Veranda v0.1 

	Envoi des données température et contact magnétic vers serveur MQTT
 """ 

from machine import Pin, I2C, reset
import time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = 'veranda'

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

# Contact
CONTACT_PIN = 13 # Signal du senseur PIR.
last_contact_state = 0 # 0=fermé, 1=ouvert

# Etat LDR
LDR_HYST  = 200  # Valeur d'hystersis (pour éviter la basculement continuel)
last_ldr_state = "NOIR" # Noir ou ECLAIRAGE

def ldr_to_state( adc_ldr, adc_pivot ):
	""" Transforme la valeur adc lue en NOIR et ECLAIRAGE """
	global last_ldr_state
	# print( "adc_ldr, adc_pivot = %s, %s" % (adc_ldr, adc_pivot) ) 
	LDR_HYST  = 200  # Valeur d'hystersis (pour éviter la basculement continuel)
	if adc_ldr > (adc_pivot+LDR_HYST):
		return "ECLAIRAGE"
	elif adc_ldr < (adc_pivot-LDR_HYST):
		return "NOIR"
	else:
		return last_ldr_state

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = Pin( 0, Pin.OUT )
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
	q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
	if q.connect() != 0:
		led_error( step=1 )
except Exception as e:
	print( e )
	led_error( step=2 ) # check MQTT_SERVER, MQTT_USE- MQTT_PSWD

# chargement des bibliotheques
try:
	from ads1x15 import *
	from machine import Pin
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )


# créer les senseurs
try:
	adc = ADS1115( i2c=i2c, address=0x48, gain=0 )

	contact = Pin( CONTACT_PIN, Pin.IN, Pin.PULL_UP )
	last_contact_state = contact.value()
	# lire la valeur de la LDR et déterminer le dernier etat connu
	last_ldr_state = ldr_to_state( 
		adc_ldr   = adc.read( rate=0, channel1=1),
		adc_pivot = adc.read( rate=0, channel1=2) )
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
	q.publish( "maison/rez/veranda/temp", t )

def check_contact():
	""" Publie un message chaque fois que le contact change d'état """
	global q
	global last_contact_state
	# si rien n'a changé
	if contact.value()==last_contact_state:
		return
	# état différent -> deparasitage logiciel
	time.sleep( 0.100 )
	# relire l'état et s'assurer qu'il n'a pas changé
	valeur = contact.value()  
	if valeur != last_contact_state:
		q.publish( "maison/rez/veranda/portefen", "OUVERT" if valeur==1 else "FERME" )
		last_contact_state = valeur

def check_ldr():
	global q
	global adc
	global last_ldr_state 
	ldr_state = ldr_to_state( 
		adc_ldr = adc.read( rate=0, channel1=1),
		adc_pivot = adc.read( rate=0, channel1=2) )
	if ldr_state != last_ldr_state:
		q.publish( "maison/rez/veranda/ldr", ldr_state )
		last_ldr_state = ldr_state

def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	# PS: LED déjà éteinte par run_every!
	time.sleep( 0.2 )


async def run_every( fn, min= 1, sec=None):
	""" Execute a function fn every min minutes or sec secondes"""
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
loop.create_task( run_every(capture_1h, min=60) )
loop.create_task( run_every(check_contact, sec=2 ) )
loop.create_task( run_every(check_ldr, sec=5) )
loop.create_task( run_every(heartbeat, sec=10) )
try:
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

loop.close()
led.value( 1 ) # eteindre 
print( "Fin!")
