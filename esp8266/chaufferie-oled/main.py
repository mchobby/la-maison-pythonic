# coding: utf8
""" La Maison Pythonic - Afficheur chauferie avec écran OLED v0.1

Permet d'envoyer des commandes à l'objet chaufferie et d'avoir des
informations sur l'état et le température.
 """

from machine import Pin, reset, Timer
import time
from ubinascii import hexlify
from network import WLAN


CLIENT_ID = 'chaufferie-oled'

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

# Topics et informations capturée
TOPIC_CHAUD = u"maison/cave/chaufferie/etat"
TOPIC_CMD   = u"maison/cave/chaufferie/cmd" # Commande vers la chaudière
TOPIC_TEMP_EAU = u"maison/cave/chaufferie/temp-eau"
chaud_etat = '?'
temp = '?'
operation = 'attente'

# Interface utilisateur
CHAUD_TOGGLE_PIN = 2   # BOUTON C - Broche commande MARCHE.
chaud_toggle = Pin( CHAUD_TOGGLE_PIN,  Pin.IN, Pin.PULL_UP ) # Call do_chaud_on()


def do_chaud_toggle( timer ):
	global operation
	global chaud_etat
	global q
	chaud_etat = 'MARCHE' if chaud_etat == 'ARRET' else 'ARRET'
	q.publish( TOPIC_CMD, chaud_etat )
	operation = '%s sent!' % chaud_etat
	update_lcd()

def debounce_chaud_toggle( pin ):
	# Démarrer ou remplacer le timer pour 200ms afin qu'il démarre le callback
	timer.init( mode=Timer.ONE_SHOT, period=200, callback=do_chaud_toggle )

# déclarer un nouveau Timer matériel
timer = Timer( 0 )

# Enregistrer le callback des boutons + deparasitage via Timer
chaud_toggle.irq( debounce_chaud_toggle, Pin.IRQ_RISING )

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = Pin( 0, Pin.OUT )
led.value( 1 ) # eteindre

# chargement des bibliotheques
try:
	from ssd1306 import SSD1306_I2C
	from machine import Pin, I2C
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c (if any)
#
i2c = I2C( sda=Pin(4), scl=Pin(5) )
# OLED
lcd = SSD1306_I2C( 128, 32, i2c )
lcd.fill(1) # Rempli l'écran en blanc
lcd.text( 'STARTING...', 15, 15, 0 )
lcd.show()  # Afficher!

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
	lcd.fill(0) # Rempli l'écran en noir
	lcd.text( 'RunApp = STOP', 15, 15, 1 )
	lcd.show()  # Afficher!
	from sys import exit
	exit(0)

led.value( 0 ) # allumer

# --- Programme Pincipal ---
def sub_cb( topic, msg ):
	""" fonction de rappel pour souscriptions MQTT """
	global chaud_etat
	global temp
	global operation

	# debogage
	# print( '-'*20 )
	# print( topic )
	# print( msg )

	# bytes -> str
	t = topic.decode( 'utf8' )
	m = msg.decode('utf8')
	try:
		if t == TOPIC_CHAUD:
			chaud_etat = m
		elif t == TOPIC_TEMP_EAU:
			temp = m

		operation = ''
		update_lcd() # Faire m-à-j écran
	except Exception as e:
		# Capturer TOUTE exception sur souscription
		# Ne pas crasher check_mqtt_sub et asyncio.run_until_complete et l'ESP!

		# Info debug sur REPL
		print( "="*20 )
		print( "Subscriber callback (sub_cb) catch an exception:" )
		print( e )
		print( "for topic and message" )
		print( t )
		print( m )
		print( "="*20 )

from umqtt.simple import MQTTClient
try:
	q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
	q.set_callback( sub_cb )
	if q.connect() != 0:
		led_error( step=1 )
	q.subscribe( TOPIC_CHAUD )
	q.subscribe( TOPIC_TEMP_EAU )
except Exception as e:
	print( e )
	led_error( step=2 ) # check MQTT_SERVER, MQTT_USE- MQTT_PSWD


# créer les senseurs
try:
	pass
except Exception as e:
	print( e )
	led_error( step=4 )

def update_lcd( ):
	""" Affiche les informations à l'écran. """
	global chaud_etat
	global temp
	global operation

	global lcd
	lcd.fill( 0 ) # Remplir en noir
	lcd.text( 'T %sC' % temp, 0,6, 1 )
	lcd.text( operation, 0, 24, 1)

	if chaud_etat == 'MARCHE':
		lcd.fill_rect( 70,0, 58,20, 1 )
		lcd.text( chaud_etat, 74, 6, 0)
	else:
		lcd.rect( 70,0, 58,20, 1 )
		lcd.text( chaud_etat, 74, 6, 1)
	lcd.show()

try:
	# annonce connexion objet
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.publish( "connect/%s" % CLIENT_ID , sMac )
	# Annonce l'état
	operation = 'Waiting data...'
	update_lcd()
except Exception as e:
	print( e )
	led_error( step=5 )

import uasyncio as asyncio

def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	# PS: LED déjà éteinte par run_every!
	time.sleep( 0.2 )

def check_mqtt_sub():
	""" Process the MQTT Subscription messages """
	global q
	# Non-Blocking wait_msg(). Will call mqtt callback (sub_cb)
	# when a message is received for subscription
	q.check_msg() # get one message (if any)

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
loop.create_task( run_every(heartbeat     , sec=10 ) )
loop.create_task( run_every(check_mqtt_sub, sec=2.5) )
try:
	# Execution du scheduler
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

loop.close()
led.value( 1 ) # eteindre
print( "Fin!")
