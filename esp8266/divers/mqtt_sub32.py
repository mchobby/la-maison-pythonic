""" La Maison Pythonic - souscription sur broker MQTT depuis ESP32 sous MicroPython.
    ACTIVE LA LED SUR LA BROCHE 13.

    Pour ESP8266 voir script mqtt_sub.py  """ 
import time
from network import WLAN
from machine import Pin
from umqtt.simple import MQTTClient
from ubinascii import hexlify
import sys

CLIENT_ID = "demo-sub"

MQTT_SERVER = "192.168.1.210"

# Mettre a None si pas utile
MQTT_USER = 'pusr103'
MQTT_PSWD = '21052017'

led = Pin( 13, Pin.OUT )
led.value( 0 ) # eteindre

def sub_cb( topic, msg ):
	""" fonction de rappel pour souscription MQTT """
	t = topic.decode('utf8')
	m = msg.decode('utf8')
	print( '-'*20 )
	print( 'topic: %s' % t )
	print( 'message: %s' % m )

	if t == 'cmd/led':
		print( "changement etat led")
		# LED en logique directe
		led.value( 1 if m=="on" else 0 )

print( "Creation MQTTClient")
q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
q.set_callback( sub_cb )

if q.connect() != 0:
	print( "erreur connexion" )
	sys.exit()
print( "Connecté" )

q.subscribe( 'demo/#' )
q.subscribe( 'cmd/led' )
print( "souscription OK" )

# annonce connexion objet
sMac = hexlify( WLAN().config( 'mac' ) ).decode()
q.publish( "connect/%s" % CLIENT_ID , sMac )

# Boucle de traitement
while True:
	# traitement message MQTT (BLOQUANT)
	q.wait_msg()

	# traitment message MQTT (NON BLOQUANT)
	# q.check_msg() 

q.disconnect()
